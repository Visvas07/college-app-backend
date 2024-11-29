import json
from django.shortcuts import render
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse,JsonResponse
from rest_framework.views import APIView
from rest_framework import generics,permissions,status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from .serializers import TeacherSerializer,StudentSerializer,SubjectSerializer,EnrollmentSerializer,StudentDashboardSerializer,TeacherDashboardSerializer
from . import models

def start(request):
    template = loader.get_template("index.html")
    return HttpResponse(template.render())

class TeacherList(generics.ListCreateAPIView):
    queryset=models.Teacher.objects.all()
    serializer_class=TeacherSerializer
    #permission_classes=[permissions.IsAuthenticated]

class SubjectList(generics.ListCreateAPIView):
    queryset=models.Subject.objects.all()
    serializer_class=SubjectSerializer

    def get_queryset(self):
        qs=super().get_queryset()
        if 'result' in self.request.GET:
            limit=int(self.request.GET['result'])
            qs=models.Subject.objects.all().order_by('id')[:limit]
        return qs

class SubjectDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset=models.Subject.objects.all()
    parser_classes=(MultiPartParser,)
    serializer_class=SubjectSerializer
    lookup_field = 'pk'

class TeacherDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset=models.Teacher.objects.all()
    serializer_class=TeacherSerializer
    lookup_field = 'pk'
    #permission_classes=[permissions.IsAuthenticated]

class StudentList(generics.ListCreateAPIView):
    queryset=models.Student.objects.all()
    serializer_class=StudentSerializer
   #permission_classes=[permissions.IsAuthenticated]

class StudentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset=models.Student.objects.all()
    serializer_class=StudentSerializer
    lookup_field = 'pk'
    #permission_classes=[permissions.IsAuthenticated]
    
class TeacherCreateAPIView(generics.CreateAPIView):
    queryset=models.Teacher.objects.all()
    parser_classes=(MultiPartParser,)
    serializer_class=TeacherSerializer

class StudentCreateAPIView(generics.CreateAPIView):
    queryset=models.Student.objects.all()
    parser_classes=(MultiPartParser,)
    serializer_class=StudentSerializer

class TeacherCourseList(generics.ListAPIView):
    serializer_class=SubjectSerializer
    def get_queryset(self):
        teacher_id=self.kwargs['teacher_id']
        teacher = models.Teacher.objects.get(pk=teacher_id)
        return models.Subject.objects.filter(assigned_teachers=teacher)

class SubjectTeacherList(generics.ListAPIView):
    serializer_class=TeacherSerializer
    def get_queryset(self):
        subject_id=self.kwargs['subject_id']
        subject = models.Subject.objects.get(pk=subject_id)
        return subject.assigned_teachers.all()
    
