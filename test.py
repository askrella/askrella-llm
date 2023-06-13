import os
import unittest
from flask import Flask
import json
from app import api

from dotenv import load_dotenv

# Load .env
load_dotenv()

# Test files
test_text_file = './test_files/example.txt'
test_audio_file = './test_files/example.wav'

# Test
class APITestCase(unittest.TestCase):

    # Setup flask app
    def setUp(self):
        self.app = Flask(__name__)
        self.api = api.test_client()

    # Headers
    def get_auth_headers(self):
        return {
            'Authorization': f'Bearer {os.getenv("API_KEY")}'
        }
    
    # Test auth
    def test_0_auth(self):
        # Request
        response = self.api.post('/crawl', json={
            "url": "http://example.com"
        })

        # Assertions
        self.assertEqual(response.status_code, 401)
        response_data = json.loads(response.data)
        self.assertTrue('error' in response_data)

    def test_1_crawl_endpoint(self):
        # Request
        response = self.api.post('/crawl', headers=self.get_auth_headers(), json={
            "url": "http://example.com"
        })

        # Assertions
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertTrue('urls' in response_data)

    def test_2_create_collection_endpoint(self):
        # Request
        response = self.api.post('/collection/my_collection', headers=self.get_auth_headers())

        # Assertions
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertTrue('success' in response_data)

    def test_3_ingest_text_file(self):
        # Request
        response = self.api.post('/collection/my_collection/ingest', headers=self.get_auth_headers(), data={
            'file': open(test_text_file, 'rb')
        })

        # Assertions
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertTrue('success' in response_data)
    
    def test_4_ingest_audio_file(self):
        # Request
        response = self.api.post('/collection/my_collection/ingest', headers=self.get_auth_headers(), data={
            'file': open(test_audio_file, 'rb')
        })

        # Assertions
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertTrue('success' in response_data)

    def test_5_query(self):
        # Request
        response = self.api.post('/collection/my_collection/query', headers=self.get_auth_headers(), json={
            'prompt': 'Wer ist cool?'
        })

        # Assertions
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertTrue('response' in response_data)

    def test_6_delete(self):
        # Request
        response = self.api.delete('/collection/my_collection', headers=self.get_auth_headers())

        # Assertions
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertTrue('success' in response_data)

if __name__ == '__main__':
    unittest.main()
