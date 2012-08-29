WTForms-JSON
========================================

WTForms-JSON is a WTForms extension for JSON data handling.

Quickstart
----------

In order to start using WTForms-JSON, you need to first initialize the
extension. This monkey patches some classes and methods within WTForms and
adds json handling support. ::

    import wtforms_json

    wtforms_json.init()


First Example
-------------

After the extension has been initialized we can create an ordinary WTForms
form. Notice we are using MultiDict from werkzeug.datastructures. We could be
using any MultiDict like object which has getlist() method (for example
Django's QueryDict).::


    from wtforms import Form
    from wtforms.field import BooleanField, TextField
    from wtforms.validators import Required
    from werkzeug.datastructures import MultiDict


    class LocationForm(Form):
        name = TextField(validators=[Required()])
        address = TextField()


    class EventForm(Form):
        name = TextField(validators=[Required()])
        is_public = BooleanField()


    json = {
        'name': 'First Event',
        'location': {'name': 'some location'},
    }

    form = MyForm(MultiDict(flatten_json(json)))

Using patch_data
----------------
The way forms usually work on websites is that they post all the data within
their fields. When working with APIs and JSON data it makes sense to
not actually post all the data that hasn't changed - rather make so called
patch request which only post the data that the user actually changed.

You can get access to the patch data (data that only contains the actually set
fields or fields that have defaults and are required) with form's patch_data
property.
::

    form.patch_data


Using flatten_dict
------------------

WTForms uses special flattened dict as a data parameter for forms. WTForms-JSON
provides a method for converting JSON into this format.
::

    from wtforms_json import flatten_dict

    flatten_dict({'a': {'b': 'c'}})
    >>> {'a-b': 'c'}

This neat little function understands nested lists and dicts as well.
::
    from wtforms_json import flatten_dict

    deep_dict = {
        'a': [{'b': {'c': 1}}, {'c': 2}]
    }

    flatten_dict(deep_dict)
    >>> {'a-0-b-c': 1, 'a-1-c': 2}
