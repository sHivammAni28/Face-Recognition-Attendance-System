from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import check_password
from .models import User
from apps.students.models import Student
import numpy as np
import json
import logging

logger = logging.getLogger(__name__)

# Try to import face recognition dependencies
try:
    from apps.attendance.deepface_utils import generate_face_embedding, verify_face_match
    from apps.attendance.enhanced_face_duplicate_validator import enhanced_face_validator
    DEEPFACE_AVAILABLE = True
except ImportError:
    DEEPFACE_AVAILABLE = False
    enhanced_face_validator = None
    logger.warning("DeepFace not available for face duplicate checking")


class EnhancedUserRegistrationSerializer(serializers.ModelSerializer):
    """Enhanced serializer with comprehensive duplicate checks"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)
    phone_number = serializers.CharField(max_length=15, required=False, allow_blank=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'confirm_password', 'first_name', 'last_name', 'phone_number')
    
    def validate_username(self, value):
        """Check for duplicate username"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already taken.")
        return value
    
    def validate_email(self, value):
        """Check for duplicate email"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already taken.")
        return value
    
    def validate_phone_number(self, value):
        """Check for duplicate mobile number"""
        if value and value.strip():  # Only check if phone number is provided
            if Student.objects.filter(phone_number=value).exists():
                raise serializers.ValidationError("Mobile number is already registered.")
        return value
    
    def validate_password(self, value):
        """Check for duplicate password"""
        # Get all existing users and check if any has the same password
        for user in User.objects.all():
            if check_password(value, user.password):
                raise serializers.ValidationError("Password is already taken.")
        return value
    
    def validate(self, attrs):
        """Additional validation checks"""
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords don't match"})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        phone_number = validated_data.pop('phone_number', None)
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role='student'  # Default role for registration
        )
        
        # Store phone number in user's session or temporary storage
        # This will be used when creating the student profile
        if hasattr(self, 'context') and 'request' in self.context:
            self.context['request'].session['temp_phone_number'] = phone_number
        
        return user


class FaceDuplicateValidator:
    """Utility class for face duplicate validation"""
    
    @staticmethod
    def check_face_duplicate(face_image_data, exclude_student_id=None):
        """Check if the face is already registered with another account"""
        if not DEEPFACE_AVAILABLE or enhanced_face_validator is None:
            logger.warning("Enhanced face validator not available, skipping face duplicate check")
            return False, None
        
        try:
            # Use the enhanced face duplicate validator
            is_duplicate, duplicate_info = enhanced_face_validator.check_face_duplicate(
                face_image_data, exclude_student_id
            )
            
            if is_duplicate and duplicate_info:
                logger.info(
                    f"Face duplicate detected: matches student {duplicate_info['roll_number']} "
                    f"with confidence {duplicate_info['confidence']:.3f}"
                )
                
                # Log detailed similarity information
                if 'similarity_details' in duplicate_info:
                    logger.debug(f"Similarity details: {duplicate_info['similarity_details']}")
                if 'metric_votes' in duplicate_info:
                    logger.debug(f"Metric votes: {duplicate_info['metric_votes']}")
                
                return True, {
                    'student_id': duplicate_info['student_id'],
                    'student_name': duplicate_info['student_name'],
                    'roll_number': duplicate_info['roll_number'],
                    'email': duplicate_info['email'],
                    'confidence': duplicate_info['confidence'],
                    'similarity_details': duplicate_info.get('similarity_details', {}),
                    'agreeing_metrics': duplicate_info.get('agreeing_metrics', 0)
                }
            
            return False, None
            
        except Exception as e:
            logger.error(f"Error in enhanced face duplicate check: {e}")
            return False, None


class ValidationUtils:
    """Utility class for various validation checks"""
    
    @staticmethod
    def check_username_exists(username, exclude_user_id=None):
        """Check if username already exists"""
        queryset = User.objects.filter(username=username)
        if exclude_user_id:
            queryset = queryset.exclude(id=exclude_user_id)
        return queryset.exists()
    
    @staticmethod
    def check_email_exists(email, exclude_user_id=None):
        """Check if email already exists"""
        queryset = User.objects.filter(email=email)
        if exclude_user_id:
            queryset = queryset.exclude(id=exclude_user_id)
        return queryset.exists()
    
    @staticmethod
    def check_phone_exists(phone_number, exclude_student_id=None):
        """Check if phone number already exists"""
        if not phone_number or not phone_number.strip():
            return False
        
        queryset = Student.objects.filter(phone_number=phone_number)
        if exclude_student_id:
            queryset = queryset.exclude(id=exclude_student_id)
        return queryset.exists()
    
    @staticmethod
    def check_password_exists(password, exclude_user_id=None):
        """Check if password already exists"""
        queryset = User.objects.all()
        if exclude_user_id:
            queryset = queryset.exclude(id=exclude_user_id)
        
        for user in queryset:
            if check_password(password, user.password):
                return True
        return False
    
    @staticmethod
    def check_roll_number_exists(roll_number, exclude_student_id=None):
        """Check if roll number already exists"""
        queryset = Student.objects.filter(roll_number=roll_number)
        if exclude_student_id:
            queryset = queryset.exclude(id=exclude_student_id)
        return queryset.exists()