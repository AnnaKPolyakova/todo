from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from deals.models import Task


class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаём запись в БД
        Task.objects.create(
            title='Заголовок',
            text='Текст',
            slug='test-slug',
        )

    def setUp(self):
        # Создаём неавторизованный клиент
        self.guest_client = Client()
        # Создаём авторизованный клиент
        self.user = get_user_model().objects.create_user(username='StasBasov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_page_names = {
            'deals/home.html': reverse('deals:home'),
            'deals/added.html': reverse('deals:task_added'),
            'deals/task_list.html': reverse('deals:task_list'),
            'deals/task_list.html': reverse('deals:task_list'),
            'deals/task_detail.html': (
                reverse('deals:task_detail', kwargs={'slug': 'test-slug'})
            ),
        }
        # Проверяем, что при обращении к name вызывается соответствующий HTML-шаблон
        for template, reverse_name in templates_page_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # Проверка словаря контекста главной страницы (в нём передаётся форма)
    def test_home_page_show_correct_context(self):
        """Шаблон home сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('deals:home'))
        # Список ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        form_fields = {
            'title': forms.fields.CharField,
            # При создании формы поля модели типа TextField 
            # преобразуются в CharField с виджетом forms.Textarea 
            'text': forms.fields.CharField,
            'slug': forms.fields.SlugField,
            'image': forms.fields.ImageField,
        }
        # Проверяем, что типы полей формы в словаре context соответствуют ожиданиям
        for value, expected in form_fields.items():
            with self.subTest():
                form_field = response.context.get('form').fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    def test_task_list_page_list_is_1(self):
        response = self.authorized_client.get(reverse('deals:task_list'))
        self.assertEqual(len(response.context['object_list']), 1)

    # Проверяем, что словарь context страницы /task
    # в первом элементе списка object_list содержит ожидаемые значения 
    def test_task_list_page_show_correct_context(self):
        """Шаблон task_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('deals:task_list'))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        task_title_0 = response.context.get('object_list')[0].title
        task_text_0 = response.context.get('object_list')[0].text
        task_slug_0 = response.context.get('object_list')[0].slug
        self.assertEqual(task_title_0, 'Заголовок')
        self.assertEqual(task_text_0, 'Текст')
        self.assertEqual(task_slug_0, 'test-slug')

    # Проверяем, что словарь context страницы task/test-slug
    # содержит ожидаемые значения 
    def test_task_detail_pages_show_correct_context(self):
        """Шаблон task_detail сформирован с правильным контекстом."""
        response = self.authorized_client.\
            get(reverse('deals:task_detail', kwargs={'slug': 'test-slug'}))
        self.assertEqual(response.context.get('task').title, 'Заголовок')
        self.assertEqual(response.context.get('task').text, 'Текст')
        self.assertEqual(response.context.get('task').slug, 'test-slug')