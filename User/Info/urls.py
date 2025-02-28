# urls.py
from django.urls import path
from . import views
from .views import upload_image, verify_ocr, generate_qr_code, qr_display
 
urlpatterns = [
    path('', views.student_form, name='student_form'),
    path('generate_qr_code/<int:student_id>/', generate_qr_code, name='generate_qr_code'),  # QR code generation
    path('upload-image/',upload_image ),
    path('verify-ocr/', verify_ocr, name='verify_ocr'),
    path('qr_display/', qr_display, name='qr_display'),


    
]