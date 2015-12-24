import tempfile

import os
import unittest
from kraken import webkraken


class WebKrakenTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, webkraken.app.config['DATABASE'] = tempfile.mkstemp()
        self.app = webkraken.app.test_client()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(webkraken.app.config['DATABASE'])

    def test_hello(self):
        rv = self.app.get('/')
        assert 'Hello from Kraken' in str(rv.data)


if __name__ == '__main__':
    unittest.main()
