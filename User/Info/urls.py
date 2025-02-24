# urls.py
from django.urls import path
from . import views
from .views import upload_image, verify_ocr, generate_qr_code


urlpatterns = [
    path('', views.student_form, name='student_form'),
    # path('student_list/', views.student_list, name='student_list'),  # List of students
    # path('student_detail/<int:student_id>/', views.student_detail, name='student_detail'),  # Student details page
    path('generate_qr_code/<int:student_id>/', views.generate_qr_code, name='generate_qr_code'),  # QR code generation
    # path('send-otp/<int:student_id>/', send_otp, name='send_otp'),
    # path('verify-otp/<int:student_id>/', verify_otp, name='verify_otp'),
    path('upload-image/',upload_image ),
    path('verify-ocr/', verify_ocr, name='verify_ocr'),
]