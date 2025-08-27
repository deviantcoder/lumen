import os
import shortuuid


ALLOWED_EXTENSIONS = (
    'jpg', 'jpeg', 'png', 'gif', 'webp'
)


def base_upload_to(instance, filename, base_dir='uploads', id_attr='public_id'):
    ext = os.path.splitext(filename)[-1]
    new_filename = shortuuid.uuid()

    obj_id = getattr(instance, id_attr, None) or getattr(instance, 'pk', 'unknown')

    return f'{base_dir}/{str(obj_id)}/{new_filename}{ext}'
