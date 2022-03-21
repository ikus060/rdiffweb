'''
Created on Jul. 3, 2019

@author: ikus060
'''

from rdiffweb.test import AppTestCase


class AppTest(AppTestCase):
    def test_version(self):
        """Verify return value of version."""
        self.assertIsNotNone(self.app.version)
