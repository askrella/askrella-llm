import os
import unittest
from flask import Flask
import json
from app import api

from dotenv import load_dotenv

# Load .env
load_dotenv()

class APITestCase(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.api = api.test_client()

    def get_auth_headers(self):
        return {
            'Authorization': f'Bearer {os.getenv("API_KEY")}'
        }

    def test_0_crawl_endpoint(self):
        # Request
        response = self.api.post('/crawl', headers=self.get_auth_headers(), json={
            "url": "http://example.com"
        })

        # Assertions
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertTrue('urls' in response_data)


    def test_1_create_collection_endpoint(self):
        # Request
        response = self.api.post('/collection/my_collection', headers=self.get_auth_headers())

        # Assertions
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertTrue('success' in response_data)


    def test_2_ingest_collection_endpoint(self):
        # Prepare a test file to send with the request
        with open('test.txt', 'w') as f:
            f.write('Test document')

        # Request
        response = self.api.post('/collection/my_collection/ingest', headers=self.get_auth_headers(), data={
            'file': open('test.txt', 'rb')
        })

        # Assertions
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertTrue('success' in response_data)

        # Clean up the test file
        os.remove('test.txt')
    
    def test_3_query_collection_endpoint(self):
        # Request
        response = self.api.post('/collection/my_collection/query', headers=self.get_auth_headers(), json={
            'prompt': 'example prompt'
        })

        # Print response headers and body
        print(f"Query response: {response.status_code}, {response.data}")

        # Assertions
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertTrue('response' in response_data)

    def test_4_delete_collection_endpoint(self):
        # Request
        response = self.api.delete('/collection/my_collection', headers=self.get_auth_headers())

        # Assertions
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertTrue('success' in response_data)


if __name__ == '__main__':
    unittest.main()
