# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Student
from django.utils.timezone import now
import qrcode
from io import BytesIO
from django.http import HttpResponse

# Register a new student
def student_form(request):
    if request.method == 'POST':
        name = request.POST['name']
        event = request.POST['event']
        visitor_type = request.POST['visitor_type']
        phone_number = request.POST['phone_number']
        college_name = request.POST['college_name']
        UID = request.POST['UID']
        college_id_card = request.FILES['college_id_card']
        registration_time = now()

        student = Student.objects.create(
            name=name,
            event=event,
            visitor_type=visitor_type,
            phone_number=phone_number,
            college_name=college_name,
            UID=UID,
            college_id_card=college_id_card,
            registration_time=registration_time
        )
        student.save()
        messages.success(request, f'Student registered successfully on {registration_time.strftime("%Y-%m-%d %H:%M:%S")}')
        
        # After saving, generate QR code and redirect to the QR code page
        return redirect('generate_qr_code', student_id=student.id)

    return render(request, 'student_form.html')

# Generate a QR code for a student
def generate_qr_code(request, student_id):
    student = Student.objects.get(id=student_id)
    
    # Create a string containing student details to be encoded into the QR code
    qr_data = f"Name: {student.name}\nEvent: {student.event}\nVisitor Type: {student.visitor_type}\nPhone: {student.phone_number}\nCollege: {student.college_name}\nUID: {student.UID}"
    
    # Generate the QR code
    qr = qrcode.make(qr_data)
    
    # Save the QR code to a BytesIO object
    qr_image = BytesIO()
    qr.save(qr_image, 'PNG')
    qr_image.seek(0)
    
    # Serve the image as a response
    return HttpResponse(qr_image, content_type="image/png")

# Display the list of all students
def student_list(request):
    students = Student.objects.all()  # Get all students from the database
    return render(request, 'student_list.html', {'students': students})

# View details of a specific student
def student_detail(request, student_id):
    student = Student.objects.get(id=student_id)
    return render(request, 'student_detail.html', {'student': student})