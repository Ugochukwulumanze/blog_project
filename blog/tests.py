from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from .models import BlogPost

class BlogPostAPITestCase(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.client = APIClient()
        self.client.login(username="testuser", password="password123")
        self.blogpost_data = {
            "title": "Test Blog Post",
            "content": "This is a test content for the blog post.",
        }
        # Create a blog post for testing retrieval, update, and deletion
        self.blogpost = BlogPost.objects.create(user=self.user, **self.blogpost_data)

    def test_create_blog_post(self):
        url = reverse('posts')  # Adjust the name based on your URL configuration
        response = self.client.post(url, self.blogpost_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], self.blogpost_data["title"])
        self.assertEqual(response.data["content"], self.blogpost_data["content"])
        self.assertEqual(response.data["user"], self.user.id)
        
    def test_retrieve_blog_post(self):
        url = reverse('posts/<int:pk>', args=[self.blogpost.id])  # Adjust the name based on your URL configuration
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.blogpost.title)
        self.assertEqual(response.data["content"], self.blogpost.content)
        self.assertEqual(response.data["user"], self.user.id)

    def test_update_blog_post(self):
        url = reverse('posts/<int:pk>', args=[self.blogpost.id])  # Adjust the name based on your URL configuration
        updated_data = {
            "title": "Updated Blog Post Title",
            "content": "Updated content for the blog post.",
        }
        
        response = self.client.put(url, updated_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.blogpost.refresh_from_db()
        self.assertEqual(self.blogpost.title, updated_data["title"])
        self.assertEqual(self.blogpost.content, updated_data["content"])

    def test_delete_blog_post(self):
        url = reverse('posts/<int:pk>', args=[self.blogpost.id])  # Adjust the name based on your URL configuration
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(BlogPost.objects.filter(id=self.blogpost.id).exists())

    def test_list_blog_posts(self):
        url = reverse('posts')  # Adjust the name based on your URL configuration
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data['results'], list)  # Assuming pagination
        self.assertGreaterEqual(len(response.data['results']), 1)  # At least one blog post exists
