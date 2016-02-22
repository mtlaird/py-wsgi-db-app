import sqlite3
import json


def _decode_list(data):
    rv = []
    for item in data:
        if isinstance(item, unicode):
            item = item.encode('utf-8')
        elif isinstance(item, list):
            item = _decode_list(item)
        elif isinstance(item, dict):
            item = _decode_dict(item)
        rv.append(item)
    return rv


def _decode_dict(data):
    rv = {}
    for key, value in data.iteritems():
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        elif isinstance(value, list):
            value = _decode_list(value)
        elif isinstance(value, dict):
            value = _decode_dict(value)
        rv[key] = value
    return rv


def _dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class DB:
    def __init__(self, config_file_name='example_db_config.json'):
        with open(config_file_name) as data_file:
            db_config = json.load(data_file, object_hook=_decode_dict)
            try:
                loaded_db_tables = db_config['db_tables']
            except KeyError:
                loaded_db_tables = False
            try:
                loaded_db_name = db_config['db_name']
            except KeyError:
                loaded_db_name = 'default.db'
        self.db_tables = loaded_db_tables
        self.db_name = loaded_db_name
        self.con = sqlite3.connect(self.db_name)
        self.con.text_factory = str
        self.con.row_factory = _dict_factory
        self.cur = self.con.cursor()

    def run_select_command(self, command, values=None):
        if not values:
            try:
                self.cur.execute(command)
            except sqlite3.Error as e:
                print e
                return False
        else:
            try:
                self.cur.execute(command, values)
            except sqlite3.Error as e:
                print e
                return False

        return self.cur.fetchall()

    def run_edit_command(self, command, values):
        try:
            self.cur.execute(command, values)
        except sqlite3.Error as e:
            print e
            return False

        self.con.commit()

        return True

    def get_schema(self):
        command = "SELECT sql FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence'"
        rows = self.run_select_command(command)
        if not rows:
            return False
        ret_list = []
        for r in rows:
            ret_list.append(r['sql'])

        return ret_list

    def create_schema(self, return_script=False):

        if not return_script:
            create_tables_script = ""
        else:
            create_tables_script = []

        for t in self.db_tables:
            create_tables_script_line = "CREATE TABLE %s(" % t
            first_column = True
            for c in self.db_tables[t]['columns']:
                if not first_column:
                    create_tables_script_line += ", "
                else:
                    first_column = False
                create_tables_script_line += "%s %s" % (c['name'], c['type'])
            create_tables_script_line += "); "
            if not return_script:
                create_tables_script += create_tables_script_line
            else:
                create_tables_script.append(create_tables_script_line[:-2])

        if not return_script:
            self.cur.executescript(create_tables_script)
            self.con.commit()

            return True
        else:
            return create_tables_script

    def check_schema(self):
        existing_schema = self.get_schema()
        correct_schema = self.create_schema(True)

        if len(existing_schema) == 0:
            print "No schema found. Creating DB schema."
            self.create_schema()
            return True

        if len(existing_schema) != len(correct_schema):
            print "Wrong number of tables in DB, exiting."
            return False

        for s in correct_schema:
            if s not in existing_schema:
                print "Table definition missing or incorrect in DB, exiting."
                return False

        return True

    def drop_db(self):
        drop_tables_script = ""
        for t in self.db_tables:
            drop_tables_script += "DROP TABLE IF EXISTS %s;" % t
        self.cur.executescript(drop_tables_script)
        self.con.commit()

        return True

    @staticmethod
    def make_list_string_from_dict(input_dict, name, skip_values=None):
        ret_string = ""
        first_item = True
        for d in input_dict:
            if d[name] not in skip_values:
                if first_item:
                    first_item = False
                else:
                    ret_string += ", "
                ret_string += d[name]
        return ret_string

    @staticmethod
    def make_list_string_from_char(input_char, length):
        ret_string = ""
        first_item = True
        for i in range(0, length):
            if first_item:
                first_item = False
            else:
                ret_string += ", "
            ret_string += input_char
        return ret_string

    def get_num_columns(self, table_name):
        num_columns = len(self.db_tables[table_name]['columns'])
        if self.db_tables[table_name]['index_column']:
            num_columns -= 1
        return num_columns

    def make_sorted_list_from_dict(self, data, table_name, prefix=''):
        ret_list = []
        for c in self.db_tables[table_name]['columns']:
            if c['name'] not in self.db_tables[table_name]['index_column']:
                col_label = prefix + c['name']
                if col_label in data:
                    if type(data[col_label]) is str:
                        ret_list.append(data[col_label])
                    elif type(data[col_label]) is list:
                        if type(data[col_label][0]) is str:
                            ret_list.append(data[col_label][0])
                        else:
                            return False
                    else:
                        return False
                else:
                    return False
        return ret_list

    def make_simple_select_command(self, table_name):
        select_command = "SELECT * FROM %s " % table_name
        if self.db_tables[table_name]['joined_tables']:
            for jt in self.db_tables[table_name]['joined_tables']:
                select_command += "INNER JOIN %s ON %s.%s = %s.%s " % (jt['table'], table_name, jt['column'],
                                                                       jt['table'], jt['column'])
        return select_command

    def make_complex_select_command(self, table_name, additional_joins):
        select_command = self.make_simple_select_command(table_name)
        for j in additional_joins:
            select_command += "INNER JOIN %s ON %s = %s " % (j['joined_table'], j['left_join'], j['right_join'])

        return select_command

    def make_insert_command(self, table_name):
        insert_command = "INSERT INTO %s (" % table_name
        insert_command += self.make_list_string_from_dict(self.db_tables[table_name]['columns'], 'name',
                                                          self.db_tables[table_name]["index_column"])
        insert_command += ") VALUES("
        num_columns = self.get_num_columns(table_name)
        insert_command += self.make_list_string_from_char('?', num_columns)
        insert_command += ")"
        return insert_command

    def make_update_command(self, table_name):
        update_command = "UPDATE %s SET " % table_name
        first_entry = True
        for c in self.db_tables[table_name]['columns']:
            if c['name'] not in self.db_tables[table_name]['index_column']:
                if not first_entry:
                    update_command += ", %s=?" % c['name']
                else:
                    update_command += "%s=?" % c['name']
                    first_entry = False
        update_command += " WHERE "
        first_entry = True
        for c in self.db_tables[table_name]['columns']:
            if c['name'] not in self.db_tables[table_name]['index_column']:
                if not first_entry:
                    update_command += "AND %s=? " % c['name']
                else:
                    update_command += "%s=? " % c['name']
                    first_entry = False

        return update_command

    def make_delete_command(self, table_name):
        delete_command = "DELETE FROM %s WHERE " % table_name
        first_entry = True
        for c in self.db_tables[table_name]['columns']:
            if c['name'] not in self.db_tables[table_name]['index_column']:
                if not first_entry:
                    delete_command += "AND %s=? " % c['name']
                else:
                    delete_command += "%s=? " % c['name']
                    first_entry = False

        return delete_command

    def get_subset_table_rows(self, table_name, conditions, additional_joins=None, order_and_limit=None):

        if not additional_joins:
            select_command = self.make_simple_select_command(table_name)
        else:
            select_command = self.make_complex_select_command(table_name, additional_joins)
        first_item = True
        for c in conditions:
            if first_item:
                first_item = False
                select_command += 'WHERE '
            else:
                select_command += 'AND '
            if type(c[c.keys()[0]]) is list:
                select_command += "%s = '%s' " % (c.keys()[0], c[c.keys()[0]][0])
            elif type(c[c.keys()[0]]) is str or type(c[c.keys()[0]]) is int:
                select_command += "%s = '%s' " % (c.keys()[0], c[c.keys()[0]])

        if order_and_limit:
            if 'order' in order_and_limit.keys():
                first_item = True
                for o in order_and_limit['order']:
                    if first_item:
                        first_item = False
                        select_command += 'ORDER BY '
                    else:
                        select_command += ', '
                    select_command += '%s ' % o
            if 'limit' in order_and_limit.keys():
                select_command += 'LIMIT %s ' % order_and_limit['limit']

        try:
            self.cur.execute(select_command)
        except sqlite3.Error as e:
            print e
            return False

        rows = self.cur.fetchall()

        return rows

    def get_all_table_rows(self, table_name):

        select_command = self.make_simple_select_command(table_name)
        try:
            self.cur.execute(select_command)
        except sqlite3.Error as e:
            print e
            return False

        rows = self.cur.fetchall()

        return rows

    def add_table_row(self, table_name, data):

        if len(data) < self.get_num_columns(table_name):
            print 'ERROR: number of columns and items in data do not match'
            return False

        if type(data) is dict:
            data = self.make_sorted_list_from_dict(data, table_name)
            if not data:
                print 'ERROR: could not make list from data dict'
                return False

        insert_command = self.make_insert_command(table_name)
        try:
            self.cur.execute(insert_command, data)
        except sqlite3.Error as e:
            print e
            return False

        self.con.commit()
        return True

    def delete_table_row(self, table_name, data):

        if len(data) < self.get_num_columns(table_name):
            print 'ERROR: number of columns and items in data do not match'
            return False

        if type(data) is dict:
            data = self.make_sorted_list_from_dict(data, table_name)
            if not data:
                print 'ERROR: could not make list from data dict'
                return False

        delete_command = self.make_delete_command(table_name)
        try:
            self.cur.execute(delete_command, data)
        except sqlite3.Error as e:
            print e
            return False

        self.con.commit()
        return True

    def update_table_row(self, table_name, data):

        if len(data) < self.get_num_columns(table_name):
            print 'ERROR: number of columns and items in data do not match'
            return False

        if type(data) is dict:
            new_data = self.make_sorted_list_from_dict(data, table_name)
            old_data = self.make_sorted_list_from_dict(data, table_name, '_old_')
            if not new_data or not old_data:
                print 'ERROR: could not make list from data dict'
                return False
            data = new_data+old_data

        update_command = self.make_update_command(table_name)

        try:
            self.cur.execute(update_command, data)
        except sqlite3.Error as e:
            print e
            return False

        self.con.commit()
        return True

    def get_joined_table_rows(self, table_name):

        ret_dict = {}

        for jt in self.db_tables[table_name]['joined_tables']:
            ret_dict[jt['table']] = self.get_all_table_rows(jt['table'])

        return ret_dict
