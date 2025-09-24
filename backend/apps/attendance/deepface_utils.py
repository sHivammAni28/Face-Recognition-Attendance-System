"""
DeepFace utilities for facial recognition in attendance system
"""
import os
import base64
import io
import numpy as np
import logging
from typing import Tuple, Optional, List, Dict, Any
from PIL import Image
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

# Global model cache to avoid reloading
_model_cache = {}

def get_deepface_config() -> Dict[str, Any]:
    """Get DeepFace configuration from environment variables"""
    return {
        'model_name': os.getenv('DEEPFACE_MODEL', 'Facenet'),
        'similarity_threshold': float(os.getenv('DEEPFACE_SIMILARITY_THRESHOLD', '0.8')),
        'detector_backend': os.getenv('DEEPFACE_DETECTOR_BACKEND', 'opencv'),
        'enforce_detection': os.getenv('DEEPFACE_ENFORCE_DETECTION', 'False').lower() == 'true'
    }

def preload_deepface_model():
    """Preload DeepFace model to improve performance"""
    try:
        from deepface import DeepFace
        config = get_deepface_config()
        
        # Create a dummy image to trigger model loading
        dummy_img = np.zeros((224, 224, 3), dtype=np.uint8)
        
        logger.info(f"Preloading DeepFace model: {config['model_name']}")
        DeepFace.represent(
            img_path=dummy_img,
            model_name=config['model_name'],
            detector_backend=config['detector_backend'],
            enforce_detection=False
        )
        logger.info("DeepFace model preloaded successfully")
        return True
    except Exception as e:
        logger.warning(f"Failed to preload DeepFace model: {e}")
        return False

def decode_base64_image(face_image_data: str) -> np.ndarray:
    """
    Decode base64 image data to numpy array
    
    Args:
        face_image_data: Base64 encoded image string
        
    Returns:
        numpy array representing the image
        
    Raises:
        ValueError: If image data is invalid
    """
    try:
        # Remove data URL prefix if present
        if ',' in face_image_data:
            face_image_data = face_image_data.split(',')[1]
        
        # Decode base64
        image_data = base64.b64decode(face_image_data)
        
        # Open image with PIL
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert to numpy array
        image_array = np.array(image)
        
        # Validate image dimensions
        if len(image_array.shape) != 3 or image_array.shape[2] != 3:
            raise ValueError("Invalid image format - must be RGB")
        
        return image_array
        
    except Exception as e:
        raise ValueError(f"Failed to decode image: {str(e)}")

def generate_face_embedding(face_image_data: str) -> Tuple[bool, str, Optional[np.ndarray]]:
    """
    Generate face embedding using DeepFace
    
    Args:
        face_image_data: Base64 encoded image string
        
    Returns:
        Tuple of (success, message, embedding_array)
    """
    try:
        from deepface import DeepFace
        
        config = get_deepface_config()
        
        # Decode image
        try:
            image_array = decode_base64_image(face_image_data)
        except ValueError as e:
            return False, str(e), None
        
        logger.info(f"Generating face embedding using {config['model_name']}")
        
        # Generate embedding using DeepFace
        result = DeepFace.represent(
            img_path=image_array,
            model_name=config['model_name'],
            detector_backend=config['detector_backend'],
            enforce_detection=config['enforce_detection']
        )
        
        # DeepFace.represent returns a list of embeddings
        if not result:
            return False, "No face detected in the image", None
        
        if len(result) > 1:
            logger.warning(f"Multiple faces detected ({len(result)}), using the first one")
        
        # Get the first embedding
        embedding = np.array(result[0]['embedding'])
        
        logger.info(f"Face embedding generated successfully, dimension: {embedding.shape}")
        return True, "Face embedding generated successfully", embedding
        
    except ImportError:
        return False, "DeepFace library not available", None
    except Exception as e:
        error_msg = f"Face embedding generation failed: {str(e)}"
        logger.error(error_msg)
        return False, error_msg, None

