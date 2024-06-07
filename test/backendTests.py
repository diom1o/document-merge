import os
import json
import unittest
import requests
from dotenv import load_dotenv
load_dotenv()
BASE_URL = os.getenv("API_BASE_URL")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")  
HEADERS = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json"
}
class TestAPIEndpoints(unittest.TestCase):
    def test_get_endpoint(self):
        response = requests.get(f"{BASE_URL}/resource", headers=HEADERS)
        self.assertEqual(response.status_code, 200)
    def test_post_endpoint(self):
        payload = {"name": "New Resource", "type": "Example"}
        response = requests.post(f"{BASE_URL}/resource", headers=HEADERS, json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['name'], payload['name'])
        self.assertEqual(response.json()['type'], payload['type'])
    def test_put_endpoint(self):
        update_payload = {"name": "Updated Resource"}
        response = requests.put(f"{BASE_URL}/resource/1", headers=HEADERS, json=update_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['name'], update_payload['name'])
    def test_delete_endpoint(self):
        response = requests.delete(f"{BASE_URL}/resource/1", headers=HEADERS)
        self.assertEqual(response.status_code, 204)
    def test_access_control(self):
        no_auth_headers = {"Content-Type": "application/json"}
        response = requests.get(f"{BASE_URL}/protected-resource", headers=no_auth_headers)
        self.assertIn(response.status_code, [401, 403])
if __name__ == "__main__":
    unittest.main()