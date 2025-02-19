from django.db import models
from django.utils.timezone import now

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
