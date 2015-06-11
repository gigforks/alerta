import json
import unittest

from alerta.app import app


class AppTestCase(unittest.TestCase):

    def setUp(self):

        app.config['TESTING'] = True
        self.app = app.test_client()

        self.alert = {
            'event': 'Foo',
            'resource': 'Bar',
            'environment': 'Production',
            'service': ['Quux']
        }

    def tearDown(self):

        pass

    def test_debug_output(self):

        response = self.app.get('/_')
        self.assertEqual(response.status_code, 200)
        self.assertIn("ok", response.data)

    def test_new_alert(self):

        response = self.app.post('/alert', data=json.dumps(self.alert), headers={'Content-type': 'application/json'})
        data = json.loads(response.data)
        self.assertListEqual(self.alert['service'], data['alert']['service'])

        new_alert_id = data['id']

        response = self.app.get('/alert/' + new_alert_id)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn(new_alert_id, data['alert']['id'])

    def test_alert_not_found(self):

        response = self.app.get('/alert/doesnotexist')
        self.assertEqual(response.status_code, 404)

    # def test_get_alerts(self):
    #
    #     response = self.app.get('/alerts')
    #     self.assertIn("asldfjasdlfkjasdf", response.data)

