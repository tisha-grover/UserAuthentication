from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils.timezone import now
import qrcode
from io import BytesIO
from .models import Student
from .forms import RegistrationForm, IdUploadForm
from .ocr_api import extract_text_from_api, verify_ocr_data
from .utils import process_extracted_text
import pytesseract
from PIL import Image
import cv2
from django.conf import settings
import numpy as np
import re
import os
from fuzzywuzzy import fuzz
from django.core.files.base import ContentFile

# import requests

def preprocess_image(image_path):
    """Convert image to grayscale and apply adaptive thresholding."""
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    _, thresh = cv2.threshold(image, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return Image.fromarray(thresh)

def extract_field(ocr_text, pattern):
    """Extracts a specific field using regex."""
    match = re.search(pattern, ocr_text, re.IGNORECASE)
    return match.group(1).strip() if match else None

def normalize_text(text):
    """Normalize text by removing special characters and converting to lowercase."""
    return re.sub(r'[^a-zA-Z0-9\s]', '', text).strip().lower() if text else ""

def verify_ocr(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get("college_id_card")
        form_name = request.POST.get("name")
        form_event = request.POST.get("event")
        visitor_type = request.POST.get("visitor_type")
        phone_number = request.POST.get("phone_number")
        form_college = request.POST.get("college_name")
        form_uid = request.POST.get("UID")
        visit_date = request.POST.get("visit_date")

        print(form_name, form_college, form_uid, visit_date, phone_number, visitor_type, form_event)

        if not uploaded_file:
            return JsonResponse({"success": False, "error": "No image uploaded."})

        # Save uploaded image temporarily
        temp_dir = "/tmp"
        os.makedirs(temp_dir, exist_ok=True)
        image_path = os.path.join(temp_dir, uploaded_file.name)

        with open(image_path, "wb") as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)

        # Preprocess Image for better OCR
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        # OCR Processing
        extracted_text = pytesseract.image_to_string(thresh)
        print("🔍 Raw OCR Output:\n", extracted_text)

        # Improved Regex-based Field Extraction
        extracted_name = extract_field(extracted_text, r"(?i)Name\s*[:\-]?\s*([A-Za-z\s]+)")
        extracted_college = extract_field(extracted_text, r"(?i)(Chitkara\s+University|[\w\s]+University)")
        extracted_uid = extract_field(extracted_text, r"(?i)(\d{10,})")  # Extracts 10+ digit numbers

        # Normalize extracted and form data
        extracted_name = normalize_text(extracted_name) if extracted_name else ""
        extracted_college = normalize_text(extracted_college) if extracted_college else ""
        extracted_uid = normalize_text(extracted_uid) if extracted_uid else ""

        form_name = normalize_text(form_name)
        form_college = normalize_text(form_college)
        form_uid = normalize_text(form_uid)

        # Debugging: Print extracted vs. form data
        print(f"📌 Extracted Name: {extracted_name} | Form Name: {form_name}")
        print(f"📌 Extracted College: {extracted_college} | Form College: {form_college}")
        print(f"📌 Extracted UID: {extracted_uid} | Form UID: {form_uid}")

        # Fuzzy matching with threshold adjustment
        name_match = fuzz.partial_ratio(form_name, extracted_name) > 65
        college_match = fuzz.partial_ratio(form_college, extracted_college) > 65
        uid_match = form_uid == extracted_uid  # UID should be exact

        errors = []
        if not name_match:
            errors.append("Name does not match.")
        if not college_match:
            errors.append("College name does not match.")
        if not uid_match:
            errors.append("UID does not match.")

        if errors:
            return JsonResponse({"success": False, "error": " | ".join(errors)})

        # ✅ Save Student Data if OCR verification is successful
        student, created = Student.objects.update_or_create(
            phone_number=phone_number,
            defaults={
                "name": form_name,
                "event": form_event,
                "visitor_type": visitor_type,
                "college_name": form_college,
                "UID": form_uid,
                "registration_time": visit_date,
                # "college_id_card": uploaded_file,  # Save the uploaded image
            }
        )
        if created:
            return generate_qr_code(request,student.UID)  # Generate QR code for the new student
        
        return JsonResponse({"success": True, "message": "Student data stored successfully!", "student_id": student.id})

    return JsonResponse({"success": False, "error": "Invalid request."})

def student_form(request):
    extracted_data = None
    error_message = None  

    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form_data = {
                "name": form.cleaned_data['name'],
                "college_name": form.cleaned_data['college_name'],
                "UID": form.cleaned_data['UID'],
            }
            print(form_data)

            college_id_card = request.FILES.get('college_id_card')

            if college_id_card:
                try:
                    extracted_text = extract_text_from_api(college_id_card)
                    extracted_data = process_extracted_text(extracted_text)

                    verification_result = verify_ocr_data(extracted_text, form_data)

                    if "✅" not in verification_result:
                        return render(request, 'student_form.html', {
                            'form': form,
                            'error_message': verification_result,
                            'processed_data': extracted_data
                        })

                except Exception as e:
                    print("In error")
                    messages.error(request, f"OCR Error: {str(e)}")
                    return render(request, 'student_form.html', {'form': form, 'error_message': "OCR failed"})

            # Save Student Data
            student, created = Student.objects.update_or_create(
                phone_number=form.cleaned_data['phone_number'],
                defaults={
                    "name": form.cleaned_data['name'],
                    "event": form.cleaned_data['event'],
                    "visitor_type": form.cleaned_data['visitor_type'],
                    "college_name": form.cleaned_data['college_name'],
                    "UID": form.cleaned_data['UID'],
                    "college_id_card": college_id_card,
                    "registration_time": now()
                }
            )

            messages.success(request, 'Student registered successfully!')
            generate_qr_code(request,student.id)
            # Redirect to QR display page after saving
            return redirect('qr_display', student_id=student.id)


    else:
        form = RegistrationForm()

    return render(request, 'student_form.html', {
        'form': form,
        'processed_data': extracted_data,
        'error_message': error_message
    })


def upload_image(request):
    from .ocr_api import extract_text_from_api
    from .utils import process_extracted_text  

    if request.method == 'POST':
        form = IdUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_image = form.cleaned_data['image']
            extracted_text = extract_text_from_api(uploaded_image)
            processed_data = process_extracted_text(extracted_text)

            return render(request, 'upload_success.html', {
                'image': uploaded_image,
                'text': extracted_text,
                'processed_data': processed_data
            })

def generate_qr_code(request, student_id):
    student = get_object_or_404(Student, UID=student_id)
    print("✅ Generating QR for:", student.name)  # Debugging

    qr = qrcode.make(f"Student ID: {student.UID}, Name: {student.name}")
    buffer = BytesIO()
    qr.save(buffer, format="PNG")

    student.qr_code.save(f"qr_{student.UID}.png", ContentFile(buffer.getvalue()), save=True)
    print("✅ QR Code saved!")
    
    
    return qr_display(request,student.UID)



def qr_display(request, student_id):
    student = get_object_or_404(Student, UID=student_id)
    qr_code=student.qr_code
    name=student.name
    context = {
        'image_url': qr_code.url,
        'name': name
    }
    print(context)
    return render(request, 'qr_display.html', context)
