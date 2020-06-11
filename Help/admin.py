from django.contrib import admin

# Register your models here.
from Help.models import Help
from ResMan.admin import admin_site


class HelpAdmin(admin.ModelAdmin):
    model = Help
    list_display = ('name_en','description_en')

    def get_list_display(self, request):
        if request.LANGUAGE_CODE.find("es") != -1:
            return ('name_es', 'description_es')
        return self.list_display

    def has_delete_permission(self, request, obj=None):
        if obj:
            if obj.id in [1,2,3,4]:
                return False
        return True

admin_site.register(Help,HelpAdmin)
