from django.utils import timezone
import random
from django.db import models
from cloudinary.models import CloudinaryField
# Create your models here.

class Subject(models.Model):
    name=models.CharField(max_length=255)
    description=models.TextField(max_length=500,default="Default Description")
    course_image=CloudinaryField("image",null=True,blank=True)

    def total_enrolled_students(self):
        total_enrolled_students=Enrollment.objects.filter(subject=self).count()
        return total_enrolled_students
    
    def __str__(self):
        return f"{self.name}"

    @property
    def image_url(self):
        if self.course_image:
            return(f"https://res.cloudinary.com/drzvymfnv/{self.course_image}") 
        return None


class Teacher(models.Model):
    first_name=models.CharField(max_length=200)
    last_name=models.CharField(max_length=200)
    username=models.CharField(max_length=200,unique=True,blank=True)
    email=models.EmailField(unique=True,max_length=100)
    password=models.CharField(max_length=200)
    qualification=models.CharField(max_length=200)
    mobile_no=models.CharField(max_length=15)
    GENDERS = {"M":"Male","F":"Female"}
    gender=models.CharField(max_length=1,choices=GENDERS,default="S")
    profile_photo=CloudinaryField("image")
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_teachers')
    
    def total_courses(self):
        total_courses=Subject.objects.filter(assigned_teachers=self).count()
        return total_courses
    
    def total_students(self):
        return Enrollment.objects.filter(subject__assigned_teachers=self).values("student").distinct().count()
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def image_url(self):
        if self.profile_photo:
            return(f"https://res.cloudinary.com/drzvymfnv/{self.profile_photo}") 
        return None


class Student(models.Model):
    first_name=models.CharField(max_length=200)
    last_name=models.CharField(max_length=200)
    username=models.CharField(max_length=200,unique=True,blank=True)
    email=models.EmailField(unique=True,max_length=100)
    password=models.CharField(max_length=200)
    mobile_no=models.CharField(max_length=15)
    degree=models.CharField(max_length=30)
    GENDERS = {"M":"Male","F":"Female"}
    gender=models.CharField(max_length=1,choices=GENDERS)
    dob=models.DateField()
    blood_group=models.CharField(max_length=5)
    address=models.TextField(max_length=500)
    profile_photo=CloudinaryField("image")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def total_courses(self):
        total_courses=Enrollment.objects.filter(student=self).count()
        return total_courses
    
    def total_teachers(self):
        total_teacher=Teacher.objects.filter(subject__enrolled_subject__student=self).distinct().count()
        return total_teacher

    @property
    def image_url(self):
        if self.profile_photo:
            return(f"https://res.cloudinary.com/drzvymfnv/{self.profile_photo}") 
        return None


class Enrollment(models.Model):
    student=models.ForeignKey(Student,on_delete=models.CASCADE,related_name="enrolled_student")
    subject=models.ForeignKey(Subject,on_delete=models.CASCADE,related_name="enrolled_subject")
    enrollment_date=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} - {self.student}"











    
