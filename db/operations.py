def commit_sql(conn, sql, data):
    """
    Create a new register to database
    :param conn: connection database
    :param sql: sql string
    :param data: data to operation
    :return:
    """
    cur = conn.cursor()
    cur.execute(sql, data)
    conn.commit()
    
    return cur.lastrowid


def query_sql(conn, sql, params=None):
    """
    Query rows in table inside sql
    :param conn: Connection database
    : return rows:
    """
    cur = conn.cursor()
    if params:
        cur.execute(sql, params)
    else:
        cur.execute(sql)
        
    rows = cur.fetchall()
    
    return rows