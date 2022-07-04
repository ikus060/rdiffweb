'''
Created on Jul. 3, 2019

@author: ikus060
'''

import rdiffweb.test


class AppTest(rdiffweb.test.WebCase):
    def test_version(self):
        """Verify return value of version."""
        self.assertIsNotNone(self.app.version)
