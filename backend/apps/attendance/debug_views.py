"""
Debug version of attendance views with detailed error logging
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Attendance
from .serializers import AttendanceSerializer
from apps.students.models import Student
import logging
import json

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def debug_mark_attendance_face(request):
    """Debug version of mark_attendance_face with detailed logging"""
    
    # Log the incoming request
    logger.info(f"=== DEBUG FACE ATTENDANCE REQUEST ===")
    logger.info(f"User: {request.user.email} (ID: {request.user.id})")
    logger.info(f"User role: {getattr(request.user, 'role', 'unknown')}")
    logger.info(f"Request data keys: {list(request.data.keys())}")
    logger.info(f"Request method: {request.method}")
    
    # Check 1: User is student
    if not request.user.is_student:
        error_msg = f'User {request.user.email} is not a student (role: {getattr(request.user, "role", "unknown")})'
        logger.error(error_msg)
        return Response({
            'error': 'Only students can mark attendance via face recognition',
            'debug_info': error_msg
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Check 2: Student profile exists
    try:
        student = request.user.student_profile
        logger.info(f"Found student profile: {student.full_name} (ID: {student.id})")
    except Student.DoesNotExist:
        error_msg = f'Student profile not found for user {request.user.email}'
        logger.error(error_msg)
        return Response({
            'error': 'Student profile not found',
            'debug_info': error_msg
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Check 3: Face registration
    logger.info(f"Student face registration status: {student.is_face_registered}")
    logger.info(f"Student has face encoding: {bool(student.face_encoding)}")
    
    if not student.is_face_registered:
        error_msg = f'Student {student.full_name} has not registered face'
        logger.error(error_msg)
        return Response({
            'error': 'Face not registered. Please register your face first.',
            'face_registration_required': True,
            'debug_info': error_msg
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check 4: Already marked today
    today = timezone.now().date()
    session = request.data.get('session', 'daily')
    logger.info(f"Checking attendance for date: {today}, session: {session}")
    
    existing_attendance = Attendance.objects.filter(
        student=student,
        date=today,
        session=session
    ).first()
    
    if existing_attendance:
        error_msg = f'Attendance already marked for {today} session {session}'
        logger.warning(error_msg)
        return Response({
            'error': 'Attendance already marked for today!',
            'debug_info': error_msg
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check 5: Face image data
    face_image_data = request.data.get('face_image_data')
    logger.info(f"Face image data provided: {bool(face_image_data)}")
    if face_image_data:
        logger.info(f"Face image data length: {len(face_image_data)}")
        logger.info(f"Face image data starts with: {face_image_data[:50]}...")
    
    if not face_image_data:
        error_msg = 'No face image data provided in request'
        logger.error(error_msg)
        return Response({
            'error': 'No face image provided',
            'debug_info': error_msg
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check 6: DeepFace availability
    try:
        from .deepface_utils import generate_face_embedding, verify_face_match
        logger.info("DeepFace utilities imported successfully")
    except ImportError as e:
        error_msg = f'DeepFace not available: {e}'
        logger.error(error_msg)
        return Response({
            'error': 'Face recognition system not available',
            'debug_info': error_msg
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # If we get here, everything looks good for processing
    logger.info("All checks passed, proceeding with face recognition...")
    
    try:
        # Generate embedding for the captured image
        success, message, face_embedding = generate_face_embedding(face_image_data)
        logger.info(f"Face embedding generation: success={success}, message={message}")
        
        if not success or face_embedding is None:
            error_msg = f'Face processing failed: {message}'
            logger.error(error_msg)
            return Response({
                'error': f'Face processing failed: {message}',
                'debug_info': error_msg,
                'status': 'face_not_found'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get student's stored embedding
        stored_embedding = student.get_face_encoding()
        if stored_embedding is None:
            error_msg = 'No stored face encoding found for student'
            logger.error(error_msg)
            return Response({
                'error': 'No stored face encoding found for student',
                'debug_info': error_msg
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify face match
        is_match, confidence = verify_face_match(stored_embedding, face_embedding)
        logger.info(f"Face verification: match={is_match}, confidence={confidence}")
        
        if not is_match:
            error_msg = f'Face verification failed. Confidence: {confidence:.2f}'
            logger.warning(error_msg)
            return Response({
                'error': f'Face verification failed. Confidence: {confidence:.2f}',
                'matched_student_id': None,
                'confidence_score': confidence,
                'status': 'face_not_matched',
                'debug_info': error_msg
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Success! Mark attendance
        current_time = timezone.now().time()
        final_status = 'late' if current_time.hour >= 9 else 'present'
        
        attendance = Attendance.objects.create(
            student=student,
            session=session,
            status=final_status,
            is_face_recognition=True,
            marked_by=request.user
        )
        
        logger.info(f"Attendance marked successfully: {final_status}")
        
        return Response({
            'message': f'Attendance marked successfully as {final_status}',
            'attendance': AttendanceSerializer(attendance).data,
            'matched_student_id': student.id,
            'confidence_score': confidence,
            'status': 'success'
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        error_msg = f'Unexpected error during face recognition: {str(e)}'
        logger.error(error_msg, exc_info=True)
        return Response({
            'error': 'Face recognition failed due to system error',
            'debug_info': error_msg,
            'status': 'system_error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)