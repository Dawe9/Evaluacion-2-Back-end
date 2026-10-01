"""Carga un catálogo visual de ejemplo para desarrollo y demostraciones."""

from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from academic.models import MedicalSupply, SupplyCategory


class Command(BaseCommand):
    """Crea o actualiza insumos demo sin duplicar registros."""

    help = 'Carga categorías e insumos médicos de ejemplo con imágenes.'

    catalog = [
        {
            'category': 'Medicamentos',
            'category_description': 'Medicamentos de uso habitual para instituciones de salud.',
            'commercial_name': 'Paracetamol 500 mg · 100 comprimidos',
            'active_ingredient': 'Paracetamol',
            'lot': 'DEMO-MED-001',
            'days_to_expire': 820,
            'unit_price': '2490.00',
            'stock': 84,
            'image_url': 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?auto=format&fit=crop&w=900&q=85',
        },
        {
            'category': 'Medicamentos',
            'category_description': 'Medicamentos de uso habitual para instituciones de salud.',
            'commercial_name': 'Suero fisiológico 0,9% · 500 mL',
            'active_ingredient': 'Cloruro de sodio',
            'lot': 'DEMO-MED-002',
            'days_to_expire': 610,
            'unit_price': '1890.00',
            'stock': 45,
            'image_url': 'https://images.unsplash.com/photo-1603398938378-e54eab446dde?auto=format&fit=crop&w=900&q=85',
        },
        {
            'category': 'Medicamentos',
            'category_description': 'Medicamentos de uso habitual para instituciones de salud.',
            'commercial_name': 'Vitamina C · 1 g · 30 sobres',
            'active_ingredient': 'Ácido ascórbico',
            'lot': 'DEMO-MED-003',
            'days_to_expire': 730,
            'unit_price': '3990.00',
            'stock': 32,
            'image_url': 'https://images.unsplash.com/photo-1550572017-edd951b55104?auto=format&fit=crop&w=900&q=85',
        },
        {
            'category': 'Material quirúrgico',
            'category_description': 'Material clínico desechable y de protección.',
            'commercial_name': 'Gasas estériles · 10 x 10 cm · 100 unidades',
            'active_ingredient': '',
            'lot': 'DEMO-QX-001',
            'days_to_expire': 900,
            'unit_price': '1290.00',
            'stock': 120,
            'image_url': 'https://images.unsplash.com/photo-1583947215259-38e31be8751f?auto=format&fit=crop&w=900&q=85',
        },
        {
            'category': 'Material quirúrgico',
            'category_description': 'Material clínico desechable y de protección.',
            'commercial_name': 'Guantes de nitrilo · talla M · 100 unidades',
            'active_ingredient': 'Nitrilo',
            'lot': 'DEMO-QX-002',
            'days_to_expire': 1000,
            'unit_price': '5990.00',
            'stock': 65,
            'image_url': 'https://images.unsplash.com/photo-1584634731339-252c581abfc5?auto=format&fit=crop&w=900&q=85',
        },
        {
            'category': 'Material quirúrgico',
            'category_description': 'Material clínico desechable y de protección.',
            'commercial_name': 'Mascarillas quirúrgicas · 3 capas · 50 unidades',
            'active_ingredient': '',
            'lot': 'DEMO-QX-003',
            'days_to_expire': 950,
            'unit_price': '3490.00',
            'stock': 92,
            'image_url': 'https://images.unsplash.com/photo-1584634731339-252c581abfc5?auto=format&fit=crop&w=900&q=80',
        },
        {
            'category': 'Antisépticos',
            'category_description': 'Soluciones para higiene, limpieza y prevención.',
            'commercial_name': 'Alcohol gel 70% · 500 mL',
            'active_ingredient': 'Etanol 70%',
            'lot': 'DEMO-ANT-001',
            'days_to_expire': 660,
            'unit_price': '3290.00',
            'stock': 58,
            'image_url': 'https://images.unsplash.com/photo-1584744982491-665216d95f8b?auto=format&fit=crop&w=900&q=85',
        },
        {
            'category': 'Antisépticos',
            'category_description': 'Soluciones para higiene, limpieza y prevención.',
            'commercial_name': 'Clorhexidina 2% · 250 mL',
            'active_ingredient': 'Gluconato de clorhexidina',
            'lot': 'DEMO-ANT-002',
            'days_to_expire': 580,
            'unit_price': '4290.00',
            'stock': 26,
            'image_url': 'https://images.unsplash.com/photo-1607619056574-7b8d3ee536b2?auto=format&fit=crop&w=900&q=85',
        },
    ]

    def handle(self, *args, **options):
        today = timezone.localdate()
        created_categories = set()
        created_supplies = 0
        updated_supplies = 0

        for item in self.catalog:
            category, category_created = SupplyCategory.objects.get_or_create(
                name=item['category'],
                defaults={'description': item['category_description']},
            )
            if not category_created and category.description != item['category_description']:
                category.description = item['category_description']
                category.save(update_fields=['description'])
            if category_created:
                created_categories.add(category.name)

            supply, supply_created = MedicalSupply.objects.update_or_create(
                commercial_name=item['commercial_name'],
                lot=item['lot'],
                defaults={
                    'category': category,
                    'active_ingredient': item['active_ingredient'],
                    'expiration_date': today + timedelta(days=item['days_to_expire']),
                    'unit_price': Decimal(item['unit_price']),
                    'image_url': item['image_url'],
                    'stock': item['stock'],
                    'is_active': True,
                },
            )
            if supply_created:
                created_supplies += 1
            else:
                updated_supplies += 1

        self.stdout.write(self.style.SUCCESS(
            f'Catálogo demo listo: {len(created_categories)} categorías nuevas, '
            f'{created_supplies} insumos creados y {updated_supplies} actualizados.'
        ))