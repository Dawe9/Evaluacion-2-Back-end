"""Pruebas de integración del abastecimiento institucional."""

from datetime import date
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.db import OperationalError
from django.test import TestCase
from rest_framework_simplejwt.tokens import AccessToken

from .models import Institution, MedicalSupply, Profile, PurchaseRequest, SupplyCategory


class PharmacyApiTests(TestCase):
    """Cubre autenticación, catálogo, carro y ciclo del stock."""

    def setUp(self):
        self.institution = Institution.objects.create(name='Centro Médico de Prueba')
        self.category = SupplyCategory.objects.create(name='Medicamentos')
        self.supply = MedicalSupply.objects.create(
            category=self.category,
            commercial_name='Paracetamol 500 mg',
            active_ingredient='Paracetamol',
            lot='LOT-2026-01',
            expiration_date=date(2028, 12, 31),
            unit_price=Decimal('2500.00'),
            stock=5,
        )
        user_model = get_user_model()
        self.customer = user_model.objects.create_user(username='institucion', password='secret123')
        Profile.objects.create(
            user=self.customer,
            role=Profile.Role.MEDICAL_INSTITUTION,
            institution=self.institution,
        )
        self.manager = user_model.objects.create_user(
            username='gestor',
            password='secret123',
            is_staff=True,
        )
        Profile.objects.create(user=self.manager, role=Profile.Role.WAREHOUSE_MANAGER)

    def authenticate(self, user):
        response = self.client.post(
            '/api/token/',
            {'username': user.username, 'password': 'secret123'},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.client.defaults['HTTP_AUTHORIZATION'] = f"Bearer {response.json()['access']}"
        return AccessToken(response.json()['access'])

    def test_public_catalog_filters_and_documentation(self):
        response = self.client.get(
            f'/api/insumos/?category={self.category.pk}&price_min=2000&price_max=3000'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]['commercial_name'], 'Paracetamol 500 mg')
        self.assertEqual(self.client.get('/api/categorias/').status_code, 200)
        self.assertEqual(self.client.get('/api/docs/').status_code, 401)

        self.authenticate(self.manager)
        self.assertEqual(self.client.get('/api/docs/').status_code, 200)
        self.assertEqual(self.client.get('/api/schema/').status_code, 200)

    def test_jwt_contains_role_claim_and_catalog_writes_are_restricted(self):
        token = self.authenticate(self.customer)

        self.assertEqual(token['role'], Profile.Role.MEDICAL_INSTITUTION)
        response = self.client.post(
            '/api/insumos/',
            {'category': self.category.pk, 'commercial_name': 'Gasa', 'lot': 'G-1',
             'expiration_date': '2028-12-31', 'unit_price': '1000.00', 'stock': 10},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 403)

    def test_staff_user_gets_manager_role_even_if_profile_was_created_as_customer(self):
        self.manager.profile.role = Profile.Role.MEDICAL_INSTITUTION
        self.manager.profile.save(update_fields=['role'])

        token = self.authenticate(self.manager)

        self.assertEqual(token['role'], Profile.Role.WAREHOUSE_MANAGER)
        self.manager.profile.refresh_from_db()
        self.assertEqual(self.manager.profile.role, Profile.Role.WAREHOUSE_MANAGER)

    def test_cart_persists_and_checkout_snapshots_price_without_changing_stock(self):
        self.authenticate(self.customer)
        add_response = self.client.post(
            '/api/carro-insumos/',
            {'supply_id': self.supply.pk, 'quantity': 2},
            content_type='application/json',
        )
        self.assertEqual(add_response.status_code, 200)
        self.assertEqual(self.supply.stock, 5)

        self.client.defaults.pop('HTTP_AUTHORIZATION')
        self.authenticate(self.customer)
        cart_response = self.client.get('/api/carro-insumos/')
        self.assertEqual(cart_response.json()['items'][0]['quantity'], 2)

        response = self.client.post('/api/solicitudes/confirmar/')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['status'], PurchaseRequest.Status.PENDING)
        self.assertEqual(response.json()['total'], '5000.00')
        self.assertEqual(self.supply.stock, 5)

    def test_adding_same_supply_increments_one_cart_line(self):
        self.authenticate(self.customer)
        endpoint = '/api/carro-insumos/'
        self.client.post(
            endpoint,
            {'supply_id': self.supply.pk, 'quantity': 1, 'increment': True},
            content_type='application/json',
        )
        response = self.client.post(
            endpoint,
            {'supply_id': self.supply.pk, 'quantity': 2, 'increment': True},
            content_type='application/json',
        )

        self.assertEqual(len(response.json()['items']), 1)
        self.assertEqual(response.json()['items'][0]['quantity'], 3)

    def test_paid_order_decrements_stock_and_paid_cancellation_restores_it(self):
        self.authenticate(self.customer)
        self.client.post(
            '/api/carro-insumos/',
            {'supply_id': self.supply.pk, 'quantity': 2},
            content_type='application/json',
        )
        order = self.client.post('/api/solicitudes/confirmar/').json()

        self.authenticate(self.manager)
        paid = self.client.patch(
            f"/api/solicitudes/{order['id']}/estado/",
            {'status': PurchaseRequest.Status.PAID},
            content_type='application/json',
        )
        self.assertEqual(paid.status_code, 200)
        self.supply.refresh_from_db()
        self.assertEqual(self.supply.stock, 3)

        cancelled = self.client.patch(
            f"/api/solicitudes/{order['id']}/estado/",
            {'status': PurchaseRequest.Status.CANCELLED},
            content_type='application/json',
        )
        self.assertEqual(cancelled.status_code, 200)
        self.supply.refresh_from_db()
        self.assertEqual(self.supply.stock, 5)

    def test_payment_is_rejected_when_stock_is_insufficient(self):
        self.authenticate(self.customer)
        self.client.post(
            '/api/carro-insumos/',
            {'supply_id': self.supply.pk, 'quantity': 6},
            content_type='application/json',
        )
        order = self.client.post('/api/solicitudes/confirmar/').json()

        self.authenticate(self.manager)
        response = self.client.patch(
            f"/api/solicitudes/{order['id']}/estado/",
            {'status': PurchaseRequest.Status.PAID},
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        self.supply.refresh_from_db()
        self.assertEqual(self.supply.stock, 5)

    def test_html_pages_show_student_footer(self):
        for path in ['/', '/products/', '/cart/', '/login/', '/register/', '/gestor/']:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Completar nombre del estudiante')

    def test_warehouse_dashboard_has_inventory_controls(self):
        response = self.client.get('/gestor/')

        self.assertContains(response, 'Panel de administración')
        self.assertContains(response, 'Documentación API')
        self.assertContains(response, 'Registrar insumo')
        self.assertContains(response, 'Solicitudes institucionales')

    def test_staff_jwt_can_open_documentation_session_but_customer_cannot(self):
        self.authenticate(self.customer)
        denied = self.client.post('/api/docs/session/')
        self.assertEqual(denied.status_code, 403)

        self.client.defaults.pop('HTTP_AUTHORIZATION')
        self.authenticate(self.manager)
        response = self.client.post('/api/docs/session/')

        self.assertEqual(response.status_code, 204)
        self.client.defaults.pop('HTTP_AUTHORIZATION')
        self.assertEqual(self.client.get('/api/docs/').status_code, 200)
        self.assertEqual(self.client.get('/api/schema/').status_code, 200)

    def test_staff_admin_can_open_catalog_create_form(self):
        self.client.force_login(self.manager)

        response = self.client.get('/admin/academic/medicalsupply/add/')

        self.assertEqual(response.status_code, 200)

    def test_staff_admin_can_create_worker_without_promoting_user(self):
        self.client.force_login(self.manager)
        add_page = self.client.get('/admin/auth/user/add/')

        self.assertEqual(add_page.status_code, 200)
        self.assertNotContains(add_page, 'name="is_staff"')
        self.assertNotContains(add_page, 'name="is_superuser"')

        response = self.client.post('/admin/auth/user/add/', {
            'username': 'bodega_worker',
            'password1': 'worker-secret-123',
            'password2': 'worker-secret-123',
            'first_name': 'Trabajador',
            'last_name': 'Bodega',
            'email': 'trabajador@example.test',
            'profile-TOTAL_FORMS': '1',
            'profile-INITIAL_FORMS': '0',
            'profile-MIN_NUM_FORMS': '0',
            'profile-MAX_NUM_FORMS': '1',
            'profile-0-institution': '',
            'is_staff': 'on',
            'is_superuser': 'on',
        }, follow=True)

        worker = get_user_model().objects.get(username='bodega_worker')
        self.assertFalse(worker.is_staff)
        self.assertFalse(worker.is_superuser)
        self.assertEqual(worker.profile.role, Profile.Role.MEDICAL_INSTITUTION)
        self.assertEqual(response.status_code, 200)

    def test_warehouse_manager_can_create_and_edit_supply(self):
        self.authenticate(self.manager)
        payload = {
            'category': self.category.pk,
            'commercial_name': 'Gasas estériles',
            'active_ingredient': '',
            'lot': 'LOT-GASA-01',
            'expiration_date': '2028-12-31',
            'unit_price': '1200.00',
            'stock': 25,
            'image_url': '',
            'is_active': True,
        }
        created = self.client.post('/api/insumos/', payload, content_type='application/json')

        self.assertEqual(created.status_code, 201)
        supply_id = created.json()['id']
        updated = self.client.patch(
            f'/api/insumos/{supply_id}/',
            {'stock': 30, 'is_active': False},
            content_type='application/json',
        )

        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.json()['stock'], 30)
        self.assertFalse(updated.json()['is_active'])

    def test_cart_warns_when_stock_is_insufficient(self):
        self.authenticate(self.customer)
        self.client.post(
            '/api/carro-insumos/',
            {'supply_id': self.supply.pk, 'quantity': 2},
            content_type='application/json',
        )

        self.supply.stock = 0
        self.supply.save(update_fields=['stock'])

        response = self.client.get('/api/carro-insumos/')

        self.assertEqual(response.status_code, 200)
        self.assertIn('warnings', response.json())
        self.assertTrue(any(item['supply_id'] == self.supply.pk for item in response.json()['warnings']))

        checkout_response = self.client.post('/api/solicitudes/confirmar/')
        self.assertEqual(checkout_response.status_code, 201)
        self.assertIn('warnings', checkout_response.json())

    def test_homepage_is_distinct_from_catalog(self):
        home_response = self.client.get('/')
        catalog_response = self.client.get('/products/')

        self.assertContains(home_response, 'Explora por categoría')
        self.assertContains(catalog_response, 'Buscar en el catálogo')
        self.assertNotEqual(home_response.content, catalog_response.content)

    @patch('academic.views.SupplyCategory.objects.annotate', side_effect=OperationalError('database unavailable'))
    def test_homepage_still_renders_when_catalog_database_fails(self, _annotate):
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No se pudo conectar con el catálogo')

    def test_public_registration_creates_customer_profile_not_manager(self):
        response = self.client.post(
            '/api/registro/',
            {
                'institution_name': 'Clínica Nueva',
                'tax_id': '76.123.456-7',
                'username': 'clinica_nueva',
                'email': 'contacto@clinica.example',
                'password': 'clave-segura-123',
                'password_confirm': 'clave-segura-123',
                'role': Profile.Role.WAREHOUSE_MANAGER,
            },
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 201)
        user = get_user_model().objects.get(username='clinica_nueva')
        self.assertTrue(user.check_password('clave-segura-123'))
        self.assertEqual(user.profile.role, Profile.Role.MEDICAL_INSTITUTION)
        self.assertEqual(user.profile.institution.name, 'Clínica Nueva')

    def test_registration_rejects_mismatched_passwords(self):
        response = self.client.post(
            '/api/registro/',
            {
                'institution_name': 'Clínica Registro',
                'username': 'registro',
                'email': 'registro@clinica.example',
                'password': 'clave-segura-123',
                'password_confirm': 'otra-clave-123',
            },
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(get_user_model().objects.filter(username='registro').exists())
