"""Filtros públicos para explorar el catálogo de insumos médicos."""

import django_filters

from .models import MedicalSupply, SupplyCategory


class MedicalSupplyFilter(django_filters.FilterSet):
    category = django_filters.ModelChoiceFilter(queryset=SupplyCategory.objects.all())
    category_name = django_filters.CharFilter(field_name='category__name', lookup_expr='icontains')
    price_min = django_filters.NumberFilter(field_name='unit_price', lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='unit_price', lookup_expr='lte')
    active_ingredient = django_filters.CharFilter(lookup_expr='icontains')
    expiration_before = django_filters.DateFilter(field_name='expiration_date', lookup_expr='lte')
    expiration_after = django_filters.DateFilter(field_name='expiration_date', lookup_expr='gte')

    class Meta:
        model = MedicalSupply
        fields = ['category', 'category_name', 'price_min', 'price_max', 'active_ingredient']