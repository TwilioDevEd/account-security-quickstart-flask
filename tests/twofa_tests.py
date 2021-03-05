
from unittest.mock import patch, MagicMock
from urllib.parse import urlparse

from tests.base import BaseTestCase
from twofa.database import db
from twofa.models import User


class TwoFATestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.user = User(
            username='test',
            password='test',
            email='test@example.com',
            authy_id='fake_id'
        )
        db.session.add(self.user)
        db.session.commit()

    def _login(self):
        response = self.client.post('/login', data={
            'username': 'test',
            'password': 'test'
        }, follow_redirects=False)
        self.assertEqual(response.status_code, 302)

    def test_protected_redirect_anonymous_to_login(self):
        # Arrange

        # Act
        response = self.client.get('/protected')

        # Assert
        assert response.status_code == 302
        assert urlparse(response.location).path == '/login'

    def test_protected_logged_in_user_redirected_to_2fa(self):
        # Arrange
        self._login()

        # Act
        response = self.client.get('/protected')

        # Assert
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, 'http://server.test/2fa')

    def test_protected_displays_to_authy_user(self):
        # Arrange
        self._login()

        # Act
        with self.client.session_transaction() as sess:
            sess['authy'] = True
        response = self.client.get('/protected')

        # Assert
        self.assertEqual(response.status_code, 200)

    @patch('twofa.views.authy_api')
    def test_token_sms_success(self, authy_api):
        # Arrange
        request_sms_response = MagicMock()
        request_sms_response.ok.return_value = True
        authy_api.users.request_sms.return_value = request_sms_response

        self._login()

        # Act
        response = self.client.post('/token/sms')

        # Assert
        self.assertEqual(response.status_code, 200)
        authy_api.users.request_sms.assert_called_once_with(
            'fake_id',
            {'force': True}
        )
        request_sms_response.ok.assert_called_once()

    @patch('twofa.views.authy_api')
    def test_token_sms_failure(self, authy_api):
        # Arrange
        request_sms_response = MagicMock()
        request_sms_response.ok.return_value = False
        authy_api.users.request_sms.return_value = request_sms_response

        self._login()

        # Act
        response = self.client.post('/token/sms')

        # Assert
        self.assertEqual(response.status_code, 503)
        authy_api.users.request_sms.assert_called_once_with(
            'fake_id',
            {'force': True}
        )
        request_sms_response.ok.assert_called_once()

    @patch('twofa.views.authy_api')
    def test_token_voice_success(self, authy_api):
        # Arrange
        request_call_response = MagicMock()
        request_call_response.ok.return_value = True
        authy_api.users.request_call.return_value = request_call_response

        self._login()

        # Act
        response = self.client.post('/token/voice')

        # Assert
        self.assertEqual(response.status_code, 200)
        authy_api.users.request_call.assert_called_once_with(
            'fake_id',
            {'force': True}
        )
        request_call_response.ok.assert_called_once()

    @patch('twofa.views.authy_api')
    def test_token_voice_failure(self, authy_api):
        # Arrange
        request_call_response = MagicMock()
        request_call_response.ok.return_value = False
        authy_api.users.request_call.return_value = request_call_response

        self._login()

        # Act
        response = self.client.post('/token/voice')

        # Assert
        self.assertEqual(response.status_code, 503)
        authy_api.users.request_call.assert_called_once_with(
            'fake_id',
            {'force': True}
        )
        request_call_response.ok.assert_called_once()
