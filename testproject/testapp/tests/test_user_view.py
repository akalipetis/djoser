from django.conf import settings
from django.contrib.auth import get_user_model
from django.test.utils import override_settings

from djet import assertions, restframework, utils
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

import djoser.views

from .common import create_user

User = get_user_model()


class UserViewTest(restframework.APIViewTestCase,
                   assertions.EmailAssertionsMixin,
                   assertions.StatusCodeAssertionsMixin):
    view_class = djoser.views.UserView

    def test_get_return_user(self):
        user = create_user()
        request = self.factory.get(user=user)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), set(
            [User.USERNAME_FIELD, User._meta.pk.name] + User.REQUIRED_FIELDS
        ))

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{'SEND_ACTIVATION_EMAIL': False})
    )
    def test_email_change_with_send_activation_email_false(self):
        user = create_user()
        data = {'email': 'ringo@beatles.com'}
        request = self.factory.put(user=user, data=data)
        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_200_OK)
        user = utils.refresh(user)
        self.assertEqual(data['email'], user.email)
        self.assertTrue(user.is_active)

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{'SEND_ACTIVATION_EMAIL': True})
    )
    def test_email_change_with_send_activation_email_true(self):
        user = create_user()
        data = {'email': 'ringo@beatles.com'}
        request = self.factory.put(user=user, data=data)
        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_200_OK)
        user = utils.refresh(user)
        self.assertEqual(data['email'], user.email)
        self.assertFalse(user.is_active)
        self.assert_emails_in_mailbox(1)
        self.assert_email_exists(to=[data['email']])


class UserViewSetMeTest(APITestCase,
                        assertions.EmailAssertionsMixin,
                        assertions.StatusCodeAssertionsMixin):
    view_class = djoser.views.UserView

    def setUp(self):
        self.user = create_user()
        self.client.force_authenticate(user=self.user)

    def test_get_return_user(self):
        response = self.client.get(reverse('user-me'))

        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), set(
            [User.USERNAME_FIELD, User._meta.pk.name] + User.REQUIRED_FIELDS
        ))

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{'SEND_ACTIVATION_EMAIL': False})
    )
    def test_put_email_change_with_send_activation_email_false(self):
        data = {'email': 'ringo@beatles.com'}
        response = self.client.put(reverse('user-me'), data=data)

        self.assert_status_equal(response, status.HTTP_200_OK)
        self.user = utils.refresh(self.user)
        self.assertEqual(data['email'], self.user.email)
        self.assertTrue(self.user.is_active)

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{'SEND_ACTIVATION_EMAIL': True})
    )
    def test_put_email_change_with_send_activation_email_true(self):
        data = {'email': 'ringo@beatles.com'}
        response = self.client.put(reverse('user-me'), data=data)

        self.assert_status_equal(response, status.HTTP_200_OK)
        self.user = utils.refresh(self.user)
        self.assertEqual(data['email'], self.user.email)
        self.assertFalse(self.user.is_active)
        self.assert_emails_in_mailbox(1)
        self.assert_email_exists(to=[data['email']])

    def test_patch_email_change_with_send_activation_email_false(self):
        data = {'email': 'ringo@beatles.com'}
        response = self.client.patch(reverse('user-me'), data=data)

        self.assert_status_equal(response, status.HTTP_200_OK)
        self.user = utils.refresh(self.user)
        self.assertEqual(data['email'], self.user.email)
        self.assertTrue(self.user.is_active)

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{'SEND_ACTIVATION_EMAIL': True})
    )
    def test_patch_email_change_with_send_activation_email_true(self):
        data = {'email': 'ringo@beatles.com'}
        response = self.client.patch(reverse('user-me'), data=data)

        self.assert_status_equal(response, status.HTTP_200_OK)
        self.user = utils.refresh(self.user)
        self.assertEqual(data['email'], self.user.email)
        self.assertFalse(self.user.is_active)
        self.assert_emails_in_mailbox(1)
        self.assert_email_exists(to=[data['email']])

    def test_drf_docs(self):
        """
        Test that DRF docs do not crash.
        """
        response = self.client.get('/docs/')

        self.assert_status_equal(response, status.HTTP_200_OK)
