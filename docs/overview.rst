Overview
========

PyPipe treats a workflow as a small graph of :class:`~pypipe.models.Job`
objects and keeps them inside a :class:`~pypipe.models.Pipeline`.
Each job owns an ordered list of steps and optional dependencies on the
other jobs.  The registry in :mod:`pypipe.registry` stores every
pipeline by name so the CLI and transpilers can look them up later.

Minimal pipeline
----------------

The default pipeline is called ``ci``.  The :func:`pypipe.registry.default_pipeline`
helper returns it and accepts keyword arguments that map directly to
:class:`pypipe.trigger_event.PipelineSettings`.  A practical pipeline
usually consists of at least one ``@job`` function:

.. code-block:: python

   from pypipe.decorators import job
   from pypipe.steps import shell, checkout

   @job()
   def build():
       checkout()
       shell("pip install -r requirements.txt")
       shell("pytest --maxfail=1")

   if __name__ == "__main__":
       # ensure the pipeline exists and optionally tweak triggers
       from pypipe.registry import default_pipeline

       default_pipeline(on_push=["main", "release"], on_pull_request=True)

Pipelines reject duplicate job names and raise on invalid dependency
links.  The underlying topological sort guarantees that the transpiled
workflow follows the declared ``depends_on`` graph.

Trigger configuration
---------------------

``PipelineSettings`` accepts a ``Trigger`` value for ``on_push`` and
``on_pull_request``.  Each trigger can be one of:

* ``"branch-name"`` – a single branch string.
* ``["main", "dev"]`` – a list of branches (empty disables the trigger).
* ``{"branches": ["main"], "paths": ["src/**"]}`` – a raw GitHub
  Actions dictionary for power users.
* ``True`` – enable the event with default filters.
* ``False`` or ``None`` – disable the event.

If no trigger remains after transpiling, PyPipe falls back to ``push`` on
``main`` so you always end up with a valid workflow.
