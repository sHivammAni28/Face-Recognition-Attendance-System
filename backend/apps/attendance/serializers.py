from rest_framework import serializers
from django.utils import timezone
from .models import Attendance, AttendanceSession, AuditLog
from apps.students.models import Student
import base64
import io
from django.conf import settings

# Try to import face recognition dependencies
try:
    from PIL import Image
    import face_recognition
    import numpy as np
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    # Note: DeepFace is the primary face recognition system, legacy face_recognition is optional
    # Create dummy classes to prevent import errors
    class Image:
        @staticmethod
        def open(*args, **kwargs):
            raise NotImplementedError("PIL not available")
    
    class face_recognition:
        @staticmethod
        def face_encodings(*args, **kwargs):
            raise NotImplementedError("face_recognition not available")
        
        @staticmethod
        def compare_faces(*args, **kwargs):
            raise NotImplementedError("face_recognition not available")
        
        @staticmethod
        def face_distance(*args, **kwargs):
            raise NotImplementedError("face_recognition not available")
    
    import sys
    if 'numpy' not in sys.modules:
        class np:
            @staticmethod
            def array(*args, **kwargs):
                raise NotImplementedError("numpy not available")
    else:
        import numpy as np


class AttendanceSerializer(serializers.ModelSerializer):
    """Serializer for Attendance model"""
    student_name = serializers.ReadOnlyField(source='student.full_name')
    student_roll = serializers.ReadOnlyField(source='student.roll_number')
    student_class = serializers.ReadOnlyField(source='student.student_class')
    marked_by_username = serializers.SerializerMethodField()
    
    def get_marked_by_username(self, obj):
        """Get username of the user who marked attendance"""
        return obj.marked_by.username if obj.marked_by else 'System'
    
    class Meta:
        model = Attendance
        fields = [
            'id', 'student', 'student_name', 'student_roll', 'student_class',
            'date', 'time', 'session', 'status', 'marked_by', 'marked_by_username',
            'is_manual', 'created_at'
        ]
        read_only_fields = ['id', 'time', 'created_at']
    
    def to_representation(self, instance):
        """Custom representation to handle missing fields gracefully"""
        try:
            data = super().to_representation(instance)
        except Exception as e:
            # If there's an error with the base representation, create a minimal one
            data = {
                'id': instance.id,
                'student': instance.student.id,
                'student_name': instance.student.full_name,
                'student_roll': instance.student.roll_number,
                'student_class': instance.student.student_class,
                'date': str(instance.date),
                'time': str(instance.time),
                'session': instance.session,
                'status': instance.status,
                'marked_by': instance.marked_by.id if instance.marked_by else None,
                'marked_by_username': instance.marked_by.username if instance.marked_by else 'System',
                'is_manual': getattr(instance, 'is_manual', True),
                'created_at': str(instance.created_at),
            }
        
        # Add is_face_recognition field if it exists
        try:
            data['is_face_recognition'] = instance.is_face_recognition
        except AttributeError:
            data['is_face_recognition'] = False
        
        return data


