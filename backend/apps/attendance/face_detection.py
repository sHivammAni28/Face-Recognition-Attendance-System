"""
Face detection utilities for attendance system
Now using DeepFace as the primary face recognition library
"""
import base64
import io
import logging
from PIL import Image

logger = logging.getLogger(__name__)

def detect_face_in_image(face_image_data):
    """
    Detect face in image using available libraries
    Priority: DeepFace -> OpenCV -> Simple Mock
    Returns: (success, message)
    """
    try:
        # Try DeepFace first (new primary method)
        try:
            from .deepface_utils import detect_face_deepface
            
            logger.info("Using DeepFace for face detection...")
            success, message = detect_face_deepface(face_image_data)
            if success:
                return True, f'Face detected successfully using DeepFace: {message}'
            else:
                logger.warning(f"DeepFace detection failed: {message}")
                # Continue to fallback methods
                
        except ImportError as e:
            logger.warning(f"DeepFace not available: {e}")
        except Exception as e:
            logger.error(f"DeepFace detection error: {e}")
        
        # Try legacy face_recognition as fallback
        try:
            import face_recognition
            import numpy as np
            
            logger.info("Using legacy face_recognition as fallback...")
            
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
                return False, 'No face detected in the image'
            elif len(face_encodings) > 1:
                return False, 'Multiple faces detected. Please ensure only one face is visible'
            
            return True, 'Face detected successfully using legacy face_recognition'
            
        except ImportError:
            logger.info("Legacy face_recognition not available, trying OpenCV...")
            
            # Try OpenCV face detection as fallback
            import cv2
            import numpy as np
            
            # Decode base64 image
            if ',' in face_image_data:
                face_image_data = face_image_data.split(',')[1]
            
            image_data = base64.b64decode(face_image_data)
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert PIL to OpenCV format
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
            
            # Load face detection model
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            # Detect faces
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            if len(faces) == 0:
                return False, 'No face detected in the image'
            elif len(faces) > 1:
                return False, 'Multiple faces detected. Please ensure only one face is visible'
            
            return True, 'Face detected successfully using OpenCV'
            
    except ImportError:
        # Fall back to mock face detection
        logger.info("Advanced face recognition libraries not available, using simple detection...")
        try:
            from .simple_face_mock import detect_face_in_image as mock_detect
            return mock_detect(face_image_data)
        except ImportError:
            return False, 'Face detection libraries not available on this system'
    except Exception as e:
        logger.error(f"Face detection error: {e}")
        return False, f'Face detection error: {str(e)}'