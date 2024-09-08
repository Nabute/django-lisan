from django.test import TestCase
from django.contrib.admin.sites import AdminSite
from lisan.admin import LisanAdminMixin
from django.test import RequestFactory
from django.db import models


class DummyModelAdmin(LisanAdminMixin, models.Model):
    lisan_fields = ['title']
    title = models.CharField(max_length=255)


class LisanAdminMixinTestCase(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = LisanAdminMixin(DummyModelAdmin, self.site)
        self.factory = RequestFactory()

    def test_generate_lisan_getters(self):
        self.assertTrue(hasattr(self.admin, 'get_lisan_title'))

    def test_list_display(self):
        request = self.factory.get('/admin/')
        self.assertIn('get_lisan_title', self.admin.get_list_display(request))

    def test_get_lisan_inline(self):
        inlines = self.admin.get_inlines(None)
        self.assertEqual(len(inlines), 1)

    def test_get_inlines(self):
        inlines = self.admin.get_inlines(None)
        self.assertEqual(len(inlines), 1)
