# blog/filters.py
from django_filters import rest_framework as filters
from .models import BlogPost

class BlogPostFilter(filters.FilterSet):
    title = filters.CharFilter(lookup_expr='icontains')  # Case-insensitive search
    content = filters.CharFilter(lookup_expr='icontains')
    created_at = filters.DateFromToRangeFilter()  # Date range filter

    class Meta:
        model = BlogPost
        fields = ['title', 'content', 'created_at']
