from django.db import models
from django.utils.timezone import now, timedelta
from django.contrib.auth.models import AbstractUser
# import random
# import uuid
class User(AbstractUser):
    pass

class Student(models.Model):
    name = models.CharField(max_length=100)
    event_choices = [
        ('industry', 'Industry Visit'),
        ('academic', 'Academic Visit'),
    ]
    event = models.CharField(max_length=20, choices=event_choices)
    visitor_choices = [
        ('student', 'Student'),
        ('faculty', 'Faculty'),
    ]
    visitor_type = models.CharField(max_length=20, choices=visitor_choices)
    phone_number = models.CharField(max_length=15)
    college_name = models.CharField(max_length=100)
    UID = models.CharField(max_length=15)

    college_id_card = models.ImageField(upload_to='college_id_cards/')
    registration_time = models.DateTimeField(default=now)  # New field added

    def __str__(self):
        return f"{self.name} - {self.registration_time.strftime('%Y-%m-%d %H:%M:%S')}"
    
class StudentDetails(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='details')
    detail_timestamp = models.DateTimeField(default=now)
    additional_info = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Details for {self.student.name} at {self.detail_timestamp.strftime('%Y-%m-%d %H:%M:%S')}" 
    
# class OTP(models.Model):
#     student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="otps")
#     otp_code = models.CharField(max_length=6)  # Stores the 6-digit OTP
#     created_at = models.DateTimeField(default=now)  # Timestamp when OTP is created
#     expires_at = models.DateTimeField(default=lambda: now() + timedelta(minutes=5))  # OTP expires in 5 minutes
#     is_verified = models.BooleanField(default=False)  # Tracks whether OTP is used

#     def __str__(self):
#         return f"OTP for {self.student.name} - {self.otp_code} (Expires: {self.expires_at.strftime('%H:%M:%S')})"

#     def is_expired(self):
#         """Check if OTP is expired"""
#         return now() > self.expires_at

#     @classmethod
#     def generate_otp(cls, student):
#         """Generate a new OTP for a student"""
#         otp = str(random.randint(100000, 999999))  
#         otp_entry = cls.objects.create(student=student, otp_code=otp)
#         return otp_entry       