class FaceRecognitionAttendanceSerializer(serializers.Serializer):
    """Serializer for face recognition based attendance marking"""
    face_image_data = serializers.CharField(write_only=True)  # Base64 encoded image
    session = serializers.ChoiceField(choices=Attendance.SESSION_CHOICES, default='morning')
    
    def validate(self, attrs):
        """Validate face image and perform recognition"""
        if not FACE_RECOGNITION_AVAILABLE:
            raise serializers.ValidationError("Face recognition is not available on this system. Please use manual attendance marking.")
        
        face_image_data = attrs['face_image_data']
        session = attrs['session']
        
        try:
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
            
            # Compare with all registered students
            detected_encoding = face_encodings[0]
            matched_student = None
            
            students = Student.objects.filter(is_face_registered=True)
            for student in students:
                stored_encoding = student.get_face_encoding()
                if stored_encoding is not None:
                    # Compare faces
                    matches = face_recognition.compare_faces(
                        [stored_encoding], 
                        detected_encoding, 
                        tolerance=getattr(settings, 'FACE_RECOGNITION_TOLERANCE', 0.6)
                    )
                    
                    if matches[0]:
                        # Calculate face distance for better accuracy
                        face_distances = face_recognition.face_distance([stored_encoding], detected_encoding)
                        if face_distances[0] <= getattr(settings, 'MAX_FACE_DISTANCE', 0.6):
                            matched_student = student
                            break
            
            if not matched_student:
                raise serializers.ValidationError("Face not recognized. Please register first or try again.")
            
            # Check if attendance already marked for today and session
            today = timezone.now().date()
            existing_attendance = Attendance.objects.filter(
                student=matched_student,
                date=today,
                session=session
            ).first()
            
            if existing_attendance:
                raise serializers.ValidationError("Attendance already marked for today!")
            
            attrs['matched_student'] = matched_student
            return attrs
            
        except Exception as e:
            if isinstance(e, serializers.ValidationError):
                raise e
            raise serializers.ValidationError(f"Face recognition error: {str(e)}")
    
    def create(self, validated_data):
        """Create attendance record"""
        student = validated_data['matched_student']
        session = validated_data['session']
        
        # Determine if attendance is late
        current_time = timezone.now().time()
        status = 'present'
        
        try:
            session_obj = AttendanceSession.objects.get(name=session, is_active=True)
            if session_obj.is_late(current_time):
                status = 'late'
        except AttendanceSession.DoesNotExist:
            # If no session configuration, default to present
            pass
        
        # Create attendance record
        attendance = Attendance.objects.create(
            student=student,
            session=session,
            status=status,
            is_manual=False
        )
        
        return attendance


class ManualAttendanceSerializer(serializers.ModelSerializer):
    """Serializer for manual attendance marking by admin"""
    
    class Meta:
        model = Attendance
        fields = ['student', 'date', 'session', 'status']
    
    def validate(self, attrs):
        """Validate manual attendance data"""
        student = attrs['student']
        date = attrs['date']
        session = attrs['session']
        
        # Check if attendance already exists
        existing_attendance = Attendance.objects.filter(
            student=student,
            date=date,
            session=session
        ).first()
        
        if existing_attendance:
            raise serializers.ValidationError("Attendance already exists for this student, date, and session")
        
        return attrs
    
    def create(self, validated_data):
        """Create manual attendance record"""
        validated_data['is_manual'] = True
        validated_data['marked_by'] = self.context['request'].user
        return super().create(validated_data)


class AttendanceSessionSerializer(serializers.ModelSerializer):
    """Serializer for AttendanceSession model"""
    
    class Meta:
        model = AttendanceSession
        fields = '__all__'


class AttendanceStatsSerializer(serializers.Serializer):
    """Serializer for attendance statistics"""
    total_classes = serializers.IntegerField(read_only=True)
    present_count = serializers.IntegerField(read_only=True)
    late_count = serializers.IntegerField(read_only=True)
    absent_count = serializers.IntegerField(read_only=True)
    attendance_percentage = serializers.FloatField(read_only=True)
    
    def to_representation(self, instance):
        """Calculate attendance statistics"""
        student = instance
        
        # Get all attendance records for the student
        attendances = Attendance.objects.filter(student=student)
        
        total_classes = attendances.count()
        present_count = attendances.filter(status='present').count()
        late_count = attendances.filter(status='late').count()
        absent_count = attendances.filter(status='absent').count()
        
        # Calculate attendance percentage
        if total_classes > 0:
            attendance_percentage = ((present_count + late_count) / total_classes) * 100
        else:
            attendance_percentage = 0.0
        
        return {
            'total_classes': total_classes,
            'present_count': present_count,
            'late_count': late_count,
            'absent_count': absent_count,
            'attendance_percentage': round(attendance_percentage, 2)
        }


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for AuditLog model"""
    username = serializers.ReadOnlyField(source='user.username')
    student_name = serializers.ReadOnlyField(source='student.full_name')
    student_roll = serializers.ReadOnlyField(source='student.roll_number')
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'username', 'action', 'student_name', 'student_roll',
            'details', 'timestamp', 'ip_address'
        ]