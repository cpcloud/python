"""Tests for distutils.command.upload."""
import sys
import os
import unittest

from distutils.command import upload as upload_mod
from distutils.command.upload import upload
from distutils.core import Distribution

from distutils.tests import support
from distutils.tests.test_config import PYPIRC, PyPIRCCommandTestCase

PYPIRC_NOPASSWORD = """\
[distutils]

index-servers =
    server1

[server1]
username:me
"""

class FakeOpen(object):

    def __init__(self, url):
        self.url = url
        if not isinstance(url, str):
            self.req = url
        else:
            self.req = None
        self.msg = 'OK'

    def getcode(self):
        return 200


class uploadTestCase(PyPIRCCommandTestCase):

    def setUp(self):
        super(uploadTestCase, self).setUp()
        self.old_open = upload_mod.urlopen
        upload_mod.urlopen = self._urlopen
        self.last_open = None

    def tearDown(self):
        upload_mod.urlopen = self.old_open
        super(uploadTestCase, self).tearDown()

    def _urlopen(self, url):
        self.last_open = FakeOpen(url)
        return self.last_open

    def test_finalize_options(self):

        # new format
        self.write_file(self.rc, PYPIRC)
        dist = Distribution()
        cmd = upload(dist)
        cmd.finalize_options()
        for attr, waited in (('username', 'me'), ('password', 'secret'),
                             ('realm', 'pypi'),
                             ('repository', 'http://pypi.python.org/pypi')):
            self.assertEquals(getattr(cmd, attr), waited)

    def test_saved_password(self):
        # file with no password
        self.write_file(self.rc, PYPIRC_NOPASSWORD)

        # make sure it passes
        dist = Distribution()
        cmd = upload(dist)
        cmd.finalize_options()
        self.assertEquals(cmd.password, None)

        # make sure we get it as well, if another command
        # initialized it at the dist level
        dist.password = 'xxx'
        cmd = upload(dist)
        cmd.finalize_options()
        self.assertEquals(cmd.password, 'xxx')

    def test_upload(self):
        tmp = self.mkdtemp()
        path = os.path.join(tmp, 'xxx')
        self.write_file(path)
        command, pyversion, filename = 'xxx', '2.6', path
        dist_files = [(command, pyversion, filename)]
        self.write_file(self.rc, PYPIRC)

        # lets run it
        pkg_dir, dist = self.create_dist(dist_files=dist_files)
        cmd = upload(dist)
        cmd.ensure_finalized()
        cmd.run()

        # what did we send ?
        headers = dict(self.last_open.req.headers)
        self.assertEquals(headers['Content-length'], '2087')
        self.assert_(headers['Content-type'].startswith('multipart/form-data'))
        self.assertEquals(self.last_open.req.get_method(), 'POST')
        self.assertEquals(self.last_open.req.get_full_url(),
                          'http://pypi.python.org/pypi')
        self.assert_(b'xxx' in self.last_open.req.data)

def test_suite():
    return unittest.makeSuite(uploadTestCase)

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
