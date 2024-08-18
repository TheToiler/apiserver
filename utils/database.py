import os
import sqlite3
from uuid import uuid4

datadir = 'data/'
database_file = ''.join([datadir, 'database.sqlite3'])

# Create tables in the database
sql_create_customers_table = 'CREATE TABLE customers(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL)'
sql_create_user_table = 'CREATE TABLE users(id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT NOT NULL, password_hash TEXT NOT NULL, customer_id INTEGER NOT NULL, admin INTEGER, FOREIGN KEY (customer_id) REFERENCES customers(id))'
sql_create_servers_table = 'CREATE TABLE servers(api_key TEXT PRIMARY KEY, description TEXT NOT NULL, customer_id INTEGER NOT NULL, name TEXT, os_name TEXT, os_version TEXT, total_memory INTEGER, total_disk INTEGER, cpu_arch TEXT, warning BOOL, FOREIGN KEY (customer_id) REFERENCES customers(id))'
sql_create_checks_table = 'CREATE TABLE server_check(id INTEGER PRIMARY KEY AUTOINCREMENT, run_epoch INTEGER NOT NULL, api_key TEXT NOT NULL, cpu_use TEXT, memory_use INTEGER, online BOOL, pub_ipv4 TEXT, pub_ipv6 TEXT, uptime INTEGER, FOREIGN KEY (api_key) REFERENCES servers(api_key))'
sql_create_servers_logged_users_table = 'CREATE TABLE server_logged_users(api_key NOT NULL, username TEXT NOT NULL, terminal TEXT, ip_from TEXT, start_time INTEGER, stop_time INTEGER, total_time text, FOREIGN KEY (api_key) REFERENCES servers(api_key))'
sql_create_check_disks_table = 'CREATE TABLE server_check_disks(id NOT NULL, mountpoint TEXT NOT NULL, device TEXT, usage INTEGER, FOREIGN KEY(id) REFERENCES server_check(id))'
sql_create_check_current_users_table = 'CREATE TABLE server_check_current_users(id NOT NULL, username TEXT NOT NULL, ip_from TEXT, FOREIGN KEY(id) REFERENCES server_check(id))'

# Insert data in the database
sql_insert_customer = 'INSERT INTO customers(name) VALUES (?)'
sql_insert_user = 'INSERT INTO users (email, password_hash, customer_id, admin) VALUES (?, ?, ?, ?)'
sql_insert_server = 'INSERT INTO servers (api_key, description, customer_id) VALUES (?, ?, ?)'
sql_insert_server_logged_users = 'INSERT INTO server_logged_users(api_key, username, terminal, ip_from, start_time, stop_time, total_time) VALUES (?, ?, ?, ?, ?, ?, ?)'
sql_insert_check = 'INSERT INTO server_check(run_epoch, api_key, cpu_use, memory_use, online, pub_ipv4, pub_ipv6, uptime) VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
sql_insert_check_disks = 'INSERT INTO server_check_disks(id, mountpoint, device, usage) VALUES (?, ?, ?, ?)'
sql_insert_check_current_users = 'INSERT INTO server_check_current_users(id, username, ip_from) VALUES (?, ?, ?)'

# Select data from the database
sql_select_customers = 'SELECT * FROM customers'
sql_select_servers = 'SELECT * FROM servers'
sql_select_servers_customerid = 'SELECT * FROM servers WHERE customer_id=?'
sql_select_server_api = 'SELECT * FROM servers WHERE api_key=?'
sql_select_users = 'SELECT * FROM users'
sql_select_users_customerid = 'SELECT * FROM users WHERE customer_id=?'
sql_select_user_id = 'SELECT * FROM users WHERE id=?'
sql_select_user_email = 'SELECT id FROM users WHERE email=?'
sql_select_server_logged_users = 'SELECT * FROM server_check_logged_users WHERE api_key=?'
sql_select_server_check = 'SELECT * FROM server_check WHERE api_key=?'
sql_select_server_check_epoch = 'SELECT * FROM server_check WHERE api_key=? AND run_epoch BETWEEN ? AND ?'
sql_select_servers_check_disks = 'SELECT * FROM server_check_disks WHERE id=(?)'
sql_select_server_check_current_users = 'SELECT * FROM server_check_current_users WHERE id=(?)'

