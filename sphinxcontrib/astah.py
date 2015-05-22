import os
import subprocess
import pkg_resources
from glob import glob
from hashlib import sha1
from tempfile import mkdtemp
from shutil import copyfile, rmtree
from docutils import nodes
from docutils.parsers.rst.directives.images import Image, Figure
from sphinx.util.osutil import ensuredir, relative_uri


class AstahException(Exception):
    pass


def if_outdated(fn):
    def wrap(self, filename, to, **kwargs):
        if is_outdated(filename, to):
            return fn(self, filename, to, **kwargs)
        else:
            return True

    return wrap


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

    @if_outdated
    def convert(self, filename, to, sheetname=None):
        try:
            tmpdir = mkdtemp()
            self.extract(filename, tmpdir)

            subdirname = os.path.splitext(os.path.basename(filename))[0]
            imagedir = os.path.join(tmpdir, subdirname)
            if sheetname:
                target = os.path.join(imagedir, sheetname + '.png')
            else:
                target = os.path.join(imagedir, os.listdir(imagedir)[0])  # first item in archive

            if os.path.exists(target):
                ensuredir(os.path.dirname(to))
                copyfile(target, to)
                last_modified = os.stat(filename).st_mtime
                os.utime(to, (last_modified, last_modified))
                return True
            else:
                self.warn('Fail to convert astah image: unknown sheet [%s]' % self['sheet'])
                return False
        except AstahException:
            return False
        except Exception as exc:
            self.warn('Fail to convert astah image: %s' % exc)
            return False
        finally:
            rmtree(tmpdir, ignore_errors=True)


def get_imagedir(app, docname):
    if hasattr(app.builder, 'imagedir'):  # Sphinx (>= 1.3.x)
        dirname = app.builder.imagedir
    elif hasattr(app.builder, 'imgpath') or app.builder.format == 'html':  # Sphinx (<= 1.2.x) and HTML writer
        dirname = '_images'
    else:
        dirname = ''

    if dirname:
        relpath = relative_uri(app.builder.get_target_uri(docname), dirname)
    else:
        relpath = ''

    abspath = os.path.join(app.builder.outdir, dirname)
    return (relpath, abspath)


def is_outdated(astah_path, png_path):
    if not os.path.exists(astah_path):
        return False
    else:
        last_modified = os.stat(astah_path).st_mtime
        if not os.path.exists(png_path) or os.stat(png_path).st_mtime < last_modified:
            return True
        else:
            return False


class astah_image(nodes.General, nodes.Element):
    pass


def visit_astah_image(app, docname, node):
    rel_imagedir, abs_imagedir = get_imagedir(app, docname)

    hashed = sha1((node['uri'] + node.get('sheet', '')).encode('utf-8')).hexdigest()
    filename = "astah-%s.png" % hashed
    path = os.path.join(abs_imagedir, filename)

    astah_filename = os.path.join(app.srcdir, node['uri'])
    ret = Astah(app).convert(astah_filename, path, sheetname=node.get('sheet'))
    if ret is False:
        node.replace_self(nodes.Text(''))

    relfn = os.path.join(rel_imagedir, filename)
    image_node = nodes.image(**node.attributes)
    image_node['candidates'] = {'*': relfn}
    image_node['uri'] = relfn

    node.replace_self(image_node)


class AstahImageMixIn(object):
    def run(self):
        result = super(AstahImageMixIn, self).run()
        if '#' in self.arguments[0]:
            filename, sheet = self.arguments[0].split('#', 1)
        else:
            filename = self.arguments[0]
            sheet = ''

        env = self.state.document.settings.env
        path = env.doc2path(env.docname, base=None)
        rel_filename = os.path.join(os.path.dirname(path), filename)
        filename = os.path.join(env.srcdir, rel_filename)
        if not os.access(filename, os.R_OK):
            raise self.warning('astah file not readable: %s' % self.arguments[0])

        env.note_dependency(rel_filename)
        if isinstance(result[0], nodes.image):
            image = astah_image(sheet=sheet, **result[0].attributes)
            image['uri'] = rel_filename
            result[0] = image
        else:
            for node in result[0].traverse(nodes.image):
                image = astah_image(sheet=sheet, **node.attributes)
                image['uri'] = rel_filename
                node.replace_self(image)

        return result


class AstahImage(AstahImageMixIn, Image):
    pass


class AstahFigure(AstahImageMixIn, Figure):
    pass


def on_builder_inited(app):
    from docutils.parsers.rst import directives
    from docutils.parsers.rst.directives.images import Image, Figure

    Image.option_spec['option'] = directives.unchanged
    Figure.option_spec['option'] = directives.unchanged


def on_doctree_read(app, doctree):
    import cgi
    for image in doctree.traverse(nodes.image):
        if 'option' in image:
            options = cgi.parse_qs(image.get('option'))
            for name, option in options.items():
                image[name] = option.pop()


def on_doctree_resolved(app, doctree, docname):
    for astah in doctree.traverse(astah_image):
        visit_astah_image(app, docname, astah)

    for image in doctree.traverse(nodes.image):
        if image['uri'].lower().endswith('.asta'):
            visit_astah_image(app, docname, image)


def setup(app):
    app.add_node(astah_image)
    app.add_directive('astah-image', AstahImage)
    app.add_directive('astah-figure', AstahFigure)
    app.connect('builder-inited', on_builder_inited)
    app.connect('doctree-read', on_doctree_read)
    app.connect('doctree-resolved', on_doctree_resolved)

    app.add_config_value('astah_command_path', None, 'html')
    return {
        'version': pkg_resources.require('sphinxcontrib-astah')[0].version,
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
