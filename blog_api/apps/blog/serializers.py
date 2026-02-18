from rest_framework import serializers

from .models import Category, Tag, Post, Comment
from apps.users.serializers import UserSerializer

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('name', 'slug')

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'author', 'body', 'created_at')
        read_only_fields = ('created_at',)

class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True, required=False
    )

    class Meta:
        model = Post
        fields = (
            'title', 'slug', 'author', 'body', 
            'category', 'category_id', 'tags', 
            'status', 'created_at', 'updated_at'
        )
        read_only_fields = ('slug', 'author', 'created_at', 'updated_at')