from .mixins import LisanModelMixin
from .admin import LisanAdminMixin

default_app_config = 'lisan.apps.LisanConfig'

__all__ = ['LisanModelMixin', 'LisanAdminMixin']
