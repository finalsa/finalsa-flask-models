from json import JSONEncoder
from datetime import datetime
from decimal import Decimal
from .ModelList import ModelList
from .SqlConnector import sql
import re

class Model():

    id = 0
    table_name = ''
    key_name = ''
    not_visible = []

    @classmethod
    def prepare_class(cls, ):
        name = get_name(cls.__name__)
        cls.table_name = name + 's'
        cls.key_name = name + '_id'
        return cls

    def __init__(self, **args):
        super().__init__()
        self.prepare_class()
        self.set_attributes(args)

    def to_json(self, visible=[]):
        self_dict = self.__dict__.copy()
        for item in self.not_visible:
            self_dict.pop(item)
        result = {}
        if(len(visible) > 0):
            for key in visible:
                if isinstance(self_dict[key], Model):
                    result[key] = self_dict[key].to_json()
                elif isinstance(self_dict[key], list):
                    helper = []
                    for item in self_dict[key]:
                        if isinstance(item, Model):
                            helper.append(item.to_json())
                        else:
                            helper.append(item)
                    result[key] = helper
                else:
                    result[key] = self_dict[key]
            return result
        if('not_visible' in self_dict):
            self_dict.pop('not_visible')
        if(self.key_name in self_dict):
            self_dict.pop(self.key_name)
        res = {}
        for item in self_dict:
            if isinstance(self_dict[item], Model):
                res[item] = self_dict[item].to_json()
            elif isinstance(self_dict[item], list):
                helper = []
                for key in self_dict[item]:
                    if isinstance(key, Model):
                        helper.append(key.to_json())
                    else:
                        helper.append(key)
                res[item] = helper
            elif isinstance(self_dict[item], datetime):
                res[item] = str(self_dict[item])
            elif isinstance(self_dict[item], Decimal):
                res[item] = float(self_dict[item])
            else:
                res[item] = self_dict[item]
        return res

    def save(self):
        self_dict = self.__dict__.copy()
        if('not_visible' in self_dict):
            self_dict.pop('not_visible')
        if('id' in self_dict):
            self_dict[self.key_name] = self_dict['id']
            self_dict.pop('id')
        params = dict()
        for item in self_dict:
            if isinstance(self_dict[item], Model):
                params[self_dict[item].key_name] = self_dict[item].id
            else:
                params[item] = self_dict[item]
        result = sql.insert_model(
            self.table_name, self.key_name, params=params)
        if(self.key_name in result):
            result['id'] = result[self.key_name]
            result.pop(self.key_name)
        self.set_attributes(result)
        return self

    def update(self):
        self_dict = self.__dict__.copy()
        if('not_visible' in self_dict):
            self_dict.pop('not_visible')
        if('id' in self_dict):
            self_dict.pop('id')
        params = dict()
        for item in self_dict:
            if isinstance(self_dict[item], Model):
                params[self_dict[item].key_name] = self_dict[item].id
            else:
                params[item] = self_dict[item]
        result = sql.update_model(
            self.table_name, self.key_name, params, self.id)
        if(self.key_name in result):
            result['id'] = result[self.key_name]
            result.pop(self.key_name)
        self.set_attributes(result)
        return self

    def set_attributes(self, attrs):
        self.__dict__.update(attrs)

    @classmethod
    def get_list(cls, **args):
        cls.prepare_class()
        params = dict(args)
        if('id' in params):
            params[cls.key_name] = params['id']
            params.pop('id')
        query = 'select ' + \
                cls.table_name[0:1] + '.* from ' + \
            cls.table_name + ' ' + cls.table_name[0:1]
        result = sql.get_list(query, params)
        res = ModelList()
        for item in result:
            item['id'] = item[cls.key_name]
            res.append(cls(**item))
        return res

    @classmethod
    def get(cls, **args):
        cls.prepare_class()
        params = dict(args)
        if('id' in params):
            params[cls.key_name] = params['id']
            params.pop('id')
        query = 'select ' + cls.table_name[0:1] + '.* from ' + \
                cls.table_name + ' ' + cls.table_name[0:1]
        result = sql.get(query, params)
        if(len(result) > 0):
            if(cls.key_name in result):
                result['id'] = result[cls.key_name]
                result.pop(cls.key_name)
        return cls(**result)

    @classmethod
    def get_last_inserted(cls):
        cls.prepare_class()
        query = 'select ' + cls.table_name[0:1] + '.* from ' + \
            cls.table_name + ' as ' + cls.table_name[0:1]
        result = sql.get(
            query, limit=1, order_by=[cls.key_name], ascendant=False)
        return cls(**result)


def get_name(name):
    res = ''
    items = re.findall('[A-Z][^A-Z]*', name)
    for item in items:
        res += item + '_'
    res = res[:-1].lower()
    return res


class ModelEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.__str__()
        obj_dict = o.__dict__.copy()
        for item in obj_dict:
            if isinstance(obj_dict[item], Model.__class__):
                obj_dict[item] = item.to_json()
        return obj_dict
