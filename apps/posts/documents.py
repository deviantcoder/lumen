from django.contrib.auth import get_user_model

from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from .models import Post, Tag


User = get_user_model()


@registry.register_document
class PostDocument(Document):

    caption = fields.TextField()
    created = fields.DateField()
    author_username = fields.KeywordField(
        attr='author.username'
    )
    tag_names = fields.KeywordField(multi=True)
    
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
        related_models = [User, Tag]

    def prepare_tag_names(self, instance):
        return list(
            instance.tags.values_list('name', flat=True)
        )
