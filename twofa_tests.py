import os
import twofa
import unittest
import tempfile

from flask_login import encode_cookie
from twofa.database import db_session
from twofa.models import User

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

try:
    from unittest.mock import patch, MagicMock
except ImportError:
    from mock import patch, MagicMock


class TwoFATestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, twofa.app.config['DATABASE'] = tempfile.mkstemp()
        twofa.app.testing = True
        twofa.app.config['WTF_CSRF_METHODS'] = []  # This is the magic
        twofa.app.config['WTF_CSRF_ENABLED'] = False
        self.app = twofa.app.test_client()
        with twofa.app.app_context():
            twofa.init_db()

        self.user = User(
            username='test',
            password='test',
            email='test@example.com',
            authy_id='fake_id'
        )
        db_session.add(self.user)
        db_session.commit()

    def tearDown(self):
        db_session.delete(self.user)
        db_session.commit()
        os.close(self.db_fd)
        os.unlink(twofa.app.config['DATABASE'])

    def test_protected_redirect_anonymous_to_login(self):
        # Arrange

        # Act
        response = self.app.get('/protected')

        # Assert
        assert response.status_code == 302
        assert urlparse(response.location).path == '/login'

    def test_protected_logged_in_user_redirected_to_2fa(self):
        # Arrange

        # Act
        with self.app:
            response = self.app.post('/login', data={
                'username': 'test',
                'password': 'test'
            }, follow_redirects=False)
            response = self.app.get('/protected')

        # Assert
        assert response.status_code == 302
        assert urlparse(response.location).path == '/2fa'

    def test_protected_displays_to_authy_user(self):
        # Arrange

        # Act
        with self.app:
            response = self.app.post('/login', data={
                'username': 'test',
                'password': 'test'
            }, follow_redirects=False)
            with self.app.session_transaction() as sess:
                sess['authy'] = True
            response = self.app.get('/protected')

        # Assert
        assert response.status_code == 200

    @patch('twofa.views.authy_api')
    def test_token_sms_success(self, authy_api):
        # Arrange
        request_sms_response = MagicMock()
        request_sms_response.ok.return_value = True
        authy_api.users.request_sms.return_value = request_sms_response

        # Act
        with self.app:
            response = self.app.post('/login', data={
                'username': 'test',
                'password': 'test'
            }, follow_redirects=False)
            response = self.app.post('/token/sms')

        # Assert
        assert response.status_code == 200
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

        # Act
        with self.app:
            response = self.app.post('/login', data={
                'username': 'test',
                'password': 'test'
            }, follow_redirects=False)
            response = self.app.post('/token/sms')

        # Assert
        assert response.status_code == 503
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

        # Act
        with self.app:
            response = self.app.post('/login', data={
                'username': 'test',
                'password': 'test'
            }, follow_redirects=False)
            response = self.app.post('/token/voice')

        # Assert
        assert response.status_code == 200
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

        # Act
        with self.app:
            response = self.app.post('/login', data={
                'username': 'test',
                'password': 'test'
            }, follow_redirects=False)
            response = self.app.post('/token/voice')

        # Assert
        assert response.status_code == 503
        authy_api.users.request_call.assert_called_once_with(
            'fake_id',
            {'force': True}
        )
        request_call_response.ok.assert_called_once()


if __name__ == '__main__':
    unittest.main()
