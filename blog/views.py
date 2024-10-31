import logging
from rest_framework import generics
from .models import BlogPost
from .serializers import BlogPostSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.exceptions import PermissionDenied
from .filters import BlogPostFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from drf_spectacular.utils import extend_schema, OpenApiParameter

# Get the logger instance for the blog app
logger = logging.getLogger('blog')

# List all blog posts or create a new one
# Caching BlogPostListCreateView for 15 minutes
@method_decorator(cache_page(60 * 15), name='dispatch')
class BlogPostListCreateView(generics.ListCreateAPIView):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    permission_classes = [IsAuthenticated]  # Only logged-in users can access this
    filterset_class = BlogPostFilter  # Apply the filter class
    
    @extend_schema(
        description="Retrieve a paginated list of all blog posts, with optional filtering by title or content.",
        parameters=[
            OpenApiParameter(name='title', type=str, description='Filter by title'),
            OpenApiParameter(name='content', type=str, description='Filter by content'),
        ],
        responses={200: BlogPostSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        logger.info("Fetching all blog posts")
        try:
            response = super().list(request, *args, **kwargs)
            logger.debug(f"Fetched {len(response.data)} blog posts")
            return response
        except Exception as e:
            logger.error("Error fetching blog posts", exc_info=True)
            raise e
    @extend_schema(
        description="Create a new blog post assigned to the authenticated user.",
        responses={201: BlogPostSerializer}
    )
    def create(self, request, *args, **kwargs):
        logger.info("Attempting to create a new blog post")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            # Set the user to the currently authenticated user
            serializer.save(user=request.user)
            logger.info(f"Blog post created successfully with ID {serializer.data.get('id')} by user {request.user.username}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except ValidationError as e:
            logger.warning("Validation error when creating blog post", exc_info=True)
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error("Unexpected error while creating blog post", exc_info=True)
            return Response({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# Retrieve, update, or delete a specific blog post
# Caching BlogPostDetailView for 15 minutes
@method_decorator(cache_page(60 * 15), name='dispatch')
class BlogPostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    permission_classes = [IsAuthenticated]
    
    @extend_schema(description="Retrieve a specific blog post by ID.", responses={200: BlogPostSerializer})
    def retrieve(self, request, *args, **kwargs):
        logger.info(f"Fetching blog post with ID {kwargs['pk']}")
        return super().retrieve(request, *args, **kwargs)

    # Restrict updates and deletes to the owner of the blog post
    @extend_schema(description="Update a specific blog post by ID.", responses={200: BlogPostSerializer})
    def update(self, request, *args, **kwargs):
        blog_post = self.get_object()
        if blog_post.user != request.user:
            raise PermissionDenied("You are not allowed to update this post.")
        
        logger.info(f"Updating blog post with ID {kwargs['pk']}")
        try:
            response = super().update(request, *args, **kwargs)
            logger.info(f"Blog post {kwargs['pk']} updated successfully")
            return response
        except ValidationError as e:
            logger.warning("Validation error while updating blog post", exc_info=True)
            raise e
        except Exception as e:
            logger.error(f"Unexpected error while updating blog post {kwargs['pk']}", exc_info=True)
            raise e
    @extend_schema(description="Delete a specific blog post by ID.", responses={204: None})
    def destroy(self, request, *args, **kwargs):
        blog_post = self.get_object()
        if blog_post.user != request.user:
            raise PermissionDenied("You are not allowed to delete this post.")
        
        logger.info(f"Deleting blog post with ID {kwargs['pk']}")
        try:
            response = super().destroy(request, *args, **kwargs)
            logger.info(f"Blog post {kwargs['pk']} deleted successfully")
            return response
        except Exception as e:
            logger.error(f"Error deleting blog post {kwargs['pk']}", exc_info=True)
            raise e