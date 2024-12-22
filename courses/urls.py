from courses.courseViews import CourseCreateView, CourseDetailView, CourseTeacherRelationCreateView
from django.urls import path

urlpatterns = [
    path('courses/', CourseCreateView.as_view()),
    path('courses/<int:pk>/', CourseDetailView.as_view()),
    path('course-teacher/<int:pk>/', CourseTeacherRelationCreateView.as_view())
    
]