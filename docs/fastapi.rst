FastAPI
========

Periodic Tasks
---------------

It's possible to create periodic tasks. Use this function decorator:
    
.. autofunction:: obugs.utils.repeat_every.repeat_every

And then call this function in the lifecycle function:

.. autofunction:: obugs.backend.lifecycle

GraphQL
--------

Schema
^^^^^^^

Schema defined for the GraphQL endpoint:

.. automodule:: obugs.graphql.schema
    :members:

Types Input & Output
^^^^^^^^^^^^^^^^^^^^^^

I recommend creating files to store Input and Output types of the GraphQL endpoints, in files like ``src/obugs/graphql/types/a.py``.

These types are used:

.. automodule:: obugs.graphql.types.generic
    :members:


Generated Types
^^^^^^^^^^^^^^^^

These types are generated from ORM objects. When a query/mutation return an ORM type, it's automaticaly turned into a GraphQL type.

.. automodule:: obugs.graphql.types.generated
    :members:

REST API
----------

It is possible to create classic REST endpoints instead of using the GraphQL endpoint. OAuth start/callbacks are REST endpoints:

.. autofunction:: obugs.backend.oauth_github_start

.. autofunction:: obugs.backend.oauth_github_callback

.. autofunction:: obugs.backend.oauth_reddit_start

.. autofunction:: obugs.backend.oauth_reddit_callback
