from django_filters import (
    FilterSet,
    DateFilter,
)

from django.forms import DateTimeInput

from .models import Post


class PostFilter(FilterSet):
    """
    FilterSet for the Post model that provides date range filtering.
    """

    start_date = DateFilter(
        field_name='created',
        lookup_expr='gte',
        label='Date from',
        widget=DateTimeInput(attrs={'type': 'date'})
    )

    end_date = DateFilter(
        field_name='created',
        lookup_expr='lte',
        label='Date to',
        widget=DateTimeInput(attrs={'type': 'date'})
    )

    class Meta:
        model = Post
        fields = (
            'start_date',
            'end_date',
        )
