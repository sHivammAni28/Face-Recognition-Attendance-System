from django.urls import path
from . import enhanced_views

urlpatterns = [
    # Enhanced registration endpoints
    path('enhanced-register/', enhanced_views.enhanced_register_student, name='enhanced_register_student'),
    path('enhanced-register-face/', enhanced_views.enhanced_register_face, name='enhanced_register_face'),
    
    # Step 1 validation endpoint (for "Next Face Registration" button)
    path('validate-step1/', enhanced_views.validate_step1_credentials, name='validate_step1_credentials'),
    
    # Duplicate check endpoints
    path('check-duplicates/', enhanced_views.check_duplicates, name='check_duplicates'),
    path('check-username-duplicate/', enhanced_views.check_username_duplicate, name='check_username_duplicate'),
    path('check-email-duplicate/', enhanced_views.check_email_duplicate, name='check_email_duplicate'),
    path('check-phone-duplicate/', enhanced_views.check_phone_duplicate, name='check_phone_duplicate'),
    path('check-password-duplicate/', enhanced_views.check_password_duplicate, name='check_password_duplicate'),
    path('check-roll-number-duplicate/', enhanced_views.check_roll_number_duplicate, name='check_roll_number_duplicate'),
    path('check-face-duplicate/', enhanced_views.check_face_duplicate, name='check_face_duplicate'),
    
    # Backward compatibility endpoints
    path('register/', enhanced_views.register_student, name='register_student'),
    path('profile/', enhanced_views.get_student_profile, name='student_profile'),
    path('profile/update/', enhanced_views.update_student_profile, name='update_student_profile'),
    path('register-face/', enhanced_views.register_face, name='register_face'),
]