def calculate_cosine_similarity(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
    """
    Calculate cosine similarity between two face embeddings
    
    Args:
        embedding1: First face embedding
        embedding2: Second face embedding
        
    Returns:
        Cosine similarity score (0-1, higher is more similar)
    """
    try:
        # Normalize embeddings
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        # Calculate cosine similarity
        similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
        
        # Convert to 0-1 range (cosine similarity is -1 to 1)
        similarity = (similarity + 1) / 2
        
        return float(similarity)
        
    except Exception as e:
        logger.error(f"Error calculating cosine similarity: {e}")
        return 0.0

def find_matching_student(face_embedding: np.ndarray, student_embeddings: List[Dict]) -> Tuple[Optional[int], float]:
    """
    Find the best matching student based on face embedding
    
    Args:
        face_embedding: Face embedding to match
        student_embeddings: List of dicts with 'student_id' and 'embedding' keys
        
    Returns:
        Tuple of (student_id, confidence_score) or (None, 0.0) if no match
    """
    config = get_deepface_config()
    threshold = config['similarity_threshold']
    
    best_match_id = None
    best_similarity = 0.0
    
    for student_data in student_embeddings:
        try:
            student_embedding = np.array(student_data['embedding'])
            similarity = calculate_cosine_similarity(face_embedding, student_embedding)
            
            logger.debug(f"Student {student_data['student_id']} similarity: {similarity}")
            
            if similarity > best_similarity and similarity >= threshold:
                best_similarity = similarity
                best_match_id = student_data['student_id']
                
        except Exception as e:
            logger.error(f"Error comparing with student {student_data.get('student_id')}: {e}")
            continue
    
    logger.info(f"Best match: Student {best_match_id} with similarity {best_similarity}")
    return best_match_id, best_similarity

def verify_face_match(known_embedding: np.ndarray, unknown_embedding: np.ndarray) -> Tuple[bool, float]:
    """
    Verify if two face embeddings match
    
    Args:
        known_embedding: Known face embedding
        unknown_embedding: Unknown face embedding to verify
        
    Returns:
        Tuple of (is_match, confidence_score)
    """
    config = get_deepface_config()
    threshold = config['similarity_threshold']
    
    similarity = calculate_cosine_similarity(known_embedding, unknown_embedding)
    is_match = similarity >= threshold
    
    return is_match, similarity

def get_student_embeddings_cache_key() -> str:
    """Get cache key for student embeddings"""
    return "deepface_student_embeddings"

def cache_student_embeddings(embeddings: List[Dict], timeout: int = 3600):
    """
    Cache student embeddings for faster lookup
    
    Args:
        embeddings: List of student embedding data
        timeout: Cache timeout in seconds (default 1 hour)
    """
    try:
        cache_key = get_student_embeddings_cache_key()
        cache.set(cache_key, embeddings, timeout)
        logger.info(f"Cached {len(embeddings)} student embeddings")
    except Exception as e:
        logger.error(f"Failed to cache student embeddings: {e}")

def get_cached_student_embeddings() -> Optional[List[Dict]]:
    """
    Get cached student embeddings
    
    Returns:
        List of student embedding data or None if not cached
    """
    try:
        cache_key = get_student_embeddings_cache_key()
        embeddings = cache.get(cache_key)
        if embeddings:
            logger.info(f"Retrieved {len(embeddings)} student embeddings from cache")
        return embeddings
    except Exception as e:
        logger.error(f"Failed to get cached student embeddings: {e}")
        return None

def invalidate_student_embeddings_cache():
    """Invalidate the student embeddings cache"""
    try:
        cache_key = get_student_embeddings_cache_key()
        cache.delete(cache_key)
        logger.info("Student embeddings cache invalidated")
    except Exception as e:
        logger.error(f"Failed to invalidate student embeddings cache: {e}")

def detect_face_deepface(face_image_data: str) -> Tuple[bool, str]:
    """
    Detect face in image using DeepFace
    
    Args:
        face_image_data: Base64 encoded image string
        
    Returns:
        Tuple of (success, message)
    """
    try:
        from deepface import DeepFace
        
        config = get_deepface_config()
        
        # Decode image
        try:
            image_array = decode_base64_image(face_image_data)
        except ValueError as e:
            return False, str(e)
        
        logger.info("Detecting face using DeepFace")
        
        # Use DeepFace to detect faces
        result = DeepFace.extract_faces(
            img_path=image_array,
            detector_backend=config['detector_backend'],
            enforce_detection=config['enforce_detection']
        )
        
        if not result:
            return False, "No face detected in the image"
        
        if len(result) > 1:
            return False, f"Multiple faces detected ({len(result)}). Please ensure only one face is visible"
        
        return True, "Face detected successfully using DeepFace"
        
    except ImportError:
        return False, "DeepFace library not available"
    except Exception as e:
        error_msg = f"Face detection failed: {str(e)}"
        logger.error(error_msg)
        return False, error_msg

# Initialize model on module import (optional)
try:
    # Only preload if we're in a Django context
    if hasattr(settings, 'INSTALLED_APPS'):
        preload_deepface_model()
except Exception:
    pass  # Ignore errors during module import