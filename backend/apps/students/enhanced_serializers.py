from rest_framework import serializers
from .models import Student
from apps.authentication.models import User
from apps.authentication.enhanced_serializers import (
    EnhancedUserRegistrationSerializer, 
    FaceDuplicateValidator, 
    ValidationUtils
)
import base64
import io
import logging

logger = logging.getLogger(__name__)

# Try to import face recognition dependencies
try:
    from PIL import Image
    import numpy as np
    from apps.attendance.deepface_utils import generate_face_embedding, invalidate_student_embeddings_cache
    DEEPFACE_AVAILABLE = True
    FACE_RECOGNITION_AVAILABLE = True
    logger.info("DeepFace is available for face recognition")
except ImportError:
    DEEPFACE_AVAILABLE = False
    FACE_RECOGNITION_AVAILABLE = False
    logger.warning("Face recognition libraries not available. Face features will be disabled.")
    # Create dummy classes to prevent import errors
    class Image:
        @staticmethod
        def open(*args, **kwargs):
            raise NotImplementedError("PIL not available")
    
    import sys
    if 'numpy' not in sys.modules:
        class np:
            @staticmethod
            def array(*args, **kwargs):
                raise NotImplementedError("numpy not available")
    else:
        import numpy as np


class EnhancedStudentRegistrationSerializer(serializers.Serializer):
    """Enhanced serializer for complete student registration with all duplicate checks"""
    # User fields
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=30, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=30, required=False, allow_blank=True)
    
    # Student fields
    roll_number = serializers.CharField(max_length=20)
    student_class = serializers.CharField(max_length=50, default='General')
    phone_number = serializers.CharField(max_length=15, required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    
    # Face data
    face_image_data = serializers.CharField(write_only=True, required=False)  # Base64 encoded image
    
    def validate_username(self, value):
        """Check for duplicate username"""
        if ValidationUtils.check_username_exists(value):
            raise serializers.ValidationError("Username already taken.")
        return value
    
    def validate_email(self, value):
        """Check for duplicate email"""
        if ValidationUtils.check_email_exists(value):
            raise serializers.ValidationError("Email is already taken.")
        return value
    
    def validate_phone_number(self, value):
        """Check for duplicate mobile number"""
        if value and value.strip():  # Only check if phone number is provided
            if ValidationUtils.check_phone_exists(value):
                raise serializers.ValidationError("Mobile number is already registered.")
        return value
    
    def validate_password(self, value):
        """Check for duplicate password"""
        if ValidationUtils.check_password_exists(value):
            raise serializers.ValidationError("Password is already taken.")
        return value
    
    def validate_roll_number(self, value):
        """Check for duplicate roll number"""
        if ValidationUtils.check_roll_number_exists(value):
            raise serializers.ValidationError("Roll number already exists")
        return value
    
    def validate_face_image_data(self, value):
        """Check for duplicate face"""
        if value and DEEPFACE_AVAILABLE:
            is_duplicate, duplicate_info = FaceDuplicateValidator.check_face_duplicate(value)
            if is_duplicate:
                raise serializers.ValidationError("This face is already registered with another account.")
        return value
    
    def validate(self, attrs):
        """Additional validation checks"""
        # Validate passwords match
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords don't match"})
        
        return attrs
    
    def create(self, validated_data):
        """Create user and student with all validations"""
        # Extract face image data
        face_image_data = validated_data.pop('face_image_data', None)
        validated_data.pop('confirm_password')
        
        # Create user
        user_data = {
            'username': validated_data.pop('username'),
            'email': validated_data.pop('email'),
            'password': validated_data.pop('password'),
            'first_name': validated_data.pop('first_name', ''),
            'last_name': validated_data.pop('last_name', ''),
        }
        
        user = User.objects.create_user(**user_data, role='student')
        
        # Create student
        student = Student.objects.create(user=user, **validated_data)
        
        # Process face image if provided
        if face_image_data:
            try:
                self._process_face_image(student, face_image_data)
            except Exception as e:
                # If face processing fails, still create the student but without face registration
                logger.error(f"Face processing failed during registration: {e}")
        
        return student
    
    def _process_face_image(self, student, face_image_data):
        """Process and encode face image using DeepFace"""
        if not FACE_RECOGNITION_AVAILABLE:
            logger.warning("Face recognition not available, skipping face processing")
            return
        
        try:
            if DEEPFACE_AVAILABLE:
                logger.info("Processing face image with DeepFace")
                success, message, embedding = generate_face_embedding(face_image_data)
                
                if success and embedding is not None:
                    student.set_face_encoding(embedding)
                    student.save()
                    # Invalidate cache when new student is registered
                    invalidate_student_embeddings_cache()
                    logger.info(f"Face registered successfully using DeepFace for student {student.roll_number}")
                    return
                else:
                    logger.warning(f"DeepFace processing failed: {message}")
            
            # If we get here, face processing failed
            raise serializers.ValidationError("Face processing failed")
            
        except Exception as e:
            raise serializers.ValidationError(f"Face processing error: {str(e)}")


class EnhancedFaceRegistrationSerializer(serializers.Serializer):
    """Enhanced serializer for face registration with duplicate check"""
    face_image_data = serializers.CharField(write_only=True)  # Base64 encoded image
    
    def __init__(self, *args, **kwargs):
        self.student_instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)
    
    def validate_face_image_data(self, value):
        """Validate and check for duplicate face"""
        if not FACE_RECOGNITION_AVAILABLE:
            raise serializers.ValidationError("Face recognition is not available on this system")
        
        # Check for face duplicate, excluding current student
        exclude_id = self.student_instance.id if self.student_instance else None
        is_duplicate, duplicate_info = FaceDuplicateValidator.check_face_duplicate(value, exclude_id)
        
        if is_duplicate:
            raise serializers.ValidationError("This face is already registered with another account.")
        
        try:
            # Generate embedding for validation
            if DEEPFACE_AVAILABLE:
                logger.info("Validating face image with DeepFace")
                success, message, embedding = generate_face_embedding(value)
                
                if success and embedding is not None:
                    return embedding
                else:
                    raise serializers.ValidationError(f"Face processing failed: {message}")
            
            raise serializers.ValidationError("Face validation failed")
            
        except Exception as e:
            raise serializers.ValidationError(f"Face processing error: {str(e)}")
    
    def update(self, instance, validated_data):
        """Update student with new face encoding"""
        if not FACE_RECOGNITION_AVAILABLE:
            raise serializers.ValidationError("Face recognition is not available on this system")
        
        face_encoding = validated_data['face_image_data']
        instance.set_face_encoding(face_encoding)
        instance.save()
        
        # Invalidate cache when student face is updated
        if DEEPFACE_AVAILABLE:
            invalidate_student_embeddings_cache()
        
        return instance


