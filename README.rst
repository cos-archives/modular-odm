***********
modular-odm
***********

.. image:: https://badge.fury.io/py/modular-odm.png
    :target: http://badge.fury.io/py/modular-odm

A database-agnostic Document-Object Mapper for Python.


Install
=======

.. code-block:: bash

    $ pip install modular-odm


Example Usage with MongoDb
==========================

Defining Models
---------------

.. code-block:: python

    from modularodm import StoredObject, storage, fields
    from modularodm.validators import MinLengthValidator, MaxLengthValidator

    class User(StoredObject):
        _id = fields.StringField(primary=True)
        username = fields.StringField(required=True)
        password = fields.StringField(required=True, validate=[MinLengthValidator(8)])

    class Comment(StoredObject):
        _id = fields.StringField(primary=True, index=True)
        text = fields.StringField(validate=MaxLengthValidator(500))
        user = fields.ForeignField("User", backref="comments")


Setting the Storage Backend
---------------------------

.. code-block:: python

    from pymongo import MongoClient

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
    >>> comment.save()
    >>> u = User.find_one(Q("username", "eq", "unladenswallow"))
    >>> u.username
    u'unladenswallow'
    >>> c = Comment.find(Q("text", "startswith", "And now"))[0]
    >>> c.text
    u'And now for something completely different.'

*Full documentation coming soon.*

Running Tests
=============

Tests require `nose <http://nose.readthedocs.org/en/latest/>`_.

.. code-block:: bash

    $ nosetests
