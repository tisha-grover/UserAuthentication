# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.student_form, name='student_form'),
    path('student_list/', views.student_list, name='student_list'),  # List of students
    path('student_detail/<int:student_id>/', views.student_detail, name='student_detail'),  # Student details page
    path('generate_qr_code/<int:student_id>/', views.generate_qr_code, name='generate_qr_code'),  # QR code generation
]