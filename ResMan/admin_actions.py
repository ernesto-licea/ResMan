
from django.contrib import messages
from django.contrib.admin import helpers
from django.contrib.admin.utils import model_ngettext
from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _


def delete_selected_services(modeladmin,request,queryset):

    opts = modeladmin.model._meta
    app_label = opts.app_label

    # Populate deletable_objects, a data structure of all related objects that
    # will also be deleted.
    deletable_objects, model_count, perms_needed, protected = modeladmin.get_deleted_objects(queryset, request)

    # The user has already confirmed the deletion.
    # Do the deletion and return None to display the change list view again.
    if request.POST.get('post') and not protected:
        if perms_needed:
            raise PermissionDenied
        n = queryset.count()
        deleted_count = 0
        if n:
            for obj in queryset:
                obj_display = str(obj)
                modeladmin.log_deletion(request, obj, obj_display)
                ldap_error = obj.delete()
                if ldap_error:
                    modeladmin.message_user(request, ldap_error, messages.ERROR)
                else:
                    deleted_count += 1
                    message = _('The {} "{}" was successfully deleted from ldap servers.'.format(
                        opts.verbose_name,
                        obj.name
                    ))
                    modeladmin.message_user(request, message, messages.SUCCESS)
            if deleted_count:
                modeladmin.message_user(request, _("Successfully deleted %(count)d %(items)s.") % {
                    "count": deleted_count, "items": model_ngettext(modeladmin.opts, deleted_count)
                }, messages.SUCCESS)
        # Return None to display the change list page again.
        return None

    objects_name = model_ngettext(queryset)

    if perms_needed or protected:
        title = _("Cannot delete %(name)s") % {"name": objects_name}
    else:
        title = _("Are you sure?")

    context = {
        **modeladmin.admin_site.each_context(request),
        'title': title,
        'objects_name': str(objects_name),
        'deletable_objects': [deletable_objects],
        'model_count': dict(model_count).items(),
        'queryset': queryset,
        'perms_lacking': perms_needed,
        'protected': protected,
        'opts': opts,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
        'media': modeladmin.media,
    }

    request.current_app = modeladmin.admin_site.name

    # Display the confirmation page
    return TemplateResponse(request, modeladmin.delete_selected_confirmation_template or [
        "admin/%s/%s/delete_selected_confirmation.html" % (app_label, opts.model_name),
        "admin/%s/delete_selected_confirmation.html" % app_label,
        "admin/delete_selected_confirmation.html"
    ], context)

