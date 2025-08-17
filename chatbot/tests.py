from django.test import TestCase, Client
from django.urls import reverse
import json


class ChatbotEndpointsTest(TestCase):
	def setUp(self):
		self.client = Client()

	def test_health(self):
		resp = self.client.get("/chatbot/health/")
		self.assertIn(resp.status_code, (200, 503))

	def test_ask_and_history_flow(self):
		# ask without question -> 400
		resp = self.client.post("/chatbot/ask/", data=json.dumps({}), content_type="application/json")
		self.assertEqual(resp.status_code, 400)

		# ask with question
		resp = self.client.post(
			"/chatbot/ask/",
			data=json.dumps({"question": "테스트 질문"}),
			content_type="application/json",
		)
		self.assertEqual(resp.status_code, 200)
		data = resp.json()
		self.assertIn("response", data)
		user_id = data.get("user_id")

		# history
		resp = self.client.get(f"/chatbot/history/?user_id={user_id}")
		self.assertEqual(resp.status_code, 200)
		self.assertIn("history", resp.json())

		# clear history
		resp = self.client.post(
			"/chatbot/clear-history/",
			data=json.dumps({"user_id": user_id}),
			content_type="application/json",
		)
		self.assertEqual(resp.status_code, 200)

# Create your tests here.