# Delete data from the database
sql_delete_user_id = 'DELETE FROM users WHERE id=?'
sql_delete_customer_id = 'DELETE FROM customers WHERE id=?'
sql_delete_server_apikey = 'DELETE FROM servers WHERE api_key=?'

# Insert test data
sql_insert_admin_customer = "INSERT INTO customers(id, name) VALUES ('0', 'Admin company')"
sql_insert_admin_user = 'INSERT INTO users (id, email, password_hash, customer_id, admin) VALUES ("0", "administrator", "scrypt:32768:8:1$10fbfZ1uf0ldOS6A$5e5c90625824d1896e89188a35f69f13f1abb67c0ad5c85a6f3fd9ca20ba0f929b8b6f025066f804c0bc37fcb9a6dfa590b158cd2e186ebfd525b1ca9685cdc4", 0, True)'
sql_insert_test_user = 'INSERT INTO users (email, password_hash, customer_id,  admin) VALUES ("arnold.gerrits@gmail.com", "scrypt:32768:8:1$10fbfZ1uf0ldOS6A$5e5c90625824d1896e89188a35f69f13f1abb67c0ad5c85a6f3fd9ca20ba0f929b8b6f025066f804c0bc37fcb9a6dfa590b158cd2e186ebfd525b1ca9685cdc4", 0, False)'
sql_insert_test_server = 'INSERT INTO servers (api_key, description, customer_id) VALUES ("0c0f7508-4729-400c-9af8-f7faf1b6a89d", "RaspberryPI Arnold", "0")'

#Update data in the database
sql_update_server = 'UPDATE servers SET name=?, os_name=?, os_version=?, total_memory=?, total_disk=?, cpu_arch=?, warning=? WHERE api_key=?'

def get_sqlite3_thread_safety():
    # Mape value from SQLite's THREADSAFE to Python's DBAPI 2.0
    # threadsafety attribute.
    sqlite_threadsafe2python_dbapi = {0: 0, 2: 1, 1: 3}
    conn = sqlite3.connect(":memory:")
    threadsafety = conn.execute(
        "select * from pragma_compile_options where compile_options like 'THREADSAFE=%'").fetchone()[0]
    conn.close()
    threadsafety_value = int(threadsafety.split("=")[1])
    return sqlite_threadsafe2python_dbapi[threadsafety_value]


if get_sqlite3_thread_safety() == 3:
    check_same_thread = False
else:
    check_same_thread = True

connection: sqlite3.Connection = None

def withcursor(func):
    def wrapper(*args, **kwargs):
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        result = func(cursor, *args, *kwargs)
        cursor.close()
        connection.commit()
        return result
    return wrapper

def create_database_file():
    if not os.path.isdir(datadir):
        os.makedirs(datadir)
        os.chmod(datadir, 0o700)
    if not os.path.isfile(database_file):
        sqlite3.connect(database_file)
        os.chmod(database_file, 0o600)

@withcursor
def create_tables(cursor: sqlite3.Cursor):
    cursor.execute(sql_create_customers_table)
    cursor.execute(sql_create_user_table)
    cursor.execute(sql_create_servers_table)
    cursor.execute(sql_create_servers_logged_users_table)
    cursor.execute(sql_create_checks_table)
    cursor.execute(sql_create_check_disks_table)
    cursor.execute(sql_create_check_current_users_table)

@withcursor
def insert_test_data(cursor: sqlite3.Cursor):
    cursor.execute(sql_insert_admin_customer)
    cursor.execute(sql_insert_admin_user)
    cursor.execute(sql_insert_test_user)
    cursor.execute(sql_insert_test_server)


