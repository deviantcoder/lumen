from django.contrib.auth import get_user_model

from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from apps.profiles.models import Profile


User = get_user_model()


@registry.register_document
class ProfileDocument(Document):

    """
    Elasticsearch document for the Profile model.
    """

    username = fields.TextField(
        attr='user.username'
    )
    full_name = fields.TextField(
        attr='user.full_name'
    )
    bio = fields.TextField()
    
    class Index:
        name = 'profiles'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }

    class Django:
        model = Profile
        fields = (
            'id',
        )
        related_models = [User]

    def get_queryset(self):
        return (
            super().get_queryset().select_related('user')
        )
    
    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, User):
            return related_instance.profile
        return None
