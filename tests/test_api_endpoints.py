import unittest
from app import create_app

class TestAPIEndpoints(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_routes(self):
        # Web routes
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)

        res = self.client.get('/compare')
        self.assertEqual(res.status_code, 200)

        res = self.client.get('/batch')
        self.assertEqual(res.status_code, 200)

        res = self.client.get('/history')
        self.assertEqual(res.status_code, 200)

        # API history route
        res = self.client.get('/api/history')
        self.assertEqual(res.status_code, 200)
        self.assertIn('items', res.get_json())

if __name__ == '__main__':
    unittest.main()
