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


with open('example_db_tables.json') as data_file:
    db_data = json.load(data_file, object_hook=_decode_dict)
    loaded_db_tables = db_data['db_tables']

db_tables = loaded_db_tables


def _dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

con = sqlite3.connect('example.db')
con.text_factory = str
con.row_factory = _dict_factory
cur = con.cursor()


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


def get_num_columns(table_name):
    num_columns = len(db_tables[table_name]['columns'])
    if db_tables[table_name]['index_column']:
        num_columns -= 1
    return num_columns


def make_sorted_list_from_dict(data, table_name, prefix=''):
    ret_list = []
    for c in db_tables[table_name]['columns']:
        if c['name'] not in db_tables[table_name]['index_column']:
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


def make_insert_command(table_name):
    insert_command = "INSERT INTO %s (" % table_name
    insert_command += make_list_string_from_dict(db_tables[table_name]['columns'], 'name',
                                                 db_tables[table_name]["index_column"])
    insert_command += ") VALUES("
    num_columns = get_num_columns(table_name)
    insert_command += make_list_string_from_char('?', num_columns)
    insert_command += ")"
    return insert_command


def make_select_command(table_name):
    select_command = "SELECT * FROM %s " % table_name
    if db_tables[table_name]['joined_tables']:
        for jt in db_tables[table_name]['joined_tables']:
            select_command += "INNER JOIN %s ON %s.%s = %s.%s " % (jt['table'], table_name, jt['column'], jt['table'],
                                                                   jt['column'])
    return select_command


def make_complex_select_command(table_name, additional_joins):
    select_command = make_select_command(table_name)
    for j in additional_joins:
        select_command += "INNER JOIN %s ON %s = %s " % (j['joined_table'], j['left_join'], j['right_join'])

    return select_command


def make_update_command(table_name):
    update_command = "UPDATE %s SET " % table_name
    first_entry = True
    for c in db_tables[table_name]['columns']:
        if c['name'] not in db_tables[table_name]['index_column']:
            if not first_entry:
                update_command += ", %s=?" % c['name']
            else:
                update_command += "%s=?" % c['name']
                first_entry = False
    update_command += " WHERE "
    first_entry = True
    for c in db_tables[table_name]['columns']:
        if c['name'] not in db_tables[table_name]['index_column']:
            if not first_entry:
                update_command += "AND %s=? " % c['name']
            else:
                update_command += "%s=? " % c['name']
                first_entry = False

    return update_command


def make_delete_command(table_name):
    delete_command = "DELETE FROM %s WHERE " % table_name
    first_entry = True
    for c in db_tables[table_name]['columns']:
        if c['name'] not in db_tables[table_name]['index_column']:
            if not first_entry:
                delete_command += "AND %s=? " % c['name']
            else:
                delete_command += "%s=? " % c['name']
                first_entry = False

    return delete_command


def get_subset_table_rows(table_name, conditions, additional_joins=None, order_and_limit=None):
    global cur
    if not cur:
        return False

    if not additional_joins:
        select_command = make_select_command(table_name)
    else:
        select_command = make_complex_select_command(table_name, additional_joins)
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
        cur.execute(select_command)
    except sqlite3.Error as e:
        print e
        return False

    rows = cur.fetchall()

    return rows


def get_all_table_rows(table_name):
    global cur
    if not cur:
        return False

    select_command = make_select_command(table_name)
    try:
        cur.execute(select_command)
    except sqlite3.Error as e:
        print e
        return False

    rows = cur.fetchall()

    return rows


def add_table_row(table_name, data):
    global cur
    if not cur:
        return False
    global con

    if len(data) < get_num_columns(table_name):
        print 'ERROR: number of columns and items in data do not match'
        return False

    if type(data) is dict:
        data = make_sorted_list_from_dict(data, table_name)
        if not data:
            print 'ERROR: could not make list from data dict'
            return False

    insert_command = make_insert_command(table_name)
    try:
        cur.execute(insert_command, data)
    except sqlite3.Error as e:
        print e
        return False

    con.commit()
    return True


def delete_table_row(table_name, data):
    global cur
    if not cur:
        return False
    global con

    if len(data) < get_num_columns(table_name):
        print 'ERROR: number of columns and items in data do not match'
        return False

    if type(data) is dict:
        data = make_sorted_list_from_dict(data, table_name)
        if not data:
            print 'ERROR: could not make list from data dict'
            return False

    delete_command = make_delete_command(table_name)
    try:
        cur.execute(delete_command, data)
    except sqlite3.Error as e:
        print e
        return False

    con.commit()
    return True


def update_table_row(table_name, data):
    global cur
    if not cur:
        return False
    global con

    if len(data) < get_num_columns(table_name):
        print 'ERROR: number of columns and items in data do not match'
        return False

    if type(data) is dict:
        new_data = make_sorted_list_from_dict(data, table_name)
        old_data = make_sorted_list_from_dict(data, table_name, '_old_')
        if not new_data or not old_data:
            print 'ERROR: could not make list from data dict'
            return False
        data = new_data+old_data

    update_command = make_update_command(table_name)

    try:
        cur.execute(update_command, data)
    except sqlite3.Error as e:
        print e
        return False

    con.commit()
    return True


def get_joined_table_rows(table_name):

    ret_dict = {}

    for jt in db_tables[table_name]['joined_tables']:
        ret_dict[jt['table']] = get_all_table_rows(jt['table'])

    return ret_dict


def drop_db():
    global cur
    if not cur:
        return False
    global con
    drop_tables_script = ""
    for t in db_tables:
        drop_tables_script += "DROP TABLE IF EXISTS %s;" % t
    cur.executescript(drop_tables_script)
    con.commit()

    return True


def get_schema():
    global cur
    if not cur:
        return False
    global con

    try:
        cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence'")
    except sqlite3.Error as e:
        print e
        return False

    rows = cur.fetchall()
    ret_list = []
    for r in rows:
        ret_list.append(r['sql'])

    return ret_list


def create_schema(return_script=False):
    global cur
    if not cur:
        return False
    global con

    if not return_script:
        create_tables_script = ""
    else:
        create_tables_script = []

    for t in db_tables:
        create_tables_script_line = "CREATE TABLE %s(" % t
        first_column = True
        for c in db_tables[t]['columns']:
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
        cur.executescript(create_tables_script)
        con.commit()

        return True
    else:
        return create_tables_script


def check_schema():
    existing_schema = get_schema()
    correct_schema = create_schema(True)

    if len(existing_schema) == 0:
        print "No schema found. Creating DB schema."
        create_schema()
        return True

    if len(existing_schema) != len(correct_schema):
        print "Wrong number of tables in DB, exiting."
        return False

    for s in correct_schema:
        if s not in existing_schema:
            print "Table definition missing or incorrect in DB, exiting."
            return False

    return True
