from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe

class AdminLinkMixin(models.Model):
    pass

    class Meta():
        abstract = True

    @property
    def model_name(self):
        return self._meta.model_name

    @property
    def verbose_name(self):
        return self._meta.verbose_name
    
    @property
    def app_label(self):
        return self._meta.app_label 

    @property
    def admin_edit_button(self):
        url = reverse('admin:%s_%s_change' % (self.app_label,  self.model_name),  args=[self.id] )
        return mark_safe(f'<a class="btn btn-secondary btn-sm" href="{url}" target="_blank">Edit {self.model_name}</a>')
    
    @property
    def card_template(self):
        return f"{self.app_label}/{self.model_name}/card.html"

    @property
    def action_menu(self):
        return f"{self.app_label}/{self.model_name}/action_menu.html"
    
    @property
    def page_template(self):
        return f"{self.app_label}/{self.model_name}/page.html"

    @classmethod
    def list_template(cls):
        return f"{cls._meta.app_label}/{cls._meta.model_name}/list.html"
    
    @classmethod
    def class_name(cls):
        return cls._meta.model_name
    
    @property
    def icon(self):
        the_icon='bi-patch-question'
        if hasattr(self, 'ICON'):
            the_icon= self.ICON
        return mark_safe(f'<i class="bi {the_icon}"></i>')
