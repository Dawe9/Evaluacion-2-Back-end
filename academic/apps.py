"""Configuración de la aplicación Django de farmacia B2B."""

from django.apps import AppConfig


class AcademicConfig(AppConfig):
    # Django usa este nombre para registrar la aplicación academic.
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'academic'
