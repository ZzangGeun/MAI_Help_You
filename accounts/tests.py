import json

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

	def test_signup_success(self):
		payload = {'user_id': 'testuser1', 'password': 'Aa1!aaaa', 'nickname': '테스터1'}
		req = self.rf.post('/accounts/api/signup/', data=json.dumps(payload), content_type='application/json')
		resp = signup_api(req)
		self.assertEqual(resp.status_code, 201)
		data = json.loads(resp.content)
		self.assertEqual(data.get('status'), 'success')
		self.assertEqual(data['user']['user_id'], 'testuser1')
		self.assertEqual(data['user']['nickname'], '테스터1')
		self.assertTrue(User.objects.filter(username='testuser1').exists())
		self.assertTrue(UserProfile.objects.filter(maple_nickname='테스터1').exists())

	def test_signup_invalid_userid(self):
		payload = {'user_id': 'bad@id', 'password': 'Aa1!aaaa', 'nickname': '닉네임'}
		req = self.rf.post('/accounts/api/signup/', data=json.dumps(payload), content_type='application/json')
		resp = signup_api(req)
		self.assertEqual(resp.status_code, 400)
		data = json.loads(resp.content)
		self.assertEqual(data.get('status'), 'error')

	def test_signup_weak_password(self):
		payload = {'user_id': 'okuser', 'password': 'password', 'nickname': '닉네임2'}
		req = self.rf.post('/accounts/api/signup/', data=json.dumps(payload), content_type='application/json')
		resp = signup_api(req)
		self.assertEqual(resp.status_code, 400)
		data = json.loads(resp.content)
		self.assertEqual(data.get('status'), 'error')

	def test_signup_duplicate_user_or_nickname(self):
		# create user with same username
		User.objects.create_user(username='dupuser', password='Aa1!aaaa')
		payload = {'user_id': 'dupuser', 'password': 'Aa1!aaaa', 'nickname': 'unique1'}
		req = self.rf.post('/accounts/api/signup/', data=json.dumps(payload), content_type='application/json')
		resp = signup_api(req)
		self.assertEqual(resp.status_code, 400)
		data = json.loads(resp.content)
		self.assertEqual(data.get('status'), 'error')

		# create profile with nickname
		u = User.objects.create_user(username='userx', password='Aa1!aaaa')
		UserProfile.objects.create(user=u, maple_nickname='same_nick')

		payload2 = {'user_id': 'newuser', 'password': 'Aa1!aaaa', 'nickname': 'same_nick'}
		req2 = self.rf.post('/accounts/api/signup/', data=json.dumps(payload2), content_type='application/json')
		resp2 = signup_api(req2)
		self.assertEqual(resp2.status_code, 400)
		data2 = json.loads(resp2.content)
		self.assertEqual(data2.get('status'), 'error')

	def test_login_success_and_failure(self):
		# create user
		user = User.objects.create_user(username='loginuser', password='Login1!')

		# successful login
		payload = {'user_id': 'loginuser', 'password': 'Login1!'}
		req = self.rf.post('/accounts/api/login/', data=json.dumps(payload), content_type='application/json')
		_add_session_to_request(req)
		resp = login_api(req)
		self.assertEqual(resp.status_code, 200)
		data = json.loads(resp.content)
		self.assertEqual(data.get('status'), 'success')

		# wrong password
		payload2 = {'user_id': 'loginuser', 'password': 'wrongpwd'}
		req2 = self.rf.post('/accounts/api/login/', data=json.dumps(payload2), content_type='application/json')
		_add_session_to_request(req2)
		resp2 = login_api(req2)
		self.assertEqual(resp2.status_code, 401)
		data2 = json.loads(resp2.content)
		self.assertEqual(data2.get('status'), 'error')

	def test_logout_requires_authenticated(self):
		# logout without authenticated user
		req = self.rf.post('/accounts/api/logout/', content_type='application/json')
		_add_session_to_request(req)
		req.user = type('U', (), {'is_authenticated': False})()
		resp = logout_api(req)
		self.assertEqual(resp.status_code, 401)

		# logout with authenticated user
		user = User.objects.create_user(username='u2', password='Aa1!aaaa')
		req2 = self.rf.post('/accounts/api/logout/', content_type='application/json')
		_add_session_to_request(req2)
		req2.user = user
		resp2 = logout_api(req2)
		self.assertEqual(resp2.status_code, 200)
