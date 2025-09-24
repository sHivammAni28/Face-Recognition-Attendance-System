"""
Simple mock face recognition that always succeeds
This allows the system to work without actual face recognition libraries
"""

def detect_face_in_image(face_image_data):
    """
    Mock face detection that always succeeds
    This allows testing the attendance system without face recognition libraries
    """
    try:
        import base64
        from PIL import Image
        import io
        
        # Basic validation - check if we have valid image data
        if not face_image_data:
            return False, 'No image data provided'
        
        # Try to decode the image
        if ',' in face_image_data:
            face_image_data = face_image_data.split(',')[1]
        
        try:
            image_data = base64.b64decode(face_image_data)
            image = Image.open(io.BytesIO(image_data))
            
            # Basic image validation
            if image.width < 50 or image.height < 50:
                return False, 'Image too small'
            
            # Mock success - in a real system, this would do actual face detection
            return True, 'Face detected successfully (mock detection)'
            
        except Exception as e:
            return False, f'Invalid image data: {str(e)}'
            
    except Exception as e:
        return False, f'Face detection error: {str(e)}'