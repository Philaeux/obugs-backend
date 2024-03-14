Database
==========

ORM
-----

.. mermaid::

    classDiagram
        Software: +String id
        Software: +String full_name
        Software: +String editor
        Software: +String description
        Software: +String language
        Tag: +UUID id
        Tag: +String name
        Tag: +String font_color
        Tag: +String background_color
        Software "1" <-- "*" Tag: tags
        Entry: +UUID id
        Entry: +String title
        Entry: +String description
        Entry: +String illustration
        Entry: +EntryStatus status 
        Entry: +Float rating 
        Entry: +Int rating_total 
        Entry: +Int rating_count
        Entry: +Datetime created_at
        Entry: +Datetime updated_at
        Entry: +Int open_patches_count
        Entry: +Int comment_count
        Software "1" <-- "*" Entry: entries
        Entry "1" <-- "*" Tag: has
        User: +UUID id
        User: +Int github_id
        User: +String github_name
        User: +Int reddit_id
        User: +String reddit_name
        User: +bool is_admin
        User: +bool is_banned
        Vote: +UUID id
        Vote: +Int rating
        User "1" <-- "*" Vote: has
        Entry "1" <-- "*" Vote: on 
        EntryMessage: +UUID id
        Entry "1" <-- "*" EntryMessage: on
        User "1" <-- "*" EntryMessage: author

.. automodule:: obugs.database.entry_message
  :members:

.. automodule:: obugs.database.entry
  :members:

.. automodule:: obugs.database.software_suggestion
  :members:

.. automodule:: obugs.database.software
  :members:

.. automodule:: obugs.database.tag
  :members:

.. automodule:: obugs.database.user_software_role
  :members:

.. automodule:: obugs.database.user
  :members:

.. automodule:: obugs.database.vote
  :members:

To use the database, we use the Database singleton.

.. autoclass:: template.database.database.Database
    :members:

Migrations
-----------

To generate a new database migration (new tables, new columns, deletions, updates...), change the ORM classes first. 
Then, generate the new migration using Alembic::

    poetry run alembic revision --autogenerate

A new migration will appear in ``src/template/alembic/versions``. Update the file accordingly.

It's possible to decide if migrations are automaticaly run at startup. Otherwise, use manual updates::

    # Forward
    poetry run alembic revision +1
    # Backward
    poetry run alembic revision -1
