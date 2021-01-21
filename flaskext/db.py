from mysql.connector import InternalError
from json import dumps

class SqlConnector():

    instance = None

    def exec_query(self, q, params=[]):
        db = self.instance.get_db()
        cursor = db.cursor()
        res = []
        try:
            cursor.execute(q, params)
            res = cursor.fetchall()
        except InternalError as error:
            code, message, other = error.args
            print(">>>>>>>>>>>>>", code, message, other)
        return res

    def exec_json_query(self, q, params=[]):
        db = self.instance.get_db()
        cursor = db.cursor(prepared=True)
        cursor.execute(q, params)
        row_headers = [x[0] for x in cursor.description]
        rv = cursor.fetchall()
        json_data = []
        for result in rv:
            json_data.append(dict(zip(row_headers, result)))
        return json_data

    def exec_command_with_keys(self, q, params=[]):
        db = self.instance.get_db()
        cursor = db.cursor(prepared=True)
        key = 0
        try:
            cursor.execute(q, params)
            db.commit()
            key = cursor.lastrowid
        except InternalError as error:
            code, message, other = error.args
            print(">>>>>>>>>>>>>", code, message, other)
            db.rollback()
        return key

    def exec_command(self, q, params=[]):
        db = self.instance.get_db()
        cursor = db.cursor(prepared=True)
        try:
            cursor.execute(q, params)
            db.commit()
        except InternalError as error:
            code, message, other = error.args
            print(">>>>>>>>>>>>>", code, message, other)
            db.rollback()

    def masive_insert(self, table_name, headers, items):
        params = []
        query = "INSERT INTO " + table_name + " ("
        for item in headers:
            query += item + ","
        query = query[:-1] + ") VALUES "
        for item in items:
            query += "("
            for header in headers:
                query += "?,"
                params.append(item[header])
            query = query[:-1] + "),"
        query = query[:-1] + ";"
        self.exec_command(query, params)

    def insert(self, table_name, params={}):
        items = []
        query = "INSERT INTO " + table_name + " ("
        for item in params:
            query += item + ","
            items.append(params[item])
        query = query[:-1] + ") VALUES("
        for i in range(0, len(params)):
            query += "?,"
        query = query[:-1] + ");"
        return self.exec_command_with_keys(query, items)

    def insert_model(self, table_name, key_name, params={}):
        items = []
        query = "INSERT INTO " + table_name + " ("
        for item in params:
            query += item + ","
            items.append(params[item])
        query = query[:-1] + ") VALUES("
        for i in range(0, len(params)):
            query += "?,"
        query = query[:-1] + ");"
        id = self.exec_command_with_keys(query, items)
        query = "select "+table_name[0:1] + \
            ".* from " + table_name + " " + table_name[0:1]
        return self.get(query, {key_name: id})

    def update_model(self, table_name, key_name, params, key_id):
        items = []
        query = "UPDATE " + table_name + " SET "
        for item in params:
            query += item + " = ?,"
            items.append(params[item])
        query = query[:-1]
        conditions = {key_name: key_id}
        if(len(conditions) > 0):
            query += " WHERE "
            for item in conditions:
                query += item + " = ? AND "
                items.append(conditions[item])
            query = query[:-4] + ""
        query += ";"
        self.exec_command(query, items)
        query = "select " + table_name[0:1] + \
            ".* from " + table_name + " " + table_name[0:1]
        return self.get(query, conditions)

    def update(self, table_name, params={}, conditions={}):
        items = []
        query = "UPDATE " + table_name + " SET "
        for item in params:
            query += item + " = ?,"
            items.append(params[item])
        query = query[:-1]
        if(len(conditions) > 0):
            query += " WHERE "
            for item in conditions:
                query += item + " = ? AND "
                items.append(conditions[item])
            query = query[:-4] + ""
        query += ";"
        return self.exec_command(query, items)

    def delete(self, table_name, params={}):
        items = []
        query = "DELETE FROM " + table_name
        if(len(params) > 0):
            query += " WHERE "
            for item in params:
                query += item + " = ? AND "
                items.append(params[item])
            query = query[:-4] + ")"
        query += ";"
        return self.exec_command(query, items)

    def get(self, query, conditions={}, likeable={}, order_by=[], ascendant=True, limit=0):
        l = self.get_list(query=query, conditions=conditions, likeable=likeable,
                          order_by=order_by, ascendant=ascendant, limit=limit)
        if(len(l) > 0):
            return l[0]
        return {}

    def get_list(self, query, conditions={}, likeable={}, order_by=[], ascendant=True, limit=0):
        items = []
        q = query + " "
        if(len(conditions) > 0 or len(likeable) > 0):
            q += " WHERE "
            if(len(likeable) > 0):
                q += "("
                for item in likeable:
                    q += item + " LIKE ? OR "
                    items.append(likeable[item])
                q = q[:-3] + ") AND  1=1 "
            if(len(conditions) > 0):
                for item in conditions:
                    if item.endswith('__lte'):
                        q += item.replace('__lte', '') + " <= ?  AND "
                    elif item.endswith('__mte'):
                        q += item.replace('__mte', '') + " >= ?  AND "
                    elif item.endswith('__mt'):
                        q += item.replace('__mt', '') + " > ?  AND "
                    elif item.endswith('__lt'):
                        q += item.replace('__lt', '') + " < ?  AND "
                    else: 
                        q += item + " = ? AND "
                    items.append(conditions[item])
                q = q[:-4]
        if(len(order_by) > 0):
            q += " ORDER BY "
            for item in order_by:
                q += item + ","
            q = q[:-1]
            if(ascendant):
                q += " ASC "
            else:
                q += " DESC "
        if(limit > 0):
            q += "LIMIT " + str(limit)
        return self.exec_json_query(q, items)
