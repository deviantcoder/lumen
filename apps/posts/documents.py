from django.contrib.auth import get_user_model

from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from .models import Post


User = get_user_model()


@registry.register_document
class PostDocument(Document):

    caption = fields.TextField()
    created = fields.DateField()
    author_username = fields.KeywordField(
        attr='author.username'
    )
    
    class Index:
        name = 'posts'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }

    class Django:
        model = Post
        fields = (
            'id',
            'public_id',
        )
        related_models = [User]
