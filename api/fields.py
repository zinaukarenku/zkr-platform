from drf_extra_fields.fields import Base64ImageField as BaseBase64ImageField
import base64


class Base64ImageField(BaseBase64ImageField):

    def to_representation(self, file):
        if file and hasattr(file, 'url') and file.url:
            with file.open(mode='rb') as f:
                return base64.b64encode(f.read()).decode()
