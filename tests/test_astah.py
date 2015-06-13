# -*- coding: utf-8 -*-

import os
import sys
from time import time
from sphinx_testing import with_app
from sphinx_testing.path import path
from sphinxcontrib.astah import Astah

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest


class TestSphinxcontrib(unittest.TestCase):
    def setUp(self):
        self.skip_image_check = os.environ.get('SKIP_IMAGE_CHECK')

    @with_app(buildername='html', srcdir="tests/examples/multipages", copy_srcdir_to_tmpdir=True)
    def test_Astah_extract(self, app, status, warnings):
        Astah(app).extract(app.srcdir / 'multipages.asta', app.outdir)
        self.assertEqual(['multipages'], os.listdir(app.outdir))
        self.assertEqual(['Class Diagram.png', 'Sequence.png'], os.listdir(app.outdir / 'multipages'))

    @with_app(buildername='html', srcdir="tests/examples/multipages", copy_srcdir_to_tmpdir=True)
    def test_Astah_convert(self, app, status, warnings):
        # get first sheet
        ret = Astah(app).convert(app.srcdir / 'multipages.asta',
                                 app.outdir / 'output1.png')
        self.assertEqual(True, ret)
        self.assertIn('output1.png', os.listdir(app.outdir))

        # get sheet with sheet name
        ret = Astah(app).convert(app.srcdir / 'multipages.asta',
                                 app.outdir / 'output2.png',
                                 sheetname='Class Diagram')
        self.assertEqual(True, ret)
        self.assertIn('output2.png', os.listdir(app.outdir))

        # get sheet with unknown sheet name
        ret = Astah(app).convert(app.srcdir / 'multipages.asta',
                                 app.outdir / 'output3.png',
                                 sheetname='unknown')
        self.assertEqual(False, ret)
        self.assertNotIn('output3.png', os.listdir(app.outdir))

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

        if not self.skip_image_check:
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

    @with_app(buildername='html', srcdir="tests/examples/astah_figure", copy_srcdir_to_tmpdir=True)
    def test_astah_figure(self, app, status, warnings):
        app.build()
        print(status.getvalue(), warnings.getvalue())
        html = (app.outdir / 'index.html').read_text()
        image_files = (app.outdir / '_images').listdir()
        self.assertEqual(1, len(image_files))
        image_filename = image_files[0]

        self.assertRegexpMatches(html,
                                 ('<div class="figure".*?>\s*'
                                  '<img alt="(_images/%s)" src="\\1" />\s*'
                                  '<p class="caption">(<span class="caption-text">)?caption of figure(</span>)?</p>\s*'
                                  '</div>'
                                  ) % image_filename)

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

        if not self.skip_image_check:
            expected = path("tests/examples/multipages-2.png").read_bytes()
            actual = (app.outdir / '_images' / image_filename).read_bytes()
            self.assertEqual(expected, actual)

    @with_app(buildername='html', srcdir="tests/examples/image", copy_srcdir_to_tmpdir=True)
    def test_image(self, app, status, warnings):
        app.build()
        print(status.getvalue(), warnings.getvalue())
        html = (app.outdir / 'index.html').read_text()
        image_files = (app.outdir / '_images').listdir()
        self.assertEqual(1, len(image_files))
        image_filename = image_files[0]

        self.assertRegexpMatches(html, '<img alt="(_images/%s)" src="\\1" />' % image_filename)

        if not self.skip_image_check:
            expected = path("tests/examples/animal.png").read_bytes()
            actual = (app.outdir / '_images' / image_filename).read_bytes()
            self.assertEqual(expected, actual)

    @with_app(buildername='html', srcdir="tests/examples/image_option", copy_srcdir_to_tmpdir=True)
    def test_image_option(self, app, status, warnings):
        app.build()
        print(status.getvalue(), warnings.getvalue())
        html = (app.outdir / 'index.html').read_text()
        image_files = (app.outdir / '_images').listdir()
        self.assertEqual(1, len(image_files))
        image_filename = image_files[0]

        self.assertRegexpMatches(html, '<img alt="(_images/%s)" src="\\1" />' % image_filename)

        if not self.skip_image_check:
            expected = path("tests/examples/multipages-2.png").read_bytes()
            actual = (app.outdir / '_images' / image_filename).read_bytes()
            self.assertEqual(expected, actual)

    @with_app(buildername='html', srcdir="tests/examples/figure", copy_srcdir_to_tmpdir=True)
    def test_figure(self, app, status, warnings):
        app.build()
        print(status.getvalue(), warnings.getvalue())
        html = (app.outdir / 'index.html').read_text()
        image_files = (app.outdir / '_images').listdir()
        self.assertEqual(1, len(image_files))
        image_filename = image_files[0]

        self.assertRegexpMatches(html,
                                 ('<div class="figure".*?>\s*'
                                  '<img alt="(_images/%s)" src="\\1" />\s*'
                                  '<p class="caption">(<span class="caption-text">)?caption of figure(</span>)?</p>\s*'
                                  '</div>'
                                  ) % image_filename)

        if not self.skip_image_check:
            expected = path("tests/examples/animal.png").read_bytes()
            actual = (app.outdir / '_images' / image_filename).read_bytes()
            self.assertEqual(expected, actual)
