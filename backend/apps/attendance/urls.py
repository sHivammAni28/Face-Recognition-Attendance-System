from django.urls import path
from . import views
from . import debug_views

urlpatterns = [
    # Attendance marking
    path('mark/face/', views.mark_attendance_face, name='mark_attendance_face'),
    path('mark/face/debug/', debug_views.debug_mark_attendance_face, name='debug_mark_attendance_face'),
    path('mark/self/', views.mark_attendance_self, name='mark_attendance_self'),
    path('mark/manual/', views.mark_attendance_manual, name='mark_attendance_manual'),
    
    # Student attendance views
    path('my-attendance/', views.get_my_attendance, name='my_attendance'),
    path('my-stats/', views.get_my_attendance_stats, name='my_attendance_stats'),
    path('check-status/', views.check_attendance_status, name='check_attendance_status'),
    
    # Admin attendance views
    path('all/', views.get_all_attendance, name='all_attendance'),
    path('analytics/', views.get_attendance_analytics, name='attendance_analytics'),
    path('export/csv/', views.export_attendance_csv, name='export_attendance_csv'),
    
    # Attendance management
    path('<int:attendance_id>/update/', views.update_attendance, name='update_attendance'),
    path('<int:attendance_id>/delete/', views.delete_attendance, name='delete_attendance'),
    
    # Audit logs
    path('audit-logs/', views.get_audit_logs, name='audit_logs'),
    
    # Session management
    path('sessions/', views.attendance_sessions, name='attendance_sessions'),
]