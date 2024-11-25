from courses.courseViews import CourseCreateView, CourseDetailView
from django.urls import path

urlpatterns = [
    path('courses/', CourseCreateView.as_view()),
    path('courses/<int:pk>/', CourseDetailView.as_view())
]