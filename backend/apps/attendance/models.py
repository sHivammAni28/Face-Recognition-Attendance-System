from django.db import models
from django.utils import timezone
from apps.students.models import Student
from apps.authentication.models import User


class Attendance(models.Model):
    """Attendance model with unique constraints"""
    
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('late', 'Late'),
        ('absent', 'Absent'),
    ]
    
    SESSION_CHOICES = [
        ('daily', 'Daily'),
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
        ('evening', 'Evening'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(default=timezone.now)
    time = models.TimeField(auto_now_add=True)
    session = models.CharField(max_length=10, choices=SESSION_CHOICES, default='daily')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present')
    marked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_manual = models.BooleanField(default=False)  # True if marked manually by admin
    is_face_recognition = models.BooleanField(default=False)  # True if marked via face recognition
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student', 'date', 'session']
        ordering = ['-date', '-time']
    
    def __str__(self):
        return f"{self.student.roll_number} - {self.date} ({self.session}) - {self.status}"
    
    @property
    def student_name(self):
        return self.student.full_name
    
    @property
    def student_roll(self):
        return self.student.roll_number


class AttendanceSession(models.Model):
    """Model to define attendance sessions and their time limits"""
    
    name = models.CharField(max_length=20, choices=Attendance.SESSION_CHOICES, unique=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    late_threshold = models.TimeField()  # Time after which attendance is marked as late
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} ({self.start_time} - {self.end_time})"
    
    def is_current_session(self):
        """Check if current time falls within this session"""
        now = timezone.now().time()
        return self.start_time <= now <= self.end_time
    
    def is_late(self, current_time=None):
        """Check if current time is past the late threshold"""
        if current_time is None:
            current_time = timezone.now().time()
        return current_time > self.late_threshold


class AuditLog(models.Model):
    """Audit log for attendance actions"""
    
    ACTION_CHOICES = [
        ('mark', 'Mark Attendance'),
        ('update', 'Update Attendance'),
        ('delete', 'Delete Attendance'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE, null=True, blank=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    details = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.student.roll_number} - {self.timestamp}"