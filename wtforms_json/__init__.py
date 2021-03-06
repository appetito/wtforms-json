import collections

from wtforms import Form
from wtforms.fields import BooleanField, Field, FormField, _unset_value
from wtforms.validators import Optional, Required


def flatten_json(json, parent_key='', separator='-'):
    """Flattens given JSON dict to cope with WTForms dict structure.

    :param json: json to be converted into flat WTForms style dict
    :param parent_key: this argument is used internally be recursive calls
    :param separator: default separator

    Examples::

        flatten_json({'a': {'b': 'c'}})
        >>> {'a-b': 'c'}
    """
    items = []
    for key, value in json.items():
        new_key = parent_key + separator + key if parent_key else key
        if isinstance(value, collections.MutableMapping):
            items.extend(flatten_json(value, new_key).items())
        elif isinstance(value, list):
            items.extend(flatten_json_list(value, new_key))
        else:
            items.append((new_key, value))
    return dict(items)


def flatten_json_list(json, parent_key='', separator='-'):
    items = []
    i = 0
    for item in json:
        new_key = parent_key + separator + str(i)
        if isinstance(item, list):
            items.extend(flatten_json_list(item, new_key, separator))
        elif isinstance(item, dict):
            items.extend(flatten_json(item, new_key, separator).items())
        else:
            items.append((new_key, item))
        i += 1
    return items


@property
def patch_data(self):
    if hasattr(self, '_patch_data'):
        return self._patch_data

    data = {}

    def is_optional(field):
        return Optional in [v.__class__ for v in field.validators]

    def is_required(field):
        return Required in [v.__class__ for v in field.validators]

    for name, f in self._fields.iteritems():
        if f.is_missing:
            if is_optional(f):
                continue
            elif not is_required(f) and f.default is None:
                continue

        if isinstance(f, FormField):
            data[name] = f.patch_data
        else:
            data[name] = f.data
    return data


def monkey_patch_process(func):
    """Monkey patches Form process method to better understand missing values.
    """
    def process(self, formdata, data=_unset_value):
        call_original_func = True
        if not isinstance(self, FormField):
            self.is_missing = True
            if formdata:
                if self.name in formdata:
                    if len(formdata.getlist(self.name)) == 1:
                        if formdata[self.name] is None:
                            call_original_func = False
                            self.data = None
                    self.is_missing = not bool(formdata.getlist(self.name))
                else:
                    self.is_missing = True
        if call_original_func:
            func(self, formdata, data=data)
        if (formdata and self.name in formdata and
                formdata[self.name] is None and
                isinstance(self, FormField)):
            self.form._is_missing = False
            self.form._patch_data = None
    return process


class MultiDict(dict):
    def getlist(self, key):
        return [self[key]]


@classmethod
def from_json(cls, formdata=None, obj=None, **kwargs):
    return cls(MultiDict(flatten_json(formdata)), obj, **kwargs)


@property
def is_missing(self):
    if hasattr(self, '_is_missing'):
        return self._is_missing

    for name, field in self._fields.items():
        if not field.is_missing:
            return False
    return True


def process_formdata(self, valuelist):
    """This function should overrides BooleanField process_formdata in order
    to adds support for JSON styled boolean False values."""
    if valuelist and valuelist[0] is False:
        self.data = False
    else:
        self.data = bool(valuelist)


def init():
    Form.is_missing = is_missing
    Form.patch_data = patch_data
    Form.from_json = from_json
    Field.process = monkey_patch_process(Field.process)
    FormField.process = monkey_patch_process(FormField.process)
    BooleanField.process_formdata = process_formdata
