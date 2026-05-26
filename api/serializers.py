from rest_framework import serializers
from users.models import User
from vacancies.models import Vacancy, Response
from practices.models import PracticeBase, PracticeRequest


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role', 'phone', 'company_name', 'student_group')
        read_only_fields = ('id',)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'first_name', 'last_name', 'role', 'company_name', 'student_group')

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class VacancySerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.company_name', read_only=True)

    class Meta:
        model = Vacancy
        fields = '__all__'
        read_only_fields = ('company', 'created_at', 'updated_at')


class ResponseSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.username', read_only=True)
    vacancy_title = serializers.CharField(source='vacancy.title', read_only=True)

    class Meta:
        model = Response
        fields = '__all__'
        read_only_fields = ('student', 'created_at', 'vacancy')


class PracticeBaseSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.company_name', read_only=True)

    class Meta:
        model = PracticeBase
        fields = '__all__'
        read_only_fields = ('company',)


class PracticeRequestSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.username', read_only=True)
    practice_type = serializers.CharField(source='practice_base.practice_type', read_only=True)
    company_name = serializers.CharField(source='practice_base.company.company_name', read_only=True)

    class Meta:
        model = PracticeRequest
        fields = '__all__'
        read_only_fields = ('student', 'created_at')
