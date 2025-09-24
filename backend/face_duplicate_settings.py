"""
Face Duplicate Detection Configuration
Add these settings to your Django settings.py file
"""

# Face Duplicate Detection Settings
# =================================

# Similarity Thresholds for different metrics
# Lower values for distance metrics (euclidean, manhattan) mean more similar
# Higher values for similarity metrics (cosine, dot_product) mean more similar

# Euclidean Distance Threshold (recommended: 0.3-0.6)
# Lower values = stricter matching (fewer false positives, more false negatives)
# Higher values = looser matching (more false positives, fewer false negatives)
FACE_EUCLIDEAN_THRESHOLD = 0.4

# Cosine Similarity Threshold (recommended: 0.8-0.95)
# Higher values = stricter matching
FACE_COSINE_THRESHOLD = 0.85

# Manhattan Distance Threshold (recommended: 10-20)
FACE_MANHATTAN_THRESHOLD = 15.0

# Dot Product Similarity Threshold (recommended: 0.8-0.95)
FACE_DOT_PRODUCT_THRESHOLD = 0.85

# Primary metric to use for duplicate detection
# Options: 'euclidean', 'cosine', 'manhattan', 'dot_product'
# Recommended: 'cosine' (most reliable for face embeddings)
FACE_PRIMARY_METRIC = 'cosine'

# Whether to use multiple metrics for validation
# True = Use consensus of multiple metrics (more reliable)
# False = Use only primary metric (faster)
FACE_USE_MULTIPLE_METRICS = True

# Minimum number of metrics that must agree for duplicate detection
# Only used when FACE_USE_MULTIPLE_METRICS = True
# Recommended: 2 (out of 4 metrics)
FACE_MIN_AGREEING_METRICS = 2

# Cache settings for face embeddings
# Cache timeout in seconds (default: 1 hour)
FACE_CACHE_TIMEOUT = 3600

# Logging level for face duplicate detection
# Options: 'DEBUG', 'INFO', 'WARNING', 'ERROR'
FACE_LOG_LEVEL = 'INFO'

# DeepFace Model Configuration
# ============================

# DeepFace model to use for face recognition
# Options: 'VGG-Face', 'Facenet', 'OpenFace', 'DeepFace', 'DeepID', 'ArcFace', 'Dlib'
# Recommended: 'Facenet' (good balance of accuracy and speed)
DEEPFACE_MODEL = 'Facenet'

# Similarity threshold for DeepFace verification
# Used in attendance marking (different from duplicate detection)
DEEPFACE_SIMILARITY_THRESHOLD = 0.8

# Face detector backend
# Options: 'opencv', 'ssd', 'dlib', 'mtcnn', 'retinaface', 'mediapipe'
# Recommended: 'opencv' (fastest) or 'mtcnn' (most accurate)
DEEPFACE_DETECTOR_BACKEND = 'opencv'

# Whether to enforce face detection
# True = Raise error if no face detected
# False = Continue processing even if no face detected
DEEPFACE_ENFORCE_DETECTION = False

# Example usage in settings.py:
# ==============================
"""
# Add to your Django settings.py file:

# Face Duplicate Detection Settings
FACE_EUCLIDEAN_THRESHOLD = 0.4
FACE_COSINE_THRESHOLD = 0.85
FACE_MANHATTAN_THRESHOLD = 15.0
FACE_DOT_PRODUCT_THRESHOLD = 0.85
FACE_PRIMARY_METRIC = 'cosine'
FACE_USE_MULTIPLE_METRICS = True
FACE_MIN_AGREEING_METRICS = 2
FACE_CACHE_TIMEOUT = 3600
FACE_LOG_LEVEL = 'INFO'

# DeepFace Configuration
DEEPFACE_MODEL = 'Facenet'
DEEPFACE_SIMILARITY_THRESHOLD = 0.8
DEEPFACE_DETECTOR_BACKEND = 'opencv'
DEEPFACE_ENFORCE_DETECTION = False
"""

# Threshold Recommendations by Use Case:
# =====================================

# High Security (Banking, Government):
HIGH_SECURITY_SETTINGS = {
    'FACE_EUCLIDEAN_THRESHOLD': 0.3,
    'FACE_COSINE_THRESHOLD': 0.9,
    'FACE_MANHATTAN_THRESHOLD': 12.0,
    'FACE_DOT_PRODUCT_THRESHOLD': 0.9,
    'FACE_USE_MULTIPLE_METRICS': True,
    'FACE_MIN_AGREEING_METRICS': 3,  # Require 3 out of 4 metrics to agree
}

# Balanced (Schools, Offices):
BALANCED_SETTINGS = {
    'FACE_EUCLIDEAN_THRESHOLD': 0.4,
    'FACE_COSINE_THRESHOLD': 0.85,
    'FACE_MANHATTAN_THRESHOLD': 15.0,
    'FACE_DOT_PRODUCT_THRESHOLD': 0.85,
    'FACE_USE_MULTIPLE_METRICS': True,
    'FACE_MIN_AGREEING_METRICS': 2,  # Require 2 out of 4 metrics to agree
}

# Lenient (Social Apps, Low Security):
LENIENT_SETTINGS = {
    'FACE_EUCLIDEAN_THRESHOLD': 0.6,
    'FACE_COSINE_THRESHOLD': 0.75,
    'FACE_MANHATTAN_THRESHOLD': 20.0,
    'FACE_DOT_PRODUCT_THRESHOLD': 0.75,
    'FACE_USE_MULTIPLE_METRICS': False,
    'FACE_MIN_AGREEING_METRICS': 1,  # Use only primary metric
}