class StudentEnrollmentView(generics.CreateAPIView):
    queryset = models.Enrollment.objects.all()
    serializer_class = EnrollmentSerializer

    def create(self, request, *args, **kwargs):
        # Extract student_id and subject_id from URL path parameters
        student_id = kwargs.get('student_id')
        subject_id = kwargs.get('subject_id')

        # Debugging: Log extracted parameters
        print(f"Student ID: {student_id}, Subject ID: {subject_id}")

        # Validate student and subject
        try:
            student = models.Student.objects.get(id=student_id)
        except models.Student.DoesNotExist:
            return Response({"student": "Student does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            subject = models.Subject.objects.get(id=subject_id)
        except models.Subject.DoesNotExist:
            return Response({"subject": "Subject does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure that the student is not already enrolled in the subject
        if models.Enrollment.objects.filter(student=student, subject=subject).exists():
            return Response({"student": "Student is already enrolled in this subject."}, status=status.HTTP_400_BAD_REQUEST)

        # Save the enrollment
        enrollment = models.Enrollment.objects.create(student=student, subject=subject)
        
        # Serialize and return the response
        serializer = self.get_serializer(enrollment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class EnrolledSubjectList(generics.ListAPIView):
    queryset=models.Enrollment.objects.all()
    serializer_class=EnrollmentSerializer

    def get_queryset(self):
        if 'subject_id' in self.kwargs:
            subject_id=self.kwargs['subject_id']
            subject=models.Subject.objects.get(pk=subject_id)
            return models.Enrollment.objects.filter(subject=subject)
        elif 'teacher_id' in self.kwargs:
            teacher_id=self.kwargs['teacher_id']
            teacher=models.Teacher.objects.get(pk=teacher_id)
            return models.Enrollment.objects.filter(subject__assigned_teachers=teacher).distinct()
        elif 'student_id' in self.kwargs:
            student_id=self.kwargs['student_id']
            student=models.Student.objects.get(pk=student_id)
            return models.Enrollment.objects.filter(student=student).distinct()
            

class TeacherDashboard(generics.RetrieveAPIView):
    queryset=models.Teacher.objects.all()
    serializer_class=TeacherDashboardSerializer

class StudentDashboard(generics.RetrieveAPIView):
    queryset=models.Student.objects.all()
    serializer_class=StudentDashboardSerializer

    

@csrf_exempt
def teacher_login(request):
    username = request.POST['username']
    password = request.POST['password']
    try:
        teacher_data=models.Teacher.objects.get(username=username,password=password)
    except models.Teacher.DoesNotExist:
        return JsonResponse({'status':'error','message':'Invalid Credentials'})
    if teacher_data:
        return JsonResponse({'bool':True,'teacher_id':teacher_data.id})
    else:
        return JsonResponse({'bool':False})
    
@csrf_exempt
def student_login(request):
    username=request.POST['username']
    password=request.POST['password']
    try:
        student_data=models.Student.objects.get(username=username,password=password)
    except models.Student.DoesNotExist:
        return JsonResponse({'status':'error','message':'Invalid Credentials'})
    if student_data:
        return JsonResponse({'bool':True,'student_id':student_data.id})
    else:
        return JsonResponse({'bool':False})
    
@csrf_exempt
def teacher_change_password(request, teacher_id):
    if request.method == "PATCH":
        try:
            teacher = models.Teacher.objects.get(id=teacher_id)
        except models.Teacher.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Teacher not found"}, status=404)

        data = json.loads(request.body)
        old_password = data.get("oldpassword")
        new_password = data.get("newpassword")
        confirm_password = data.get("confirmpassword")

        if not old_password or not new_password or not confirm_password:
            return JsonResponse({"status": "error", "message": "All fields are required"}, status=400)

        if not teacher.password == old_password:
            return JsonResponse({"status": "error", "message": "Old password is incorrect"}, status=400)

        if new_password != confirm_password:
            return JsonResponse({"status": "error", "message": "Passwords do not match"}, status=400)

        teacher.password = new_password
        teacher.save()
        return JsonResponse({"status": "success", "message": "Password updated successfully"})

    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)


@csrf_exempt
def student_change_password(request, student_id):
    if request.method == "PATCH":
        try:
            student = models.Student.objects.get(id=student_id)
        except models.Student.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Teacher not found"}, status=404)

        data = json.loads(request.body)
        old_password = data.get("oldpassword")
        new_password = data.get("newpassword")
        confirm_password = data.get("confirmpassword")

        if not old_password or not new_password or not confirm_password:
            return JsonResponse({"status": "error", "message": "All fields are required"}, status=400)

        if not student.password == old_password:
            return JsonResponse({"status": "error", "message": "Old password is incorrect"}, status=400)

        if new_password != confirm_password:
            return JsonResponse({"status": "error", "message": "Passwords do not match"}, status=400)

        student.password = new_password
        student.save()
        return JsonResponse({"status": "success", "message": "Password updated successfully"})

    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)

@csrf_exempt
def fetch_enroll_status(request,student_id,subject_id):
    student_data=models.Student.objects.filter(id=student_id).first()
    course_data=models.Subject.objects.filter(id=subject_id).first()
    enroll_status=models.Enrollment.objects.filter(subject=course_data,student=student_data).count()
    if enroll_status:
        return JsonResponse({'bool':True})
    else:
        return JsonResponse({'bool':False})
        

