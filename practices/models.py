from django.db import models
from users.models import User

class PracticeBase(models.Model):
    company = models.ForeignKey(User, on_delete=models.CASCADE, related_name='practice_bases', limit_choices_to={'role': 'company'})
    practice_type = models.CharField('Тип практики', max_length=100)
    available_slots = models.IntegerField('Количество мест')
    description = models.TextField('Описание практики')
    contact_person = models.CharField('Контактное лицо', max_length=100)
    contact_phone = models.CharField('Телефон', max_length=20)
    contact_email = models.EmailField('Email')

    class Meta:
        verbose_name = 'База практики'
        verbose_name_plural = 'Базы практик'

    def __str__(self):
        return f"{self.company.company_name or self.company.username} - {self.practice_type}"


class PracticeRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'На рассмотрении'),
        ('approved', 'Согласована'),
        ('rejected', 'Отклонена'),
        ('completed', 'Завершена'),
    )

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='practice_requests', limit_choices_to={'role': 'student'})
    practice_base = models.ForeignKey(PracticeBase, on_delete=models.CASCADE, related_name='requests')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    start_date = models.DateField('Дата начала', null=True, blank=True)
    end_date = models.DateField('Дата окончания', null=True, blank=True)
    report_file = models.FileField('Отчёт о практике', upload_to='reports/', blank=True)
    feedback = models.TextField('Отзыв от руководителя', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Заявка на практику'
        verbose_name_plural = 'Заявки на практику'

    def __str__(self):
        return f"{self.student.username} - {self.practice_base.practice_type}"
