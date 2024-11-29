from django.urls import path
from . import views

urlpatterns =[
    path("",views.start,name="start"),
    path('teacher/',views.TeacherList.as_view()),
    path('teacher-dashboard/<int:pk>',views.TeacherDashboard.as_view()),
     path('student-dashboard/<int:pk>',views.StudentDashboard.as_view()),
    path('teacher/<int:pk>',views.TeacherDetail.as_view()),
    path('student/',views.StudentList.as_view()),
    path('student/<int:pk>',views.StudentDetail.as_view()),
    path('teacher/create/',views.TeacherCreateAPIView.as_view(),name='teacher_create'),
    path('student/create/',views.StudentCreateAPIView.as_view,name='student_create'),
    path('teacher-login',views.teacher_login),
    path('login',views.student_login),
    path('course/',views.SubjectList.as_view()),
    path('course/<int:pk>',views.SubjectDetail.as_view()),
    path('teacher/<int:teacher_id>/courses',views.TeacherCourseList.as_view(),name='teacher-courses'),
    path('teacher-change-password/<int:teacher_id>',views.teacher_change_password),
    path('student-change-password/<int:student_id>',views.student_change_password),
    path('course/<int:subject_id>/teacher/', views.SubjectTeacherList.as_view(), name='course-teacher-list'),
    path('student-enroll-course/<int:student_id>/<int:subject_id>',views.StudentEnrollmentView.as_view()),
    path('fetch-status/<int:student_id>/<int:subject_id>',views.fetch_enroll_status),
    path('fetch-all-enrolled-students/<int:subject_id>',views.EnrolledSubjectList.as_view()),
    path('fetch-enrolled-students/<int:teacher_id>',views.EnrolledSubjectList.as_view()),
    path('fetch-enrolled-courses/<int:student_id>',views.EnrolledSubjectList.as_view())
]