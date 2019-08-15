import os
import subprocess
import pkg_resources
from glob import glob
from hashlib import sha1
from tempfile import mkdtemp
from shutil import copyfile, rmtree
from docutils.parsers.rst import directives
from sphinx.util.osutil import ensuredir
from sphinxcontrib.imagehelper import (
    ImageConverter, add_image_type, generate_image_directive, generate_figure_directive
)


class AstahException(Exception):
    pass


class Astah(object):
    def __init__(self, app):
        self.astah_command_path = app.config.astah_command_path
        self.warn = app.warn

    @property
    def command_path(self):
        if self.astah_command_path:
            return self.astah_command_path

        patterns = ['/Applications/astah*/astah-command.sh']  # Mac OS X
        for pattern in patterns:
            for path in glob(pattern):
                if os.path.exists(path):
                    return path

        return None

    def extract(self, filename, dir):
        if self.command_path is None:
            self.warn('astah-command.sh (or .bat) not found. set astah_command_path in your conf.py')
            raise AstahException

        command_args = [self.command_path, '-image', 'all', '-f', filename, '-o', dir]
        retcode = subprocess.call(command_args)
        if retcode != 0:
            self.warn('Fail to convert astah image (exitcode: %s)' % retcode)
            raise AstahException

    def convert(self, filename, to, sheetname=None):
        try:
            tmpdir = mkdtemp()
            self.extract(filename, tmpdir)

            subdirname = os.path.splitext(os.path.basename(filename))[0]
            imagedir = os.path.join(tmpdir, subdirname)
            if sheetname:
                for root, dirs, files in os.walk(imagedir):
                    if sheetname + '.png' in files:
                        target = os.path.join(root, sheetname + '.png')

            else:
                target = os.path.join(imagedir, os.listdir(imagedir)[0])  # first item in archive

            if os.path.exists(target):
                ensuredir(os.path.dirname(to))
                copyfile(target, to)
                return True
            else:
                self.warn('Fail to convert astah image: unknown sheet [%s]' % sheetname)
                return False
        except AstahException:
            return False
        except Exception as exc:
            self.warn('Fail to convert astah image: %s' % exc)
            return False
        finally:
            rmtree(tmpdir, ignore_errors=True)

Image = generate_image_directive('astah')
Figure = generate_figure_directive('astah')


class AstahMixIn(object):
    def prerun(self):
        if '#' in self.arguments[0]:
            filename, sheetname = self.arguments[0].split('#', 1)
            self.arguments[0] = filename
            self.sheetname = sheetname
        else:
            self.sheetname = None

    def postrun(self, node):
        node['sheet'] = self.sheetname or ''


class AstahImage(AstahMixIn, Image):
    pass


class AstahFigure(AstahMixIn, Figure):
    pass


class AstahImageConverter(ImageConverter):
    option_spec = {
        'sheet': directives.unchanged
    }

    def get_filename_for(self, node):
        hashed = sha1((node['uri'] + node.get('sheet', '')).encode('utf-8')).hexdigest()
        return "astah-%s.png" % hashed

    def convert(self, node, filename, to):
        return Astah(self.app).convert(filename, to, sheetname=node.get('sheet'))


def setup(app):
    add_image_type(app, 'astah', 'asta', AstahImageConverter)

    app.add_directive('astah-image', AstahImage)
    app.add_directive('astah-figure', AstahFigure)
    app.add_config_value('astah_command_path', None, 'html')

    return {
        'version': pkg_resources.require('sphinxcontrib-astah')[0].version,
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
