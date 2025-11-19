Command Line Interface
=========================

The :mod:`pypipe.cli` module exposes a ``pypipe`` console script with a
single ``build`` sub-command.  It scans a source directory for pipeline
files, executes them to populate the registry, and transpiles each
registered pipeline to GitHub Actions YAML.

Usage
--------

.. code-block:: console

   $ pypipe build --src-dir .pipe --out-dir .github/workflows --clean

Options
----------

``--src-dir``
   Defaults to ``.pipe``.  Every file matching ``pipeline_*.py`` or
   ``*_pipeline.py`` in this directory is executed with :mod:`runpy`.

``--out-dir``
   Defaults to ``.github/workflows``.  For each registered pipeline a
   ``<name>.yml`` file is written using :class:`pypipe.transpilers.github.GitHubTranspiler`.

``--clean``
   Deletes orphaned YAML files from the output directory unless they
   start with ``# pypipe: keep`` within the first ten lines.  This is a
   useful safety valve when rotating pipelines.

Exit status
-------------

``cmd_build`` returns ``0`` even when no pipelines were registered so the
command is safe to run in empty repositories.  Any exception raised while
executing a pipeline file or running the transpiler will propagate to the
caller, giving CI runners immediate feedback.
