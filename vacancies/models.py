from django.db import models
from users.models import User

class Vacancy(models.Model):
    EMPLOYMENT_CHOICES = (
        ('full', 'Полная занятость'),
        ('part', 'Частичная занятость'),
        ('intern', 'Стажировка'),
    )

    company = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vacancies', limit_choices_to={'role': 'company'})
    title = models.CharField('Название', max_length=200)
    description = models.TextField('Описание')
    requirements = models.TextField('Требования')
    conditions = models.TextField('Условия работы', blank=True)
    salary_min = models.IntegerField('Зарплата от', null=True, blank=True)
    salary_max = models.IntegerField('Зарплата до', null=True, blank=True)
    employment_type = models.CharField('Тип занятости', max_length=10, choices=EMPLOYMENT_CHOICES, default='full')
    location = models.CharField('Местоположение', max_length=200, default='Москва')
    is_active = models.BooleanField('Активна', default=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Вакансия'
        verbose_name_plural = 'Вакансии'

    def __str__(self):
        return f"{self.title} - {self.company.company_name or self.company.username}"


class Response(models.Model):
    STATUS_CHOICES = (
        ('pending', 'На рассмотрении'),
        ('viewed', 'Просмотрено'),
        ('invited', 'Приглашение'),
        ('rejected', 'Отказ'),
        ('hired', 'Принят'),
    )

    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name='responses')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='responses', limit_choices_to={'role': 'student'})
    cover_letter = models.TextField('Сопроводительное письмо', blank=True)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField('Дата отклика', auto_now_add=True)

    class Meta:
        verbose_name = 'Отклик'
        verbose_name_plural = 'Отклики'
        unique_together = ['vacancy', 'student']

    def __str__(self):
        return f"{self.student.username} -> {self.vacancy.title}"


class Resume(models.Model):
    student = models.OneToOneField(User, on_delete=models.CASCADE, related_name='resume', limit_choices_to={'role': 'student'})
    about = models.TextField('О себе', blank=True)
    skills = models.TextField('Навыки', blank=True)
    education = models.TextField('Образование', blank=True)
    experience = models.TextField('Опыт работы', blank=True)
    portfolio_link = models.URLField('Портфолио', blank=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Резюме'
        verbose_name_plural = 'Резюме'

    def __str__(self):
        return f"Резюме {self.student.username}"
