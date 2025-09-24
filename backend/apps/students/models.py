from django.db import models
from django.conf import settings
import json

# Check if Pillow is available for ImageField
try:
    from PIL import Image
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False


class Student(models.Model):
    """Student model with face encoding storage"""
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile')
    roll_number = models.CharField(max_length=20, unique=True)
    student_class = models.CharField(max_length=50, default='General')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    face_encoding = models.TextField(blank=True, null=True)  # Store as JSON string
    # Use TextField instead of ImageField to avoid Pillow dependency
    face_image_data = models.TextField(blank=True, null=True)  # Store base64 image data
    is_face_registered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['roll_number']
    
    def __str__(self):
        return f"{self.roll_number} - {self.user.get_full_name() or self.user.username}"
    
    def set_face_encoding(self, encoding_array):
        """Store face encoding as JSON string"""
        if encoding_array is not None:
            self.face_encoding = json.dumps(encoding_array.tolist())
            self.is_face_registered = True
        else:
            self.face_encoding = None
            self.is_face_registered = False
    
    def get_face_encoding(self):
        """Retrieve face encoding as numpy array"""
        if self.face_encoding:
            try:
                import numpy as np
                return np.array(json.loads(self.face_encoding))
            except ImportError:
                print("Warning: numpy not available, cannot retrieve face encoding")
                return None
        return None
    
    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username
    
    @property
    def email(self):
        return self.user.email
    
    @property
    def student_name(self):
        return self.full_name
    
    @property
    def student_roll(self):
        return self.roll_number