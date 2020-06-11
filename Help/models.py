from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from Help.validators import FileMimeTypeValidator


def help_en_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/help_<id>/<filename>
    return 'help_{0}/en/{1}'.format(instance.name_en, filename)

def help_es_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/help_<id>/<filename>
    return 'help_{0}/es/{1}'.format(instance.name_es, filename)

class Help(models.Model):
    name_es = models.CharField(_('name (es)'), max_length=50, default=True)
    name_en = models.CharField(_('name (en)'), max_length=50, default=True)
    description_es = models.TextField(_('description (es)'), default="")
    description_en = models.TextField(_('description (en)'), default="")
    attachment_es = models.FileField(
        _('attachment (es)'),
        upload_to=help_es_directory_path,
        blank=True,
        validators=[
            FileExtensionValidator(['pdf',]),
            FileMimeTypeValidator(['application/pdf',])
        ]
    )
    attachment_en = models.FileField(
        _('attachment (es)'),
        upload_to=help_en_directory_path,
        blank=True,
        validators=[
            FileExtensionValidator(['pdf',]),
            FileMimeTypeValidator(['application/pdf',])
        ]
    )
    def __str__(self):
        return self.name_en

    class Meta:
        db_table = 'help'
        verbose_name = _('help')
        verbose_name_plural = _('helps')