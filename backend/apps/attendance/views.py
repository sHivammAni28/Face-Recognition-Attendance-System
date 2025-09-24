from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q, Count
from django.http import HttpResponse
import logging

logger = logging.getLogger(__name__)
from .models import Attendance, AttendanceSession, AuditLog
from .serializers import (
    AttendanceSerializer, FaceRecognitionAttendanceSerializer,
    ManualAttendanceSerializer, AttendanceStatsSerializer,
    AttendanceSessionSerializer, AuditLogSerializer
)
from .face_detection_simple import detect_face_in_image
from apps.students.models import Student
import csv
import json
from datetime import datetime, timedelta


class IsAdminUser(permissions.BasePermission):
    """Custom permission to only allow admin users"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def create_audit_log(user, action, student, attendance=None, details="", request=None):
    """Create audit log entry"""
    ip_address = get_client_ip(request) if request else None
    AuditLog.objects.create(
        user=user,
        action=action,
        attendance=attendance,
        student=student,
        details=details,
        ip_address=ip_address
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_attendance_face(request):
    """Mark attendance using face recognition (DeepFace)"""
    if not request.user.is_student:
        return Response({'error': 'Only students can mark attendance via face recognition'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        return Response({'error': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if student has registered face
    if not student.is_face_registered:
        return Response({
            'error': 'Face not registered. Please register your face first.',
            'face_registration_required': True
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if attendance already marked for today
    today = timezone.now().date()
    session = request.data.get('session', 'daily')
    
    existing_attendance = Attendance.objects.filter(
        student=student,
        date=today,
        session=session
    ).first()
    
    if existing_attendance:
        return Response({
            'error': 'Attendance already marked for today!'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Get face image data
    face_image_data = request.data.get('face_image_data')
    if not face_image_data:
        return Response({
            'error': 'No face image provided'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    confidence = 0.0
    
    try:
        # Try DeepFace recognition first
        try:
            from .deepface_utils import (
                generate_face_embedding, 
                verify_face_match
            )
            
            logger.info(f"Processing face recognition for student {student.roll_number}")
            
            # Generate embedding for the captured image
            success, message, face_embedding = generate_face_embedding(face_image_data)
            
            if not success or face_embedding is None:
                raise Exception(f'Face processing failed: {message}')
            
            # Get student's stored embedding
            stored_embedding = student.get_face_encoding()
            if stored_embedding is None:
                raise Exception('No stored face encoding found for student')
            
            # Verify face match
            is_match, confidence = verify_face_match(stored_embedding, face_embedding)
            
            if not is_match:
                return Response({
                    'error': f'Face verification failed. Confidence: {confidence:.2f}',
                    'matched_student_id': None,
                    'confidence_score': confidence,
                    'status': 'face_not_matched'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            logger.info(f"Face verified successfully for student {student.roll_number} with confidence {confidence:.2f}")
            
        except ImportError:
            logger.error("DeepFace not available - this should not happen as DeepFace is installed")
            raise Exception('DeepFace import failed - please check installation')
        
        # Determine if attendance is late
        current_time = timezone.now().time()
        final_status = 'present'
        
        # Simple late logic - after 9 AM is considered late
        if current_time.hour >= 9:
            final_status = 'late'
        
        # Create attendance record
        attendance = Attendance.objects.create(
            student=student,
            session=session,
            status=final_status,
            is_face_recognition=True,
            marked_by=request.user
        )
        
        # Create audit log
        create_audit_log(
            user=request.user,
            action='mark',
            student=student,
            attendance=attendance,
            details=f"Face recognition attendance - {final_status} (confidence: {confidence:.2f})",
            request=request
        )
        
        return Response({
            'message': f'Attendance marked successfully as {final_status}',
            'attendance': AttendanceSerializer(attendance).data,
            'matched_student_id': student.id,
            'confidence_score': confidence,
            'status': 'success'
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Face recognition failed for student {student.roll_number}: {e}")
        # Face recognition failed, provide manual option
        return Response({
            'error': f'Face recognition failed: {str(e)}',
            'face_recognition_available': False,
            'manual_option_available': True,
            'matched_student_id': None,
            'confidence_score': 0.0,
            'status': 'face_not_found'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_attendance_self(request):
    """Mark attendance manually by student (when face recognition is not available)"""
    if not request.user.is_student:
        return Response({'error': 'Only students can mark self attendance'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        return Response({'error': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    session = request.data.get('session', 'daily')
    status_value = request.data.get('status', 'present')
    
    # Check if attendance already marked for today
    today = timezone.now().date()
    existing_attendance = Attendance.objects.filter(
        student=student,
        date=today,
        session=session
    ).first()
    
    if existing_attendance:
        return Response({
            'error': 'Attendance already marked for today!'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Determine if attendance is late
    current_time = timezone.now().time()
    final_status = 'present'
    
    # Simple late logic - after 9 AM is considered late
    if current_time.hour >= 9:
        final_status = 'late'
    
    # Create attendance record
    attendance = Attendance.objects.create(
        student=student,
        session=session,
        status=final_status,
        is_manual=True,
        marked_by=request.user
    )
    
    # Create audit log
    create_audit_log(
        user=request.user,
        action='mark',
        student=student,
        attendance=attendance,
        details=f"Self attendance marking - {final_status}",
        request=request
    )
    
    return Response({
        'message': f'Attendance marked successfully as {final_status}',
        'attendance': AttendanceSerializer(attendance).data
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def mark_attendance_manual(request):
    """Mark attendance manually (Admin only)"""
    serializer = ManualAttendanceSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        attendance = serializer.save()
        
        # Create audit log
        create_audit_log(
            user=request.user,
            action='mark',
            student=attendance.student,
            attendance=attendance,
            details=f"Manual attendance - {attendance.status}",
            request=request
        )
        
        return Response({
            'message': 'Attendance marked successfully',
            'attendance': AttendanceSerializer(attendance).data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_attendance(request):
    """Get current student's attendance records"""
    print(f"get_my_attendance called by user: {request.user.email}")
    print(f"Query parameters: {request.GET}")
    
    if not request.user.is_student:
        print(f"User {request.user.email} is not a student, role: {request.user.role}")
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        student = request.user.student_profile
        print(f"Found student profile: {student.full_name}")
    except Student.DoesNotExist:
        print(f"Student profile not found for user: {request.user.email}")
        return Response({'error': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        # Filter parameters
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        session = request.GET.get('session')
        month = request.GET.get('month')
        year = request.GET.get('year')
        
        print(f"Filters - date_from: {date_from}, date_to: {date_to}, session: {session}, month: {month}, year: {year}")
        
        attendances = Attendance.objects.filter(student=student)
        print(f"Initial attendance count: {attendances.count()}")
        
        # Apply filters
        if date_from:
            attendances = attendances.filter(date__gte=date_from)
            print(f"After date_from filter: {attendances.count()}")
        if date_to:
            attendances = attendances.filter(date__lte=date_to)
            print(f"After date_to filter: {attendances.count()}")
        if session:
            attendances = attendances.filter(session=session)
            print(f"After session filter: {attendances.count()}")
        if month and year:
            attendances = attendances.filter(date__month=month, date__year=year)
            print(f"After month/year filter: {attendances.count()}")
        elif year:
            attendances = attendances.filter(date__year=year)
            print(f"After year filter: {attendances.count()}")
        
        print(f"Final attendance count: {attendances.count()}")
        
        # Test serialization
        serializer = AttendanceSerializer(attendances, many=True)
        data = serializer.data
        print(f"Serialized data length: {len(data)}")
        
        return Response(data)
        
    except Exception as e:
        print(f"Error in get_my_attendance: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return Response({'error': f'Failed to get attendance: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_attendance_stats(request):
    """Get current student's attendance statistics"""
    print(f"get_my_attendance_stats called by user: {request.user.email}")
    
    if not request.user.is_student:
        print(f"User {request.user.email} is not a student, role: {request.user.role}")
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        student = request.user.student_profile
        print(f"Found student profile: {student.full_name}")
    except Student.DoesNotExist:
        print(f"Student profile not found for user: {request.user.email}")
        return Response({'error': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        serializer = AttendanceStatsSerializer(student)
        data = serializer.data
        print(f"Stats data: {data}")
        return Response(data)
    except Exception as e:
        print(f"Error in attendance stats serializer: {e}")
        return Response({'error': f'Failed to get stats: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_all_attendance(request):
    """Get all attendance records (Admin only)"""
    # Filter parameters
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    session = request.GET.get('session')
    student_class = request.GET.get('class')
    student_id = request.GET.get('student_id')
    status_filter = request.GET.get('status')
    
    attendances = Attendance.objects.all()
    
    # Apply filters
    if date_from:
        attendances = attendances.filter(date__gte=date_from)
    if date_to:
        attendances = attendances.filter(date__lte=date_to)
    if session:
        attendances = attendances.filter(session=session)
    if student_class:
        attendances = attendances.filter(student__student_class=student_class)
    if student_id:
        attendances = attendances.filter(student_id=student_id)
    if status_filter:
        attendances = attendances.filter(status=status_filter)
    
    serializer = AttendanceSerializer(attendances, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_attendance_analytics(request):
    """Get attendance analytics and statistics (Admin only)"""
    # Overall statistics
    total_students = Student.objects.count()
    total_attendance_records = Attendance.objects.count()
    
    # Today's statistics
    today = timezone.now().date()
    today_present = Attendance.objects.filter(date=today, status='present').count()
    today_late = Attendance.objects.filter(date=today, status='late').count()
    today_absent = Attendance.objects.filter(date=today, status='absent').count()
    
    # Low attendance students (less than 75%)
    low_attendance_students = []
    for student in Student.objects.all():
        stats = AttendanceStatsSerializer(student).data
        if stats['attendance_percentage'] < 75 and stats['total_classes'] > 0:
            low_attendance_students.append({
                'student': {
                    'id': student.id,
                    'name': student.full_name,
                    'roll_number': student.roll_number,
                    'class': student.student_class
                },
                'stats': stats
            })
    
    # Monthly attendance trend (last 6 months)
    monthly_stats = []
    for i in range(6):
        date = timezone.now().date() - timedelta(days=30*i)
        month_attendances = Attendance.objects.filter(
            date__year=date.year,
            date__month=date.month
        )
        monthly_stats.append({
            'month': date.strftime('%Y-%m'),
            'total': month_attendances.count(),
            'present': month_attendances.filter(status='present').count(),
            'late': month_attendances.filter(status='late').count(),
            'absent': month_attendances.filter(status='absent').count()
        })
    
    return Response({
        'overview': {
            'total_students': total_students,
            'total_attendance_records': total_attendance_records,
            'today_present': today_present,
            'today_late': today_late,
            'today_absent': today_absent
        },
        'low_attendance_students': low_attendance_students,
        'monthly_trend': monthly_stats
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def export_attendance_csv(request):
    """Export attendance records as CSV (Admin only)"""
    # Get filtered attendance records
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    student_class = request.GET.get('class')
    
    attendances = Attendance.objects.all()
    
    if date_from:
        attendances = attendances.filter(date__gte=date_from)
    if date_to:
        attendances = attendances.filter(date__lte=date_to)
    if student_class:
        attendances = attendances.filter(student__student_class=student_class)
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="attendance_report.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Roll Number', 'Student Name', 'Class', 'Date', 'Time', 
        'Session', 'Status', 'Marked By', 'Manual'
    ])
    
    for attendance in attendances:
        writer.writerow([
            attendance.student.roll_number,
            attendance.student.full_name,
            attendance.student.student_class,
            attendance.date,
            attendance.time,
            attendance.session,
            attendance.status,
            attendance.marked_by.username if attendance.marked_by else 'System',
            'Yes' if attendance.is_manual else 'No'
        ])
    
    return response


@api_view(['PUT'])
@permission_classes([IsAdminUser])
def update_attendance(request, attendance_id):
    """Update attendance record (Admin only)"""
    attendance = get_object_or_404(Attendance, id=attendance_id)
    
    old_status = attendance.status
    serializer = AttendanceSerializer(attendance, data=request.data, partial=True)
    
    if serializer.is_valid():
        updated_attendance = serializer.save()
        
        # Create audit log
        create_audit_log(
            user=request.user,
            action='update',
            student=attendance.student,
            attendance=attendance,
            details=f"Status changed from {old_status} to {updated_attendance.status}",
            request=request
        )
        
        return Response({
            'message': 'Attendance updated successfully',
            'attendance': serializer.data
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_attendance(request, attendance_id):
    """Delete attendance record (Admin only)"""
    attendance = get_object_or_404(Attendance, id=attendance_id)
    
    # Create audit log before deletion
    create_audit_log(
        user=request.user,
        action='delete',
        student=attendance.student,
        attendance=attendance,
        details=f"Deleted attendance for {attendance.date} ({attendance.session})",
        request=request
    )
    
    attendance.delete()
    return Response({'message': 'Attendance deleted successfully'})


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_audit_logs(request):
    """Get audit logs (Admin only)"""
    logs = AuditLog.objects.all()
    
    # Filter by date range
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if date_from:
        logs = logs.filter(timestamp__date__gte=date_from)
    if date_to:
        logs = logs.filter(timestamp__date__lte=date_to)
    
    serializer = AuditLogSerializer(logs, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_attendance_status(request):
    """Check if attendance is already marked for today"""
    if not request.user.is_student:
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        return Response({'error': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    today = timezone.now().date()
    session = request.GET.get('session', 'daily')
    
    attendance = Attendance.objects.filter(
        student=student,
        date=today,
        session=session
    ).first()
    
    if attendance:
        return Response({
            'marked': True,
            'attendance': AttendanceSerializer(attendance).data
        })
    else:
        return Response({'marked': False})


# Attendance Session Management
@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
def attendance_sessions(request):
    """Manage attendance sessions (Admin only)"""
    if request.method == 'GET':
        sessions = AttendanceSession.objects.all()
        serializer = AttendanceSessionSerializer(sessions, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = AttendanceSessionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)