from django.urls import path
from . import views
from .views import analyze_view, analyze_view_by_id, login_view

urlpatterns = [
    # path('', views.main, name='main'),
    path('', analyze_view, name='main'),
    path('login/', login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('analyze/', analyze_view, name='analyze'),
    path('analyze/<int:image_id>/', views.analyze_view_by_id, name='analyze_by_id'),
    path('logout/', views.user_logout, name='user_logout'),

]
