from rest_framework import generics, permissions, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView
from django.shortcuts import get_object_or_404
from users.models import User
from vacancies.models import Vacancy, Response
from practices.models import PracticeBase, PracticeRequest
from .serializers import (
    UserSerializer, RegisterSerializer, VacancySerializer, 
    ResponseSerializer, PracticeBaseSerializer, PracticeRequestSerializer
)


class LoginView(TokenObtainPairView):
    pass


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class VacancyViewSet(viewsets.ModelViewSet):
    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(company=self.request.user)

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.role == 'company':
            return Vacancy.objects.filter(company=self.request.user)
        return Vacancy.objects.filter(is_active=True)

    @action(detail=True, methods=['post'])
    def respond(self, request, pk=None):
        vacancy = self.get_object()
        response, created = Response.objects.get_or_create(
            vacancy=vacancy,
            student=request.user,
            defaults={'cover_letter': request.data.get('cover_letter', '')}
        )
        serializer = ResponseSerializer(response)
        return Response(serializer.data)


class ResponseViewSet(viewsets.ModelViewSet):
    serializer_class = ResponseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            if self.request.user.role == 'company':
                return Response.objects.filter(vacancy__company=self.request.user)
            return Response.objects.filter(student=self.request.user)
        return Response.objects.none()

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        response = self.get_object()
        new_status = request.data.get('status')
        if new_status:
            response.status = new_status
            response.save()
        return Response(ResponseSerializer(response).data)


class PracticeBaseViewSet(viewsets.ModelViewSet):
    queryset = PracticeBase.objects.all()
    serializer_class = PracticeBaseSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(company=self.request.user)


class PracticeRequestViewSet(viewsets.ModelViewSet):
    serializer_class = PracticeRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            if self.request.user.role == 'company':
                return PracticeRequest.objects.filter(practice_base__company=self.request.user)
            return PracticeRequest.objects.filter(student=self.request.user)
        return PracticeRequest.objects.none()

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)
