# blog/serializers.py
from rest_framework import serializers
from .models import BlogPost

class BlogPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = fields = ['title', 'content', 'created_at', 'updated_at']  # Include necessary fields
        
        # Field-Level Validation
    def validate_title(self, value):
        if len(value) < 5:
            raise serializers.ValidationError("Title must be at least 5 characters long.")
        if len(value) > 100:
            raise serializers.ValidationError("Title cannot exceed 100 characters.")
        return value

    def validate_content(self, value):
        if len(value) < 20:
            raise serializers.ValidationError("Content must be at least 20 characters long.")
        return value