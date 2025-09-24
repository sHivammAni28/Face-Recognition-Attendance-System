from django.contrib import admin
from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('roll_number', 'full_name', 'email', 'student_class', 'is_face_registered', 'created_at')
    list_filter = ('student_class', 'is_face_registered', 'created_at')
    search_fields = ('roll_number', 'user__first_name', 'user__last_name', 'user__email')
    ordering = ('roll_number',)
    readonly_fields = ('created_at', 'updated_at', 'face_encoding')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Student Details', {
            'fields': ('roll_number', 'student_class', 'phone_number', 'address')
        }),
        ('Face Recognition', {
            'fields': ('face_image_data', 'is_face_registered', 'face_encoding')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )