***********
modular-odm
***********

.. image:: https://badge.fury.io/py/modular-odm.png
    :target: http://badge.fury.io/py/modular-odm

.. image:: https://travis-ci.org/CenterForOpenScience/modular-odm.png?branch=develop
    :target: https://travis-ci.org/CenterForOpenScience/modular-odm

A database-agnostic Document-Object Mapper for Python.


Install
=======

.. code-block:: bash

    $ pip install modular-odm


Example Usage with MongoDB
==========================

Defining Models
---------------

.. code-block:: python

    from modularodm import StoredObject, fields
    from modularodm.validators import MinLengthValidator, MaxLengthValidator

    class User(StoredObject):
        _meta = {"optimistic": True}
        _id = fields.StringField(primary=True, index=True)
        username = fields.StringField(required=True)
        password = fields.StringField(required=True, validate=[MinLengthValidator(8)])

        def __repr__(self):
            return "<User: {0}>".format(self.username)

    class Comment(StoredObject):
        _meta = {"optimistic": True}
        _id = fields.StringField(primary=True, index=True)
        text = fields.StringField(validate=MaxLengthValidator(500))
        user = fields.ForeignField("User", backref="comments")

        def __repr__(self):
            return "<Comment: {0}>".format(self.text)


Setting the Storage Backend
---------------------------

.. code-block:: python

    from pymongo import MongoClient
    from modularodm import storage

    client = MongoClient()
    db = client['testdb']
    User.set_storage(storage.MongoStorage(db, collection="user"))
    Comment.set_storage(storage.MongoStorage(db, collection="comment"))

Creating and Querying
---------------------

.. code-block:: python

    >>> from modularodm.query.querydialect import DefaultQueryDialect as Q
    >>> u = User(username="unladenswallow", password="h0lygrai1")
    >>> u.save()
    >>> comment = Comment(text="And now for something completely different.", user=u)
    >>> comment2 = Comment(text="It's just a flesh wound.", user=u)
    >>> comment.save()
    True
    >>> comment2.save()
    True
    >>> u = User.find_one(Q("username", "eq", "unladenswallow"))
    >>> u.comment__comments
    [<Comment: And now for something completely different.>, <Comment: It's just a flesh wound.>]
    >>> c = Comment.find(Q("text", "startswith", "And now"))[0]
    >>> c.text
    'And now for something completely different.'
    
For more information regarding querying syntax, please visit the related readthedocs page at <http://modular-odm.readthedocs.org/en/latest/query_syntax.html>.

Migrations
----------

TODO


*Full documentation coming soon.*

Development
===========

Tests require `nose <http://nose.readthedocs.org/en/latest/>`_, `invoke <http://docs.pyinvoke.org/en/latest/>`_, and MongoDB.

Installing MongoDB
------------------

If you are on MacOSX with `homebrew <http://brew.sh/>`_, run

.. code-block:: bash

    $ brew update
    $ brew install mongodb

Running Tests
-------------

To start mongodb, run

.. code-block:: bash

    $ invoke mongo

Run all tests with

.. code-block:: bash

    $ invoke test