class DuplicateCheckSerializer(serializers.Serializer):
    """Serializer for individual duplicate checks (for frontend validation)"""
    username = serializers.CharField(max_length=150, required=False)
    email = serializers.EmailField(required=False)
    phone_number = serializers.CharField(max_length=15, required=False)
    password = serializers.CharField(required=False)
    roll_number = serializers.CharField(max_length=20, required=False)
    face_image_data = serializers.CharField(required=False)
    
    def validate(self, attrs):
        """Perform the requested duplicate checks"""
        results = {}
        
        # Check username
        if 'username' in attrs:
            results['username_exists'] = ValidationUtils.check_username_exists(attrs['username'])
        
        # Check email
        if 'email' in attrs:
            results['email_exists'] = ValidationUtils.check_email_exists(attrs['email'])
        
        # Check phone number
        if 'phone_number' in attrs:
            results['phone_exists'] = ValidationUtils.check_phone_exists(attrs['phone_number'])
        
        # Check password
        if 'password' in attrs:
            results['password_exists'] = ValidationUtils.check_password_exists(attrs['password'])
        
        # Check roll number
        if 'roll_number' in attrs:
            results['roll_number_exists'] = ValidationUtils.check_roll_number_exists(attrs['roll_number'])
        
        # Check face
        if 'face_image_data' in attrs and DEEPFACE_AVAILABLE:
            is_duplicate, duplicate_info = FaceDuplicateValidator.check_face_duplicate(attrs['face_image_data'])
            results['face_exists'] = is_duplicate
            if is_duplicate:
                results['face_duplicate_info'] = duplicate_info
        
        return results