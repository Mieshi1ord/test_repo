from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    VacancyViewSet, ResponseViewSet, PracticeBaseViewSet, 
    PracticeRequestViewSet, UserProfileView, RegisterView
)

router = DefaultRouter()
router.register('vacancies', VacancyViewSet)
router.register('responses', ResponseViewSet, basename='response')
router.register('practice-bases', PracticeBaseViewSet)
router.register('practice-requests', PracticeRequestViewSet, basename='practice-request')

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', UserProfileView.as_view(), name='profile'),
]
