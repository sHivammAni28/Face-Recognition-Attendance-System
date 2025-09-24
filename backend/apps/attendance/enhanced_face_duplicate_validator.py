"""
Enhanced Face Duplicate Validation System
Implements robust face duplicate detection using multiple similarity metrics
"""
import numpy as np
import logging
from typing import Tuple, Optional, List, Dict, Any
from django.conf import settings
from django.core.cache import cache
from apps.students.models import Student
from .deepface_utils import generate_face_embedding, calculate_cosine_similarity

logger = logging.getLogger(__name__)


class FaceSimilarityMetrics:
    """Class containing various face similarity calculation methods"""
    
    @staticmethod
    def euclidean_distance(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate Euclidean distance between two face embeddings
        
        Args:
            embedding1: First face embedding
            embedding2: Second face embedding
            
        Returns:
            Euclidean distance (lower values indicate higher similarity)
        """
        try:
            distance = np.linalg.norm(embedding1 - embedding2)
            return float(distance)
        except Exception as e:
            logger.error(f"Error calculating Euclidean distance: {e}")
            return float('inf')
    
    @staticmethod
    def cosine_similarity(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two face embeddings
        
        Args:
            embedding1: First face embedding
            embedding2: Second face embedding
            
        Returns:
            Cosine similarity score (0-1, higher values indicate higher similarity)
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
    
    @staticmethod
    def manhattan_distance(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate Manhattan distance between two face embeddings
        
        Args:
            embedding1: First face embedding
            embedding2: Second face embedding
            
        Returns:
            Manhattan distance (lower values indicate higher similarity)
        """
        try:
            distance = np.sum(np.abs(embedding1 - embedding2))
            return float(distance)
        except Exception as e:
            logger.error(f"Error calculating Manhattan distance: {e}")
            return float('inf')
    
    @staticmethod
    def dot_product_similarity(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate dot product similarity between two face embeddings
        
        Args:
            embedding1: First face embedding
            embedding2: Second face embedding
            
        Returns:
            Dot product similarity (higher values indicate higher similarity)
        """
        try:
            # Normalize embeddings first
            norm1 = embedding1 / np.linalg.norm(embedding1)
            norm2 = embedding2 / np.linalg.norm(embedding2)
            
            similarity = np.dot(norm1, norm2)
            
            # Convert to 0-1 range
            similarity = (similarity + 1) / 2
            
            return float(similarity)
        except Exception as e:
            logger.error(f"Error calculating dot product similarity: {e}")
            return 0.0


class FaceDuplicateConfig:
    """Configuration class for face duplicate detection"""
    
    def __init__(self):
        self.euclidean_threshold = getattr(settings, 'FACE_EUCLIDEAN_THRESHOLD', 0.4)
        self.cosine_threshold = getattr(settings, 'FACE_COSINE_THRESHOLD', 0.85)
        self.manhattan_threshold = getattr(settings, 'FACE_MANHATTAN_THRESHOLD', 15.0)
        self.dot_product_threshold = getattr(settings, 'FACE_DOT_PRODUCT_THRESHOLD', 0.85)
        
        # Primary metric to use for duplicate detection
        self.primary_metric = getattr(settings, 'FACE_PRIMARY_METRIC', 'cosine')
        
        # Whether to use multiple metrics for validation
        self.use_multiple_metrics = getattr(settings, 'FACE_USE_MULTIPLE_METRICS', True)
        
        # Minimum number of metrics that must agree for duplicate detection
        self.min_agreeing_metrics = getattr(settings, 'FACE_MIN_AGREEING_METRICS', 2)
        
        # Cache settings
        self.cache_timeout = getattr(settings, 'FACE_CACHE_TIMEOUT', 3600)  # 1 hour
        
        # Logging level for face duplicate detection
        self.log_level = getattr(settings, 'FACE_LOG_LEVEL', 'INFO')
    
    def get_threshold(self, metric: str) -> float:
        """Get threshold for a specific metric"""
        thresholds = {
            'euclidean': self.euclidean_threshold,
            'cosine': self.cosine_threshold,
            'manhattan': self.manhattan_threshold,
            'dot_product': self.dot_product_threshold
        }
        return thresholds.get(metric, 0.5)


class EnhancedFaceDuplicateValidator:
    """Enhanced face duplicate validator with multiple similarity metrics"""
    
    def __init__(self):
        self.config = FaceDuplicateConfig()
        self.metrics = FaceSimilarityMetrics()
        self.cache_key_prefix = "face_embeddings_"
    
    def _get_all_face_embeddings(self, exclude_student_id: Optional[int] = None) -> List[Dict]:
        """
        Get all face embeddings from database with caching
        
        Args:
            exclude_student_id: Student ID to exclude from comparison
            
        Returns:
            List of dictionaries containing student info and embeddings
        """
        cache_key = f"{self.cache_key_prefix}all"
        if exclude_student_id:
            cache_key += f"_exclude_{exclude_student_id}"
        
        # Try to get from cache first
        cached_embeddings = cache.get(cache_key)
        if cached_embeddings:
            logger.debug(f"Retrieved {len(cached_embeddings)} face embeddings from cache")
            return cached_embeddings
        
        # Get from database
        students_query = Student.objects.filter(is_face_registered=True)
        if exclude_student_id:
            students_query = students_query.exclude(id=exclude_student_id)
        
        embeddings = []
        for student in students_query:
            face_encoding = student.get_face_encoding()
            if face_encoding is not None:
                embeddings.append({
                    'student_id': student.id,
                    'student_name': student.full_name,
                    'roll_number': student.roll_number,
                    'email': student.user.email,
                    'embedding': face_encoding
                })
        
        # Cache the results
        cache.set(cache_key, embeddings, self.config.cache_timeout)
        logger.info(f"Cached {len(embeddings)} face embeddings")
        
        return embeddings
    
    def _calculate_all_similarities(self, new_embedding: np.ndarray, stored_embedding: np.ndarray) -> Dict[str, float]:
        """
        Calculate all similarity metrics between two embeddings
        
        Args:
            new_embedding: New face embedding
            stored_embedding: Stored face embedding
            
        Returns:
            Dictionary of similarity scores for each metric
        """
        similarities = {}
        
        try:
            # Euclidean distance (lower is more similar)
            euclidean_dist = self.metrics.euclidean_distance(new_embedding, stored_embedding)
            similarities['euclidean'] = euclidean_dist
            
            # Cosine similarity (higher is more similar)
            cosine_sim = self.metrics.cosine_similarity(new_embedding, stored_embedding)
            similarities['cosine'] = cosine_sim
            
            # Manhattan distance (lower is more similar)
            manhattan_dist = self.metrics.manhattan_distance(new_embedding, stored_embedding)
            similarities['manhattan'] = manhattan_dist
            
            # Dot product similarity (higher is more similar)
            dot_product_sim = self.metrics.dot_product_similarity(new_embedding, stored_embedding)
            similarities['dot_product'] = dot_product_sim
            
        except Exception as e:
            logger.error(f"Error calculating similarities: {e}")
        
        return similarities
    
    def _is_duplicate_by_metric(self, similarities: Dict[str, float], metric: str) -> bool:
        """
        Check if faces are duplicates based on a specific metric
        
        Args:
            similarities: Dictionary of similarity scores
            metric: Metric name to check
            
        Returns:
            True if faces are considered duplicates based on this metric
        """
        if metric not in similarities:
            return False
        
        threshold = self.config.get_threshold(metric)
        score = similarities[metric]
        
        # For distance metrics (euclidean, manhattan), lower values indicate similarity
        if metric in ['euclidean', 'manhattan']:
            return score <= threshold
        
        # For similarity metrics (cosine, dot_product), higher values indicate similarity
        else:
            return score >= threshold
    
    def _evaluate_duplicate_consensus(self, similarities: Dict[str, float]) -> Tuple[bool, Dict[str, Any]]:
        """
        Evaluate if faces are duplicates based on multiple metrics consensus
        
        Args:
            similarities: Dictionary of similarity scores
            
        Returns:
            Tuple of (is_duplicate, detailed_results)
        """
        results = {
            'similarities': similarities,
            'metric_votes': {},
            'primary_metric_result': False,
            'consensus_result': False,
            'agreeing_metrics': 0
        }
        
        # Check each metric
        agreeing_metrics = 0
        for metric in ['euclidean', 'cosine', 'manhattan', 'dot_product']:
            if metric in similarities:
                is_duplicate = self._is_duplicate_by_metric(similarities, metric)
                results['metric_votes'][metric] = is_duplicate
                
                if is_duplicate:
                    agreeing_metrics += 1
                
                # Check primary metric
                if metric == self.config.primary_metric:
                    results['primary_metric_result'] = is_duplicate
        
        results['agreeing_metrics'] = agreeing_metrics
        
        # Determine final result
        if self.config.use_multiple_metrics:
            # Use consensus of multiple metrics
            results['consensus_result'] = agreeing_metrics >= self.config.min_agreeing_metrics
            is_duplicate = results['consensus_result']
        else:
            # Use only primary metric
            is_duplicate = results['primary_metric_result']
        
        return is_duplicate, results
    
    def check_face_duplicate(self, face_image_data: str, exclude_student_id: Optional[int] = None) -> Tuple[bool, Optional[Dict]]:
        """
        Check if a face is already registered with another account
        
        Args:
            face_image_data: Base64 encoded face image
            exclude_student_id: Student ID to exclude from comparison
            
        Returns:
            Tuple of (is_duplicate, duplicate_info)
        """
        try:
            # Generate embedding for the new face
            success, message, new_embedding = generate_face_embedding(face_image_data)
            
            if not success or new_embedding is None:
                logger.error(f"Failed to generate embedding: {message}")
                return False, None
            
            logger.info(f"Generated embedding with {len(new_embedding)} dimensions")
            
            # Get all stored face embeddings
            stored_embeddings = self._get_all_face_embeddings(exclude_student_id)
            
            if not stored_embeddings:
                logger.info("No stored face embeddings found")
                return False, None
            
            logger.info(f"Comparing against {len(stored_embeddings)} stored faces")
            
            # Find the best match
            best_match = None
            best_confidence = 0.0
            best_results = None
            
            for student_data in stored_embeddings:
                try:
                    stored_embedding = np.array(student_data['embedding'])
                    
                    # Calculate all similarity metrics
                    similarities = self._calculate_all_similarities(new_embedding, stored_embedding)
                    
                    # Evaluate if this is a duplicate
                    is_duplicate, detailed_results = self._evaluate_duplicate_consensus(similarities)
                    
                    if is_duplicate:
                        # Use primary metric for confidence score
                        primary_metric = self.config.primary_metric
                        if primary_metric in similarities:
                            if primary_metric in ['euclidean', 'manhattan']:
                                # For distance metrics, convert to similarity (inverse)
                                confidence = 1.0 / (1.0 + similarities[primary_metric])
                            else:
                                # For similarity metrics, use directly
                                confidence = similarities[primary_metric]
                        else:
                            confidence = 0.5  # Default confidence
                        
                        # Keep track of best match
                        if confidence > best_confidence:
                            best_confidence = confidence
                            best_match = student_data
                            best_results = detailed_results
                            
                            logger.info(
                                f"Potential duplicate found: Student {student_data['roll_number']} "
                                f"with confidence {confidence:.3f}"
                            )
                            logger.debug(f"Similarity details: {similarities}")
                
                except Exception as e:
                    logger.error(f"Error comparing with student {student_data.get('student_id')}: {e}")
                    continue
            
            # Return best match if found
            if best_match:
                duplicate_info = {
                    'student_id': best_match['student_id'],
                    'student_name': best_match['student_name'],
                    'roll_number': best_match['roll_number'],
                    'email': best_match['email'],
                    'confidence': best_confidence,
                    'similarity_details': best_results['similarities'],
                    'metric_votes': best_results['metric_votes'],
                    'agreeing_metrics': best_results['agreeing_metrics']
                }
                
                logger.warning(
                    f"Face duplicate detected: Student {best_match['roll_number']} "
                    f"({best_match['student_name']}) with confidence {best_confidence:.3f}"
                )
                
                return True, duplicate_info
            
            logger.info("No face duplicates found")
            return False, None
            
        except Exception as e:
            logger.error(f"Error in face duplicate check: {e}")
            return False, None
    
    def invalidate_cache(self):
        """Invalidate all face embedding caches"""
        try:
            # For now, we'll just delete the main cache key
            main_cache_key = f"{self.cache_key_prefix}all"
            cache.delete(main_cache_key)
            
            logger.info("Face embedding cache invalidated")
        except Exception as e:
            logger.error(f"Error invalidating face embedding cache: {e}")
    
    def get_similarity_report(self, face_image_data: str, exclude_student_id: Optional[int] = None) -> Dict:
        """
        Get detailed similarity report for a face against all stored faces
        
        Args:
            face_image_data: Base64 encoded face image
            exclude_student_id: Student ID to exclude from comparison
            
        Returns:
            Detailed similarity report
        """
        try:
            # Generate embedding for the new face
            success, message, new_embedding = generate_face_embedding(face_image_data)
            
            if not success or new_embedding is None:
                return {'error': f'Failed to generate embedding: {message}'}
            
            # Get all stored face embeddings
            stored_embeddings = self._get_all_face_embeddings(exclude_student_id)
            
            report = {
                'total_comparisons': len(stored_embeddings),
                'config': {
                    'primary_metric': self.config.primary_metric,
                    'use_multiple_metrics': self.config.use_multiple_metrics,
                    'min_agreeing_metrics': self.config.min_agreeing_metrics,
                    'thresholds': {
                        'euclidean': self.config.euclidean_threshold,
                        'cosine': self.config.cosine_threshold,
                        'manhattan': self.config.manhattan_threshold,
                        'dot_product': self.config.dot_product_threshold
                    }
                },
                'comparisons': []
            }
            
            for student_data in stored_embeddings:
                try:
                    stored_embedding = np.array(student_data['embedding'])
                    
                    # Calculate all similarity metrics
                    similarities = self._calculate_all_similarities(new_embedding, stored_embedding)
                    
                    # Evaluate if this is a duplicate
                    is_duplicate, detailed_results = self._evaluate_duplicate_consensus(similarities)
                    
                    comparison = {
                        'student_id': student_data['student_id'],
                        'student_name': student_data['student_name'],
                        'roll_number': student_data['roll_number'],
                        'is_duplicate': is_duplicate,
                        'similarities': similarities,
                        'metric_votes': detailed_results['metric_votes'],
                        'agreeing_metrics': detailed_results['agreeing_metrics']
                    }
                    
                    report['comparisons'].append(comparison)
                    
                except Exception as e:
                    logger.error(f"Error in similarity report for student {student_data.get('student_id')}: {e}")
                    continue
            
            # Sort by primary metric similarity
            primary_metric = self.config.primary_metric
            if primary_metric in ['euclidean', 'manhattan']:
                # For distance metrics, sort ascending (lower is better)
                report['comparisons'].sort(key=lambda x: x['similarities'].get(primary_metric, float('inf')))
            else:
                # For similarity metrics, sort descending (higher is better)
                report['comparisons'].sort(key=lambda x: x['similarities'].get(primary_metric, 0), reverse=True)
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating similarity report: {e}")
            return {'error': f'Failed to generate similarity report: {str(e)}'}


# Global instance
enhanced_face_validator = EnhancedFaceDuplicateValidator()