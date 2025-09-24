from django.contrib import admin
from .models import Attendance, AttendanceSession, AuditLog


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student_roll', 'student_name', 'date', 'time', 'session', 'status', 'is_manual', 'marked_by')
    list_filter = ('date', 'session', 'status', 'is_manual', 'student__student_class')
    search_fields = ('student__roll_number', 'student__user__first_name', 'student__user__last_name')
    ordering = ('-date', '-time')
    date_hierarchy = 'date'
    
    def student_roll(self, obj):
        return obj.student.roll_number
    student_roll.short_description = 'Roll Number'
    
    def student_name(self, obj):
        return obj.student.full_name
    student_name.short_description = 'Student Name'


@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_time', 'end_time', 'late_threshold', 'is_active')
    list_filter = ('is_active',)
    ordering = ('start_time',)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'student', 'timestamp', 'ip_address')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__username', 'student__roll_number', 'student__user__first_name')
    ordering = ('-timestamp',)
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'