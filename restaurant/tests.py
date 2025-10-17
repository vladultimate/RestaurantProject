from django.test import TestCase, Client
from django.urls import reverse
from django.template.loader import render_to_string

# Create your tests here.
class IndexViewTests(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.url = reverse('home')  
    
    def test_index_view_returns_correct_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'home.html')