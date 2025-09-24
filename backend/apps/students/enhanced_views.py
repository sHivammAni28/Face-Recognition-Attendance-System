from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.db import models
from .models import Student
from .serializers import StudentSerializer
from .enhanced_serializers import (
    EnhancedStudentRegistrationSerializer, 
    EnhancedFaceRegistrationSerializer,
    DuplicateCheckSerializer
)
from apps.authentication.models import User
from apps.authentication.enhanced_serializers import ValidationUtils, FaceDuplicateValidator
import logging

logger = logging.getLogger(__name__)


class IsAdminUser(permissions.BasePermission):
    """Custom permission to only allow admin users"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


@api_view(['POST'])
@permission_classes([AllowAny])
def enhanced_register_student(request):
    """Enhanced student registration with comprehensive duplicate checks"""
    logger.info(f"Enhanced student registration attempt with data: {request.data.keys()}")
    
    serializer = EnhancedStudentRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        try:
            student = serializer.save()
            logger.info(f"Student registration successful: {student.roll_number}")
            return Response({
                'message': 'Student registration successful',
                'student': StudentSerializer(student).data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error during student creation: {e}")
            return Response({
                'error': f'Registration failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    logger.warning(f"Student registration failed with errors: {serializer.errors}")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enhanced_register_face(request):
    """Enhanced face registration with duplicate check"""
    if request.user.is_student:
        # Student can only register their own face
        try:
            student = request.user.student_profile
        except Student.DoesNotExist:
            return Response({'error': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND)
    elif request.user.is_admin:
        # Admin can register face for any student
        student_id = request.data.get('student_id')
        if not student_id:
            return Response({'error': 'Student ID required'}, status=status.HTTP_400_BAD_REQUEST)
        student = get_object_or_404(Student, id=student_id)
    else:
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = EnhancedFaceRegistrationSerializer(student, data=request.data)
    if serializer.is_valid():
        try:
            serializer.save()
            logger.info(f"Face registration successful for student: {student.roll_number}")
            return Response({
                'message': 'Face registered successfully',
                'student': StudentSerializer(student).data
            })
        except Exception as e:
            logger.error(f"Error during face registration: {e}")
            return Response({
                'error': f'Face registration failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    logger.warning(f"Face registration failed with errors: {serializer.errors}")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def check_duplicates(request):
    """Check for various types of duplicates before registration"""
    serializer = DuplicateCheckSerializer(data=request.data)
    if serializer.is_valid():
        results = serializer.validated_data
        return Response({
            'duplicate_checks': results
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def validate_step1_credentials(request):
    """Validate Step 1 credentials before proceeding to face registration"""
    logger.info(f"Step 1 validation attempt with data: {list(request.data.keys())}")
    
    # Extract Step 1 fields
    step1_data = {
        'username': request.data.get('username'),
        'email': request.data.get('email'),
        'password': request.data.get('password'),
        'phone_number': request.data.get('phone_number'),
        'roll_number': request.data.get('roll_number')
    }
    
    # Remove None values
    step1_data = {k: v for k, v in step1_data.items() if v is not None}
    
    errors = {}
    
    # Check each field for duplicates
    if 'username' in step1_data:
        if ValidationUtils.check_username_exists(step1_data['username']):
            errors['username'] = ['Username already taken.']
    
    if 'email' in step1_data:
        if ValidationUtils.check_email_exists(step1_data['email']):
            errors['email'] = ['Email is already taken.']
    
    if 'phone_number' in step1_data and step1_data['phone_number'].strip():
        if ValidationUtils.check_phone_exists(step1_data['phone_number']):
            errors['phone_number'] = ['Mobile number is already registered.']
    
    if 'password' in step1_data:
        if ValidationUtils.check_password_exists(step1_data['password']):
            errors['password'] = ['Password is already taken.']
    
    if 'roll_number' in step1_data:
        if ValidationUtils.check_roll_number_exists(step1_data['roll_number']):
            errors['roll_number'] = ['Roll number already exists']
    
    if errors:
        logger.warning(f"Step 1 validation failed with errors: {errors}")
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)
    
    logger.info("Step 1 validation successful")
    return Response({
        'message': 'Step 1 validation successful. You can proceed to face registration.',
        'valid': True
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def check_username_duplicate(request):
    """Check if username already exists"""
    username = request.GET.get('username')
    if not username:
        return Response({'error': 'Username parameter required'}, status=status.HTTP_400_BAD_REQUEST)
    
    exists = ValidationUtils.check_username_exists(username)
    return Response({
        'exists': exists,
        'message': 'Username already taken.' if exists else 'Username is available.'
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def check_email_duplicate(request):
    """Check if email already exists"""
    email = request.GET.get('email')
    if not email:
        return Response({'error': 'Email parameter required'}, status=status.HTTP_400_BAD_REQUEST)
    
    exists = ValidationUtils.check_email_exists(email)
    return Response({
        'exists': exists,
        'message': 'Email is already taken.' if exists else 'Email is available.'
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def check_phone_duplicate(request):
    """Check if phone number already exists"""
    phone_number = request.GET.get('phone_number')
    if not phone_number:
        return Response({'error': 'Phone number parameter required'}, status=status.HTTP_400_BAD_REQUEST)
    
    exists = ValidationUtils.check_phone_exists(phone_number)
    return Response({
        'exists': exists,
        'message': 'Mobile number is already registered.' if exists else 'Mobile number is available.'
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def check_password_duplicate(request):
    """Check if password already exists"""
    password = request.data.get('password')
    if not password:
        return Response({'error': 'Password parameter required'}, status=status.HTTP_400_BAD_REQUEST)
    
    exists = ValidationUtils.check_password_exists(password)
    return Response({
        'exists': exists,
        'message': 'Password is already taken.' if exists else 'Password is available.'
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def check_roll_number_duplicate(request):
    """Check if roll number already exists"""
    roll_number = request.GET.get('roll_number')
    if not roll_number:
        return Response({'error': 'Roll number parameter required'}, status=status.HTTP_400_BAD_REQUEST)
    
    exists = ValidationUtils.check_roll_number_exists(roll_number)
    return Response({
        'exists': exists,
        'message': 'Roll number already exists' if exists else 'Roll number is available.'
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def get_face_similarity_report(request):
    """Get detailed face similarity report"""
    face_image_data = request.data.get('face_image_data')
    if not face_image_data:
        return Response({'error': 'Face image data required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        from apps.attendance.enhanced_face_duplicate_validator import enhanced_face_validator
        
        if enhanced_face_validator is None:
            return Response({
                'error': 'Enhanced face validator not available'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        exclude_student_id = request.data.get('exclude_student_id')
        report = enhanced_face_validator.get_similarity_report(face_image_data, exclude_student_id)
        
        return Response({
            'similarity_report': report
        })
        
    except Exception as e:
        logger.error(f"Error generating face similarity report: {e}")
        return Response({
            'error': f'Face similarity report generation failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def check_face_duplicate(request):
    """Check if face is already registered"""
    face_image_data = request.data.get('face_image_data')
    if not face_image_data:
        return Response({'error': 'Face image data required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        is_duplicate, duplicate_info = FaceDuplicateValidator.check_face_duplicate(face_image_data)
        
        response_data = {
            'exists': is_duplicate,
            'message': 'This face is already registered with another account.' if is_duplicate else 'Face is available for registration.'
        }
        
        if is_duplicate and duplicate_info:
            response_data['duplicate_info'] = {
                'student_name': duplicate_info['student_name'],
                'roll_number': duplicate_info['roll_number'],
                'confidence': duplicate_info['confidence']
            }
        
        return Response(response_data)
        
    except Exception as e:
        logger.error(f"Error checking face duplicate: {e}")
        return Response({
            'error': f'Face duplicate check failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Keep existing views for backward compatibility
@api_view(['POST'])
@permission_classes([AllowAny])
def register_student(request):
    """Original student registration (kept for backward compatibility)"""
    # Redirect to enhanced registration
    return enhanced_register_student(request)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_student_profile(request):
    """Get current student's profile"""
    logger.info(f"get_student_profile called by user: {request.user.email}")
    
    if not request.user.is_student:
        logger.warning(f"User {request.user.email} is not a student, role: {request.user.role}")
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        student = request.user.student_profile
        logger.info(f"Found student profile: {student.full_name}")
        serializer = StudentSerializer(student)
        data = serializer.data
        logger.info(f"Profile data: {data}")
        return Response(data)
    except Student.DoesNotExist:
        logger.error(f"Student profile not found for user: {request.user.email}")
        return Response({'error': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error in get_student_profile: {e}")
        return Response({'error': f'Failed to get profile: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_student_profile(request):
    """Update current student's profile"""
    if not request.user.is_student:
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        student = request.user.student_profile
        serializer = StudentSerializer(student, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Profile updated successfully',
                'student': serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Student.DoesNotExist:
        return Response({'error': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_face(request):
    """Original face registration (kept for backward compatibility)"""
    # Redirect to enhanced face registration
    return enhanced_register_face(request)