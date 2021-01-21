from .SqlConnector import sql

class ModelList(list):

    def to_json(self):
        res = []
        for item in self:
            res.append(item.to_json())
        return res

    def massive_insert(self, cls, keys):
        cls.prepare_class()
        items = []
        for item in self:
            helper = {}
            obj = item.__dict__
            for key in keys:
                helper[key] = obj[key]
            items.append(helper)
        sql.masive_insert(
            cls.table_name,
            keys,
            items
        )
        return self
