from django.test import TestCase


def simple(self, url):
    login = self.client.login(username='u1', password='hello')
    response = self.client.get(url)
    return response.status_code


TestCase.simple = simple
