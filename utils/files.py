import os
import shortuuid


ALLOWED_IMAGE_EXTENSIONS = (
    'jpg', 'jpeg', 'png', 'gif', 'webp'
)

ALLOWED_VIDEO_EXTENSIONS = (
    'mp4', 'mov', 'avi', 'mkv', 'webm'
)


def base_upload_to(instance, filename, base_dir='uploads', id_attr='public_id'):
    ext = os.path.splitext(filename)[-1]
    new_filename = shortuuid.uuid()

    attrs = id_attr.split('.')
    obj = instance

    print(attrs)
    print(obj)

    for attr in attrs:
        obj = getattr(obj, attr, None)
        print(obj)
        if obj is None:
            break

    obj_id = obj or getattr(instance, 'pk', 'unknown')

    return f'{base_dir}/{obj_id}/{new_filename}{ext}'