@withcursor
def get_users(cursor: sqlite3.Cursor) -> None:
    cursor.execute(sql_select_users)
    lu = cursor.fetchall()
    if lu is None:
        return None
    else:
        row_list = []
        for row in lu:
            row_list.append(row)
        return row_list


@withcursor
def get_users_customerid(cursor: sqlite3.Cursor, customer_id: str) -> None:
    cursor.execute(sql_select_users_customerid, (customer_id,))
    lu = cursor.fetchall()
    if lu is None:
        return None
    else:
        row_list = []
        for row in lu:
            row_list.append(row)
        return row_list


@withcursor
def get_user_id(cursor: sqlite3.Cursor, user_id: str):
    cursor.execute(sql_select_user_id, (str(user_id),))
    lu = cursor.fetchone()
    if lu is None:
        return None
    else:
        return lu


@withcursor
def get_user_email(cursor: sqlite3.Cursor, user_email: str) -> str:
    cursor.execute(sql_select_user_email, (user_email,))
    lu = cursor.fetchone()
    if lu is None:
        return None
    else:
        return lu['id']


@withcursor
def get_servers(cursor: sqlite3.Cursor):
    cursor.execute(sql_select_servers)
    lu = cursor.fetchall()
    if lu is None:
        return None
    else:
        row_list = []
        for row in lu:
            row_list.append(row)
        return row_list


@withcursor
def get_servers_api(cursor: sqlite3.Cursor, api_key: str):
    cursor.execute(sql_select_server_api, (api_key,))
    lu = cursor.fetchone()
    if lu is None:
        return None
    else:
        return lu


@withcursor
def get_servers_customerid(cursor: sqlite3.Cursor, customer_id: str) -> None:
    cursor.execute(sql_select_servers_customerid, (customer_id,))
    lu = cursor.fetchall()
    if lu is None or lu == []:
        return None
    else:
        row_list = []
        for row in lu:
            row_list.append(row)
        return row_list


@withcursor
def get_customers(cursor: sqlite3.Cursor) -> None:
    cursor.execute(sql_select_customers)
    lu = cursor.fetchall()
    if lu is None:
        return None
    else:
        row_list = []
        for row in lu:
            row_list.append(row)
        return row_list


@withcursor
def insert_user(cursor: sqlite3.Cursor, email: str, password_hash: str, customer_id: str, admin: str) -> None:
    cursor.execute(sql_insert_user,
                   (email, password_hash, customer_id, admin,))


@withcursor
def insert_customer(cursor: sqlite3.Cursor, name: str) -> None:
    cursor.execute(sql_insert_customer, (name,))


@withcursor
def insert_server(cursor: sqlite3.Cursor, description: str, customer_id: str) -> str:
    api_key = str(uuid4())
    while not cursor.execute(sql_select_server_api, (api_key, )):
        api_key = str(uuid4())
    cursor.execute(sql_insert_server, (api_key, description, customer_id,))
    return api_key


@withcursor
def insert_check(cursor: sqlite3.Cursor, json_data: str) -> None:
    #TODO: Determine warning based on the warning threshold
    cursor.execute(sql_update_server, (json_data['name'], json_data['os_name'], json_data['os_version'], json_data['total_memory'],
                                       json_data['total_disk'], json_data['cpu_arch'], False, json_data['api_key'],))
    for logged_user in json_data['logged_users']:
        cursor.execute(sql_insert_server_logged_users, (json_data['api_key'], logged_user['name'], logged_user['terminal'],
                                                        logged_user['ip_from'], logged_user['start_time'], logged_user['stop_time'],
                                                        logged_user['total_time'], ))
    cursor.execute(sql_insert_check, (json_data['run_epoch'], json_data['api_key'], json_data['cpu_use'], json_data['memory_use'],
                                      json_data['online'], json_data['pub_ipv4'], json_data['pub_ipv6'], json_data['uptime'], ))
    id = cursor.lastrowid
    for disk in json_data['disks']:
        cursor.execute(sql_insert_check_disks, (id, disk['mountpoint'], disk['device'], disk['usage'], ))
    for current_user in json_data['current_users']:
        cursor.execute(sql_insert_check_current_users, (id, current_user['name'], current_user['ip_from'], ))

