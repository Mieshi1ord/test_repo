from django.contrib import admin
from .models import Vacancy

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'is_active', 'created_at')
    list_filter = ('is_active', 'employment_type')
    search_fields = ('title', 'company__username')
