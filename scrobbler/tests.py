import uuid
import time
import md5

from django.test import TestCase, Client
from django.contrib.auth.models import User

from .views import HandShake


class ScrobblerTest(TestCase):
    def setUp(self):
        self.username = self.get_random_string()
        self.password = self.get_random_string()
        self.user = User.objects.create_user(self.username, password=self.password)
        self.timestamp = int(time.time())

    def get_random_string(self):
        return str(uuid.uuid4())

    def get_auth_string(self):
        return md5.new(md5.new(self.password).hexdigest() + str(self.timestamp)).hexdigest()

    def test_scrobbler_auth(self):
        hs_view = HandShake()
        self.assertTrue(
            hs_view.auth(self.username, self.get_auth_string(), self.timestamp),
            'Auth with correct credentials'
        )

        self.assertFalse(
            hs_view.auth(self.username, self.get_random_string(), self.timestamp),
            'Auth with incorrect password'
        )

        self.assertFalse(
            hs_view.auth(self.get_random_string(), self.get_random_string(), self.timestamp),
            'Auth with incorrect username'
        )

    def test_handshake_request(self):
        c = Client()
        response = c.get('/scrobbler/handshake/', {
            'u': self.username, 'a': self.get_random_string(), 't': self.timestamp})
        self.assertEqual(response.content, 'BADAUTH', 'Auth request with bad credentials')

        response = c.get('/scrobbler/handshake/', {
            'u': self.get_random_string(), 'a': self.get_auth_string(), 't': self.timestamp})
        self.assertEqual(response.content, 'BADAUTH', 'Auth request with bad credentials')

        response = c.get('/scrobbler/handshake/', {
            'u': self.username, 'a': self.get_auth_string(), 't': self.timestamp})
        status, session, now_playing_url, submission_url = response.content.split("\n")
        self.assertEqual(status, 'OK')
