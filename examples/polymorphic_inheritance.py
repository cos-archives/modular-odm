"""Example of using polymorphic inheritance features to keep multiple related
models in a single collection"""

import uuid

from modularodm import InheritableStoredObject, fields
from modularodm.storage import EphemeralStorage


class Car(InheritableStoredObject):
    _id = fields.StringField(primary=True, default=uuid.uuid4)

    brand = None

    doors = None


class Ford(Car):
    brand = "Ford"


class FordFocus(Ford):
    doors = 4


storage = EphemeralStorage()
for cls in (Car, Ford, FordFocus):
    cls.set_storage(storage)


generic_car = Car()
generic_car.save()

generic_ford = Ford()
generic_ford.save()

ford_focus = FordFocus()
ford_focus.save()


# All three cars have been saved
assert Car.find().count() == 3

# Only two of the cars were Fords
assert Ford.find().count() == 2

# Only one was a Focus
assert FordFocus.find().count() == 1

# Each item returned is an instance of its most specific type
for car in Car.find():
    print(car.__class__)
