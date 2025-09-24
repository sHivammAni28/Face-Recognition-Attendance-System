from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.db import models
from .models import Student
from .serializers import StudentSerializer, StudentRegistrationSerializer, FaceRegistrationSerializer
from apps.authentication.models import User


class IsAdminUser(permissions.BasePermission):
    """Custom permission to only allow admin users"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


@api_view(['POST'])
@permission_classes([AllowAny])
def register_student(request):
    """Register a new student with face capture"""
    serializer = StudentRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        student = serializer.save()
        return Response({
            'message': 'Student registration successful',
            'student': StudentSerializer(student).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_student_profile(request):
    """Get current student's profile"""
    print(f"get_student_profile called by user: {request.user.email}")
    
    if not request.user.is_student:
        print(f"User {request.user.email} is not a student, role: {request.user.role}")
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        student = request.user.student_profile
        print(f"Found student profile: {student.full_name}")
        serializer = StudentSerializer(student)
        data = serializer.data
        print(f"Profile data: {data}")
        return Response(data)
    except Student.DoesNotExist:
        print(f"Student profile not found for user: {request.user.email}")
        return Response({'error': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error in get_student_profile: {e}")
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
    """Register or re-register student face"""
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
    
    serializer = FaceRegistrationSerializer(student, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Face registered successfully',
            'student': StudentSerializer(student).data
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Admin-only views
@api_view(['GET'])
@permission_classes([IsAdminUser])
def list_students(request):
    """List all students (Admin only)"""
    students = Student.objects.all()
    
    # Filter by class if provided
    student_class = request.GET.get('class')
    if student_class:
        students = students.filter(student_class=student_class)
    
    # Search by name or roll number
    search = request.GET.get('search')
    if search:
        students = students.filter(
            models.Q(user__first_name__icontains=search) |
            models.Q(user__last_name__icontains=search) |
            models.Q(roll_number__icontains=search)
        )
    
    serializer = StudentSerializer(students, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_student_detail(request, student_id):
    """Get student details (Admin only)"""
    student = get_object_or_404(Student, id=student_id)
    serializer = StudentSerializer(student)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAdminUser])
def update_student(request, student_id):
    """Update student details (Admin only)"""
    student = get_object_or_404(Student, id=student_id)
    serializer = StudentSerializer(student, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Student updated successfully',
            'student': serializer.data
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_student(request, student_id):
    """Delete student (Admin only)"""
    student = get_object_or_404(Student, id=student_id)
    user = student.user
    student.delete()
    user.delete()  # Also delete the associated user
    return Response({'message': 'Student deleted successfully'})


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_classes(request):
    """Get list of all classes (Admin only)"""
    classes = Student.objects.values_list('student_class', flat=True).distinct()
    return Response(list(classes))