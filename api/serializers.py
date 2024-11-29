from httpcore import Response
from rest_framework import serializers
from . import models

class SubjectSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    total_students=serializers.SerializerMethodField()
    class Meta:
        model = models.Subject
        fields='__all__'
    
    def get_image_url(self,obj):
        return obj.course_image.url if obj.course_image else None
    
    def get_total_students(self,obj):
        return obj.total_enrolled_students()

    def to_representation(self, instance):
        representation= super().to_representation(instance)
        representation.pop("course_image")
        return representation


class TeacherSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()  
    subject_details = SubjectSerializer(source='subject', read_only=True)
    total_courses = serializers.SerializerMethodField()
    total_students = serializers.SerializerMethodField()

    class Meta:
        model = models.Teacher
        fields = [
            'id', 'first_name', 'last_name', 'username', 'email', 'qualification',
            'mobile_no', 'gender', 'image_url', 'subject_details',
            'total_courses', 'total_students'
        ]

    def get_image_url(self, obj):
        return obj.image_url  

    def get_total_courses(self, obj):
        return obj.total_courses()  

    def get_total_students(self, obj):
        return obj.total_students()  
    
class TeacherDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model=models.Teacher
        fields=['total_courses','total_students']

class StudentDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model=models.Student
        fields=['total_courses','total_teachers']


class StudentSerializer(serializers.ModelSerializer):
    image_url = serializers.ReadOnlyField() 
    total_courses = serializers.SerializerMethodField()
    total_teachers=serializers.SerializerMethodField()

    class Meta:
        model = models.Student
        fields = [
            'id', 'first_name', 'last_name', 'username','password', 'email', 'degree',
            'mobile_no', 'gender', 'image_url','dob','blood_group','address'
            , 'total_teachers','total_courses'
        ]
    
    def get_total_teachers(self,obj):
        return obj.total_teachers()

    def get_total_courses(self,obj):
        return obj.total_courses()
    
    def get_image_url(self,obj):
        return obj.image_url


class EnrollmentSerializer(serializers.ModelSerializer):
    teacher_details = serializers.SerializerMethodField()

    class Meta:
        model = models.Enrollment
        fields = ['id', 'subject', 'student', 'enrollment_date', 'teacher_details']
        depth = 2

    def get_teacher_details(self, obj):
        if obj.subject and obj.subject.assigned_teachers.exists():
            teacher = obj.subject.assigned_teachers.first()
            return TeacherSerializer(teacher).data
        return None

    def validate(self, data):
        # Ensure student and subject are provided (although we are now getting them from the URL)
        if not data.get('student'):
            raise serializers.ValidationError({"student": "Student is required."})
        if not data.get('subject'):
            raise serializers.ValidationError({"subject": "Subject is required."})
        return data


