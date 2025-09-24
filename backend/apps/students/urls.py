from django.urls import path
from . import views
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
    path('get-face-similarity-report/', enhanced_views.get_face_similarity_report, name='get_face_similarity_report'),
    
    # Original endpoints (backward compatibility)
    path('register/', views.register_student, name='register_student'),
    path('profile/', views.get_student_profile, name='student_profile'),
    path('profile/update/', views.update_student_profile, name='update_student_profile'),
    path('register-face/', views.register_face, name='register_face'),
    
    # Admin-only endpoints
    path('', views.list_students, name='list_students'),
    path('<int:student_id>/', views.get_student_detail, name='student_detail'),
    path('<int:student_id>/update/', views.update_student, name='update_student'),
    path('<int:student_id>/delete/', views.delete_student, name='delete_student'),
    path('classes/', views.get_classes, name='get_classes'),
]