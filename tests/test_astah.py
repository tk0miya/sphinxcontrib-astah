# -*- coding: utf-8 -*-

import sys
from time import time
from sphinx_testing import with_app
from sphinx_testing.path import path

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest


class TestSphinxcontrib(unittest.TestCase):
    @with_app(buildername='html', srcdir="tests/examples/basic", copy_srcdir_to_tmpdir=True)
    def test_astah(self, app, status, warnings):
        # first build
        app.build()
        print(status.getvalue(), warnings.getvalue())
        html = (app.outdir / 'index.html').read_text()
        image_files = (app.outdir / '_images').listdir()
        self.assertEqual(1, len(image_files))
        image_filename = image_files[0]

        self.assertRegexpMatches(html, '<img alt="(_images/%s)" src="\\1" />' % image_filename)

        expected = path("tests/examples/animal.png").read_bytes()
        actual = (app.outdir / '_images' / image_filename).read_bytes()
        self.assertEqual(expected, actual)

        # second build (no updates)
        status.truncate(0)
        warnings.truncate(0)
        app.build()

        self.assertIn('0 added, 0 changed, 0 removed', status.getvalue())

        # thrid build (.vsdx file has changed)
        status.truncate(0)
        warnings.truncate(0)
        (app.srcdir / 'animal.asta').utime((time(), time()))
        app.build()

        self.assertIn('0 added, 1 changed, 0 removed', status.getvalue())

    @with_app(buildername='html', srcdir="tests/examples/subdir", copy_srcdir_to_tmpdir=True)
    def test_astah_in_subdir(self, app, status, warnings):
        app.build()
        print(status.getvalue(), warnings.getvalue())
        html = (app.outdir / 'subdir' / 'index.html').read_text()
        image_files = (app.outdir / '_images').listdir()
        self.assertEqual(1, len(image_files))
        image_filename = image_files[0]

        self.assertRegexpMatches(html, '<img alt="(../_images/%s)" src="\\1" />' % image_filename)

    @with_app(buildername='html', srcdir="tests/examples/multipages", copy_srcdir_to_tmpdir=True)
    def test_astah_with_sheet(self, app, status, warnings):
        app.build()
        print(status.getvalue(), warnings.getvalue())
        html = (app.outdir / 'index.html').read_text()
        image_files = (app.outdir / '_images').listdir()
        self.assertEqual(1, len(image_files))
        image_filename = image_files[0]

        self.assertRegexpMatches(html, '<img alt="(_images/%s)" src="\\1" />' % image_filename)

        expected = path("tests/examples/multipages-2.png").read_bytes()
        actual = (app.outdir / '_images' / image_filename).read_bytes()
        self.assertEqual(expected, actual)
