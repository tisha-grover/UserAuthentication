from django.contrib import admin
from .models import User, Student, StudentDetails

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_active')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'event', 'visitor_type', 'phone_number', 'college_name', 'UID', 'registration_time')
    search_fields = ('name', 'college_name', 'UID')
    list_filter = ('event', 'visitor_type')

@admin.register(StudentDetails)
class StudentDetailsAdmin(admin.ModelAdmin):
    list_display = ('student', 'additional_info')
    search_fields = ('student__name',)

