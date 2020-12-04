'''
Created on Sep. 18, 2020

@author: ikus060
'''
import contextlib
import io
import unittest

from mock import patch
import pkg_resources

from rdiffweb.main import main, _parse_args


@patch('cherrypy.quickstart')
class Test(unittest.TestCase):

    def test_parse_args(self, *args):
        args = _parse_args(['-f', 'myfile.conf'])
        self.assertEqual(args.config, 'myfile.conf')

    def test_main_with_config(self, *args):
        config = pkg_resources.resource_filename('rdiffweb.tests', 'rdw.conf')  # @UndefinedVariable
        main(['-f', config])

    def test_main_without_config(self, *args):
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            with self.assertRaises(SystemExit):
                main([])
        self.assertTrue(f.getvalue().startswith('Fatal Error'), msg='%s' % f.getvalue())

    def test_main_help(self, *args):
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            with self.assertRaises(SystemExit):
                main(['--help'])
        self.assertTrue(f.getvalue().startswith('usage: rdiffweb'), msg='%s is not a help message' % f.getvalue())

    def test_main_version(self, *args):
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            with self.assertRaises(SystemExit):
                main(['--version'])
        self.assertTrue(f.getvalue().startswith('rdiffweb 2.'), msg='%s is not a version' % f.getvalue())


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
