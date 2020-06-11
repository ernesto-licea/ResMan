import magic
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _

@deconstructible
class FileMimeTypeValidator:
    message = _(
        "File mime type '%(mime_type)s' is not allowed. "
        "Allowed mime types are: '%(allowed_mime_types)s'."
    )
    code = 'invalid_extension'

    def __init__(self, allowed_mime_types=None, message=None, code=None):
        if allowed_mime_types is not None:
            allowed_mime_types = [allowed_mime_types.lower() for allowed_mime_types in allowed_mime_types]
        self.allowed_mime_types = allowed_mime_types
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code

    def __call__(self, value):
        mime_type = magic.from_buffer(value.read(), mime=True)
        if self.allowed_mime_types is not None and mime_type not in self.allowed_mime_types:
            raise ValidationError(
                self.message,
                code=self.code,
                params={
                    'mime_type': mime_type,
                    'allowed_mime_types': ', '.join(self.allowed_mime_types)
                }
            )

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and
            self.allowed_mime_types == other.allowed_mime_types and
            self.message == other.message and
            self.code == other.code
        )