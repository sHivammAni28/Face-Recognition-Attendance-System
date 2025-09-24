from rest_framework import serializers
from .models import Student
from apps.authentication.models import User
from apps.authentication.serializers import UserRegistrationSerializer
import base64
import io
import logging

logger = logging.getLogger(__name__)

# Try to import face recognition dependencies
try:
    from PIL import Image
    import numpy as np
    # Try DeepFace first
    try:
        from apps.attendance.deepface_utils import generate_face_embedding, invalidate_student_embeddings_cache
        DEEPFACE_AVAILABLE = True
        FACE_RECOGNITION_AVAILABLE = True  # For backward compatibility
        logger.info("DeepFace is available for face recognition")
    except ImportError:
        DEEPFACE_AVAILABLE = False
        # Try legacy face_recognition as fallback
        try:
            import face_recognition
            FACE_RECOGNITION_AVAILABLE = True
            logger.info("Using legacy face_recognition library")
        except ImportError:
            FACE_RECOGNITION_AVAILABLE = False
            logger.warning("No face recognition libraries available. Face features will be disabled.")
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


class StudentSerializer(serializers.ModelSerializer):
    """Serializer for Student model"""
    full_name = serializers.ReadOnlyField()
    email = serializers.ReadOnlyField()
    user_id = serializers.ReadOnlyField(source='user.id')
    username = serializers.ReadOnlyField(source='user.username')
    first_name = serializers.ReadOnlyField(source='user.first_name')
    last_name = serializers.ReadOnlyField(source='user.last_name')
    
    class Meta:
        model = Student
        fields = [
            'id', 'user_id', 'username', 'first_name', 'last_name', 'full_name', 
            'email', 'roll_number', 'student_class', 'phone_number', 'address',
            'is_face_registered', 'face_image_data', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_face_registered']


class StudentRegistrationSerializer(serializers.Serializer):
    """Serializer for complete student registration with face capture"""
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
    
    def validate(self, attrs):
        # Validate passwords match
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        
        # Check if email already exists
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError("Email already exists")
        
        # Check if roll number already exists
        if Student.objects.filter(roll_number=attrs['roll_number']).exists():
            raise serializers.ValidationError("Roll number already exists")
        
        return attrs
    
    def create(self, validated_data):
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
        """Process and encode face image using DeepFace or fallback methods"""
        if not FACE_RECOGNITION_AVAILABLE:
            logger.warning("Face recognition not available, skipping face processing")
            return
        
        try:
            # Try DeepFace first
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
                    # Fall back to legacy method
            
            # Fallback to legacy face_recognition
            if not DEEPFACE_AVAILABLE and FACE_RECOGNITION_AVAILABLE:
                logger.info("Processing face image with legacy face_recognition")
                self._process_face_image_legacy(student, face_image_data)
                return
            
            # If we get here, face processing failed
            raise serializers.ValidationError("Face processing failed with all available methods")
            
        except Exception as e:
            raise serializers.ValidationError(f"Face processing error: {str(e)}")
    
    def _process_face_image_legacy(self, student, face_image_data):
        """Legacy face processing using face_recognition library"""
        try:
            import face_recognition
            
            # Decode base64 image
            if ',' in face_image_data:
                face_image_data = face_image_data.split(',')[1]
            
            image_data = base64.b64decode(face_image_data)
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert PIL image to numpy array
            image_array = np.array(image)
            
            # Find face encodings
            face_encodings = face_recognition.face_encodings(image_array)
            
            if len(face_encodings) == 0:
                raise serializers.ValidationError("No face detected in the image")
            elif len(face_encodings) > 1:
                raise serializers.ValidationError("Multiple faces detected. Please ensure only one face is visible")
            
            # Store the face encoding
            student.set_face_encoding(face_encodings[0])
            student.save()
            logger.info(f"Face registered successfully using legacy method for student {student.roll_number}")
            
        except ImportError:
            raise serializers.ValidationError("Legacy face recognition library not available")
        except Exception as e:
            raise serializers.ValidationError(f"Legacy face processing error: {str(e)}")


class FaceRegistrationSerializer(serializers.Serializer):
    """Serializer for face registration/re-registration"""
    face_image_data = serializers.CharField(write_only=True)  # Base64 encoded image
    
    def validate_face_image_data(self, value):
        """Validate and process face image"""
        if not FACE_RECOGNITION_AVAILABLE:
            raise serializers.ValidationError("Face recognition is not available on this system")
        
        try:
            # Try DeepFace first
            if DEEPFACE_AVAILABLE:
                logger.info("Validating face image with DeepFace")
                success, message, embedding = generate_face_embedding(value)
                
                if success and embedding is not None:
                    return embedding
                else:
                    logger.warning(f"DeepFace validation failed: {message}")
                    # Fall back to legacy method
            
            # Fallback to legacy face_recognition
            if not DEEPFACE_AVAILABLE and FACE_RECOGNITION_AVAILABLE:
                logger.info("Validating face image with legacy face_recognition")
                return self._validate_face_image_legacy(value)
            
            # If we get here, validation failed
            raise serializers.ValidationError("Face validation failed with all available methods")
            
        except Exception as e:
            raise serializers.ValidationError(f"Face processing error: {str(e)}")
    
    def _validate_face_image_legacy(self, value):
        """Legacy face validation using face_recognition library"""
        try:
            import face_recognition
            
            # Decode base64 image
            if ',' in value:
                value = value.split(',')[1]
            
            image_data = base64.b64decode(value)
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert PIL image to numpy array
            image_array = np.array(image)
            
            # Find face encodings
            face_encodings = face_recognition.face_encodings(image_array)
            
            if len(face_encodings) == 0:
                raise serializers.ValidationError("No face detected in the image")
            elif len(face_encodings) > 1:
                raise serializers.ValidationError("Multiple faces detected. Please ensure only one face is visible")
            
            return face_encodings[0]
            
        except ImportError:
            raise serializers.ValidationError("Legacy face recognition library not available")
        except Exception as e:
            raise serializers.ValidationError(f"Legacy face processing error: {str(e)}")
    
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