from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.timezone import now
import qrcode
from io import BytesIO
from django.http import HttpResponse, JsonResponse
from .models import Student
from .forms import RegistrationForm, IdUploadForm
from .models import User
from .ocr_api import extract_text_from_api  # Ensure this function exists
from .utils import process_extracted_text  # Ensure this function exists
from django.utils import timezone


# ✅ Student Registration View with OCR Processing
def student_form(request):
    extracted_data = None
    error_message = None  

    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)

        if form.is_valid():
            # 📌 Extract Form Data
            name = form.cleaned_data['name']
            event = form.cleaned_data['event']
            visitor_type = form.cleaned_data['visitor_type']
            phone_number = form.cleaned_data['phone_number']
            college_name = form.cleaned_data['college_name']
            UID = form.cleaned_data['UID']
            college_id_card = request.FILES.get('college_id_card')
            registration_time = now()

            # ✅ OCR Image Processing
            if college_id_card:
                try:
                    extracted_text = extract_text_from_api(college_id_card)  
                    extracted_data = process_extracted_text(extracted_text)  

                    # 🔍 Validate OCR Data
                    extracted_college = extracted_data.get("college", "").strip().lower()
                    extracted_uid = extracted_data.get("UID", "").strip()

                    if not extracted_college or not extracted_uid:
                        error_message = "OCR extraction failed. College/UID not found."
                        return render(request, 'student_form.html', {
                            'form': form,
                            'error_message': error_message,
                            'processed_data': extracted_data
                        })

                    # 🔥 Mismatch Check
                    if college_name.strip().lower() != extracted_college:
                        error_message = f"College name mismatch: {college_name} vs. {extracted_college}"
                    if UID.strip() != extracted_uid:
                        error_message = f"UID mismatch: {UID} vs. {extracted_uid}"

                    if error_message:
                        return render(request, 'student_form.html', {
                            'form': form,
                            'error_message': error_message,
                            'processed_data': extracted_data
                        })

                except Exception as e:
                    messages.error(request, f"OCR Error: {str(e)}")
                    return render(request, 'student_form.html', {'form': form, 'error_message': "OCR failed"})

            # ✅ Save or Update Student
            student, created = Student.objects.update_or_create(
                phone_number=phone_number,
                defaults={
                    "name": name,
                    "event": event,
                    "visitor_type": visitor_type,
                    "college_name": college_name,
                    "UID": UID,
                    "college_id_card": college_id_card,
                    "registration_time": registration_time
                }
            )

            # ✅ Redirect to QR Code Generation
            messages.success(request, f'Student registered successfully!')
            return redirect('generate_qr_code', student_id=student.id)

    else:
        form = RegistrationForm()

    return render(request, 'student_form.html', {
        'form': form,
        'processed_data': extracted_data,
        'error_message': error_message
    })


# ✅ Generate QR Code
def generate_qr_code(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    qr_data = f"Name: {student.name}\nEvent: {student.event}\nVisitor Type: {student.visitor_type}\nPhone: {student.phone_number}\nCollege: {student.college_name}\nUID: {student.UID}"
    qr = qrcode.make(qr_data)

    qr_image = BytesIO()
    qr.save(qr_image, 'PNG')
    qr_image.seek(0)

    return HttpResponse(qr_image, content_type="image/png")


# ✅ Verify OCR Details
def verify_ocr(request):
    if request.method == 'POST' and request.FILES.get('college_id_card'):
        try:
            image = request.FILES['college_id_card']
            extracted_text = extract_text_from_api(image)
            extracted_data = process_extracted_text(extracted_text)

            # ✅ Ensure extracted_data contains valid values
            extracted_college = extracted_data.get("college", "")
            extracted_uid = extracted_data.get("UID", "")

            # ✅ Handle None values safely before calling `.strip()`
            extracted_college = extracted_college.strip().lower() if extracted_college else ""
            extracted_uid = extracted_uid.strip() if extracted_uid else ""

            if extracted_college and extracted_uid:
                return JsonResponse({"success": True, "data": extracted_data})
            else:
                return JsonResponse({"success": False, "error": "OCR extraction incomplete. Please try again."})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request. Please upload an ID card."})



# ✅ Upload Image View (Restored)
def upload_image(request):
    if request.method == 'POST':
        form = IdUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_image = form.cleaned_data['college_id_card']

            # 🔥 Process OCR Here
            extracted_text = extract_text_from_api(uploaded_image)
            processed_data = process_extracted_text(extracted_text)

            return render(request, 'upload_success.html', {
                'image': uploaded_image,
                'text': extracted_text,
                'processed_data': processed_data
            })
    else:
        form = IdUploadForm()

    return render(request, 'upload_image.html', {'form': form})
