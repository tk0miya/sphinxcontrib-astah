sphinxcontrib-astah
====================

.. image:: https://travis-ci.org/tk0miya/sphinxcontrib-astah.svg?branch=master
   :target: https://travis-ci.org/tk0miya/sphinxcontrib-astah

.. image:: https://coveralls.io/repos/tk0miya/sphinxcontrib-astah/badge.png?branch=master
   :target: https://coveralls.io/r/tk0miya/sphinxcontrib-astah?branch=master

.. image:: https://codeclimate.com/github/tk0miya/sphinxcontrib-astah/badges/gpa.svg
   :target: https://codeclimate.com/github/tk0miya/sphinxcontrib-astah

This package contains the astah Sphinx extension.

This extension enable you to embed diagrams by astah_ .
Following code is sample::

  .. image:: [filename]

  .. astah-image:: [filename]

  .. astah-figure:: [filename]

     caption of figure

.. _astah: http://astah.change-vision.com/

Setting
=======

Install
-------

::

   $ pip install sphinxcontrib-astah


This extension uses astah from commandline. You need to setup astah and Java package.


Configure Sphinx
----------------

Add ``sphinxcontrib.astah`` to ``extensions`` at `conf.py`::

   extensions += ['sphinxcontrib.astah']

And set your API key to ``astah_command_path``::

   astah_command_path = '/path/to/astah-command.sh'


Directive
=========

`.. image:: [filename]`, `.. figure:: [filename]`

  With this extension, `image` and `figure` directives can embed astah image to documents.
  At the same time, the directives accept `sheet` parameter through `:option:` option.

  Examples::

    .. image:: my-diagram.asta

    .. figure:: my-diagram.asta

       caption

    .. image:: my-diagram.asta
       :option: sheet=class-diagram

`.. astah-image:: [filename]`

  This directive insert a diagram into the document.
  If your diagram has multiple sheets, specify sheetid after ``#``.

  Examples::

    .. astah-image:: my-diagram.asta

    .. astah-image:: my-diagram.asta#class-diagram

  Options are same as `image directive`_ .

`.. astah-figure:: [filename]`

  This directive insert a diagram and its caption into the document.

  Examples::

    .. astah-figure:: my-diagram.asta

       Structure of this system

  Options are same as `figure directive`_ .

.. _image directive: http://docutils.sourceforge.net/docs/ref/rst/directives.html#image
.. _figure directive: http://docutils.sourceforge.net/docs/ref/rst/directives.html#figure

Configuration Options
======================

astah_command_path

  path to astah-command.sh (or astah-command.bat)
