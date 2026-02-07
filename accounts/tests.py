import json
from unittest.mock import patch, MagicMock

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.contrib.sessions.middleware import SessionMiddleware

from .views import signup_api, login_api, logout_api
from .models import UserProfile


def _add_session_to_request(request):
	"""Attach a session to a RequestFactory request so login()/logout() works in tests."""
	middleware = SessionMiddleware()
	middleware.process_request(request)
	request.session.save()


class AccountsViewsTests(TestCase):
	def setUp(self):
		self.rf = RequestFactory()

	@patch('accounts.views.process_signup_with_key')
	def test_signup_with_key_success(self, mock_process):
		# Mock return value: character name found
		mock_process.return_value = 'FoundChar'
        
		payload = {
            'user_id': 'testuser1', 
            'password': 'Aa1!aaaa', 
            'nexon_api_key': 'valid_key'
        }
		req = self.rf.post('/accounts/api/signup/', data=json.dumps(payload), content_type='application/json')
		
		with patch('accounts.views.asyncio.run', return_value='FoundChar'):
			resp = signup_api(req)
            
		self.assertEqual(resp.status_code, 201)
		data = json.loads(resp.content)
		self.assertEqual(data.get('status'), 'success')
		self.assertEqual(data['user']['linked_character'], 'FoundChar')
		self.assertTrue(UserProfile.objects.filter(nexon_api_key='valid_key').exists())

	def test_signup_no_key_success(self):
		# API Key optional
		payload = {
            'user_id': 'nokeyuser', 
            'password': 'Aa1!aaaa'
        }
		req = self.rf.post('/accounts/api/signup/', data=json.dumps(payload), content_type='application/json')
		resp = signup_api(req)
		
		self.assertEqual(resp.status_code, 201)
		data = json.loads(resp.content)
		self.assertEqual(data.get('status'), 'success')
		self.assertIsNone(data['user'].get('linked_character'))
		self.assertTrue(User.objects.filter(username='nokeyuser').exists())

	@patch('accounts.views.asyncio.run')
	def test_signup_invalid_key_failure(self, mock_async_run):
		# If API key provided but invalid/no char found -> Fail
		mock_async_run.return_value = None 
		
		payload = {
            'user_id': 'badkeyuser', 
            'password': 'Aa1!aaaa', 
            'nexon_api_key': 'bad_key'
        }
		req = self.rf.post('/accounts/api/signup/', data=json.dumps(payload), content_type='application/json')
		
        # Patch process_signup_with_key to enable import in view
		with patch('accounts.views.process_signup_with_key'):
			resp = signup_api(req)
            
		self.assertEqual(resp.status_code, 400)
		data = json.loads(resp.content)
		self.assertIn('유효하지 않은', data.get('error'))

	def test_signup_missing_fields(self):
		payload = {'user_id': 'testuser1'} # Missing password
		req = self.rf.post('/accounts/api/signup/', data=json.dumps(payload), content_type='application/json')
		resp = signup_api(req)
		self.assertEqual(resp.status_code, 400)

	def test_login_success_and_failure(self):
		user = User.objects.create_user(username='loginuser', password='Login1!')
		
		# successful login
		payload = {'user_id': 'loginuser', 'password': 'Login1!'}
		req = self.rf.post('/accounts/api/login/', data=json.dumps(payload), content_type='application/json')
		_add_session_to_request(req)
		resp = login_api(req)
		self.assertEqual(resp.status_code, 200)

		# wrong password
		payload2 = {'user_id': 'loginuser', 'password': 'wrongpwd'}
		req2 = self.rf.post('/accounts/api/login/', data=json.dumps(payload2), content_type='application/json')
		_add_session_to_request(req2)
		resp2 = login_api(req2)
		self.assertEqual(resp2.status_code, 401)

