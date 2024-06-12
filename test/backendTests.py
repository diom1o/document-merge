import os
import unittest
import requests
from dotenv import load_dotenv
from functools import lru_cache

load_dotenv()

BASE_URL = os.getenv("API_BASE_URL")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
HEADERS = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json"
}

@lru_cache(maxsize=128)
def cached_get_request(url, headers):
    return requests.get(url, headers=headers)

class TestAPIEndpoints(unittest.TestCase):
    def test_get_endpoint(self):
        response = cached_get_request(f"{BASE_URL}/resource", tuple(HEADERS.items()))
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
    
    def test_batch_post_endpoint(self):
        payloads = [{"name": f"Resource {i}", "type": "Example"} for i in range(5)]
        responses = [requests.post(f"{BASE_URL}/resource", headers=HEADERS, json=payload) for payload in payloads]
        
        for response in responses:
            self.assertEqual(response.status_code, 201)
            self.assertIn('name', response.json())
            self.assertIn('type', response.json())

    def test_access_control(self):
        response = cached_get_request(f"{BASE_URL}/protected-resource", tuple({"Content-Type": "application/json"}.items()))
        self.assertIn(response.status_code, [401, 403])


if __name__ == "__main__":
    unittest.main()