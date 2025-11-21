from django.test import TestCase
from django.urls import reverse
from .models import Todo
from datetime import date

class TodoModelTest(TestCase):
    def test_create_todo(self):
        t = Todo.objects.create(title="Test", description="desc", due_date=date.today())
        self.assertEqual(Todo.objects.count(), 1)
        self.assertFalse(t.resolved)

class TodoViewTests(TestCase):
    def setUp(self):
        self.t = Todo.objects.create(title="T", description="D")

    def test_home_shows_todo(self):
        r = self.client.get(reverse('home'))
        self.assertContains(r, "T")

    def test_create_view(self):
        r = self.client.post(reverse('todo_create'), {'title': 'X', 'description': 'Y'})
        self.assertEqual(r.status_code, 302)
        self.assertTrue(Todo.objects.filter(title='X').exists())

    def test_edit_view(self):
        url = reverse('todo_edit', args=[self.t.pk])
        r = self.client.post(url, {'title': 'Updated', 'description': 'D'})
        self.assertEqual(r.status_code, 302)
        self.t.refresh_from_db()
        self.assertEqual(self.t.title, 'Updated')

    def test_toggle_resolved(self):
        url = reverse('toggle_resolved', args=[self.t.pk])
        self.client.get(url)
        self.t.refresh_from_db()
        self.assertTrue(self.t.resolved)
