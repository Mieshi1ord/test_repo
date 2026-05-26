from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Студент'),
        ('company', 'Компания-работодатель'),
        ('admin', 'Администратор сектора'),
    )
    
    role = models.CharField('Роль', max_length=20, choices=ROLE_CHOICES, default='student')
    phone = models.CharField('Телефон', max_length=20, blank=True)
    company_name = models.CharField('Название компании', max_length=200, blank=True)
    student_group = models.CharField('Группа', max_length=50, blank=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