@withcursor
def get_checks(cursor: sqlite3.Cursor, api_key: str):
    cursor.execute(sql_select_server_check, (api_key,))
    lu = cursor.fetchall()
    if lu == None:
        return None
    else:
        row_list = []
        for row in lu:
            row_list.append(row)
        return row_list

@withcursor
def get_last_check(cursor: sqlite3.Cursor, api_key: str):
    cursor.execute(sql_select_server_check, (api_key,))
    lu = cursor.fetchall()
    if lu == []:
        return None
    else:
        return lu[len(lu)-1]

@withcursor
def get_checks_epoch(cursor: sqlite3.Cursor, api_key: str, start_epoch, end_epoch):
    cursor.execute(sql_select_server_check_epoch,
                   (api_key, start_epoch, end_epoch,))
    lu = cursor.fetchall()
    if not lu:
        return None
    else:
        row_list = []
        for row in lu:
            row_list.append(row)
        return row_list

@withcursor
def get_checks_disks(cursor: sqlite3.Cursor, id: str):
    cursor.execute(sql_select_servers_check_disks, (id, ))
    lu = cursor.fetchall()
    if not lu:
        return None
    else:
        row_list = []
        for row in lu:
            row_list.append(row)
        return row_list

@withcursor
def delete_user_id(cursor: sqlite3.Cursor, id: str) -> None:
    cursor.execute(sql_delete_user_id, (id,))


@withcursor
def delete_customer_id(cursor: sqlite3.Cursor, id: str) -> None:
    cursor.execute(sql_delete_customer_id, (id,))


@withcursor
def delete_server_apikey(cursor: sqlite3.Cursor, apikey: str) -> None:
    cursor.execute(sql_delete_server_apikey, (apikey,))


def generate_check_testdata(amount_records):
    import random
    import os
    from datetime import datetime
    api_key = insert_server('test-server', '0')
    for i in range(amount_records):
        check_json = {}
        check_json['api_key'] = api_key
        random_epoch = datetime(2024, random.randint(1, 12), random.randint(
            1, 29), random.randint(0, 23), random.randint(0, 59), random.randint(0, 59)).timestamp()
        check_json['run_epoch'] = random_epoch
        check_json['cpu'] = str(os.getloadavg()[2])
        check_json['disks'] = {}
        check_json['memory'] = random.randint(0, 100)
        check_json['logged_users'] = []
        check_json['logged_users']['name'] = 'arnold'
        check_json['logged_users']['run_epoch'] = str(random_epoch)
        insert_check(check_json)


if __name__ == '__main__':
   print('DEBUG: Module is run directly. Deleting database and filling with testdata!')
   user_input = input('Are you sure you want this? (y/N)')
   if user_input.capitalize() != 'Y':
      print('DEBUG: You have not confirmed. Exiting debug.')
      quit(0)
   if os.path.isfile(database_file):
      os.remove(database_file)
   if os.path.isdir(datadir):
      os.rmdir(datadir)
   if not os.path.isdir(datadir):
      os.makedirs(datadir)
      os.chmod(datadir, 0o700)
   create_database_file()
   connection = sqlite3.connect(database_file, check_same_thread=check_same_thread)
   connection.execute("PRAGMA foreign_keys = 1")
   create_tables()
   insert_test_data()
   # Enable the following line to create test data
   # generate_check_testdata(10000)
   connection.close()
    
    
connection = sqlite3.connect(database_file, check_same_thread=check_same_thread)
connection.execute("PRAGMA foreign_keys = 1")
