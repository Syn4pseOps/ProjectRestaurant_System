# ============================================================
#  db.py — ชั้นติดต่อฐานข้อมูล  ★★★ นิสิตเขียน SQL ในไฟล์นี้ ★★★
#  มองหาคำว่า  # TODO  ทุกฟังก์ชัน — ใช้ %s เป็น placeholder เสมอ (กัน SQL injection)
# ============================================================
import mysql.connector
import config


def get_connection():
    return mysql.connector.connect(
        host=config.DB_HOST, user=config.DB_USER, password=config.DB_PASSWORD,
        database=config.DB_NAME, port=config.DB_PORT)


def run_query(sql, params=None):
    """รัน SELECT คืนผลเป็น list ของ dict"""
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    cur.execute(sql, params or ()); rows = cur.fetchall()
    cur.close(); conn.close(); return rows


def run_command(sql, params=None):
    """รัน INSERT / UPDATE / DELETE แล้ว commit"""
    conn = get_connection(); cur = conn.cursor()
    cur.execute(sql, params or ()); conn.commit()
    out = {"new_id": cur.lastrowid, "affected": cur.rowcount}
    cur.close(); conn.close(); return out


def blank_to_none(value):
    """ช่องที่ไม่ได้กรอกในฟอร์มจะส่งมาเป็น "" — แปลงเป็น None (= NULL ใน SQL)
    ใช้กับคอลัมน์ที่ว่างได้ เช่น return_date, paid_date  เพราะ MySQL ไม่รับ '' เป็น DATE"""
    return None if value in ("", None) else value


def _todo(name):
    raise NotImplementedError(f"TODO: ยังไม่ได้เขียนฟังก์ชัน {name} ใน db.py")


# ---------- ลูกค้า (customer) ----------
def search_customers(filters):
    """ค้นหา ลูกค้า ตามเงื่อนไข (name, phone, member_tier)"""
    sql = "SELECT * FROM customer WHERE 1=1"
    params = []

    if filters.get("name"):
        sql += " AND name LIKE %s"
        params.append("%" + filters["name"] + "%")
    if filters.get("phone"):
        sql += " AND phone LIKE %s"
        params.append("%" + filters["phone"] + "%")
    if filters.get("member_tier"):
        sql += " AND member_tier = %s"
        params.append(filters["member_tier"])

    sql += " ORDER BY cust_id"
    return run_query(sql, params)

def get_customer(cust_id):
    """ดึง ลูกค้า 1 รายการตาม cust_id (ใช้ตอนเปิดฟอร์มแก้ไข)"""
    rows = run_query("SELECT * FROM customer WHERE cust_id = %s", (cust_id,))
    return rows[0] if rows else None

def create_customer(data):
    """เพิ่ม ลูกค้า ใหม่ — data มีคีย์: name, phone, member_tier"""
    sql = """INSERT INTO customer (name, phone, member_tier)
             VALUES (%s, %s, %s)"""
    return run_command(sql, (data["name"], data["phone"], data["member_tier"]))

def update_customer(cust_id, data):
    """แก้ไข ลูกค้า ตาม cust_id"""
    sql = """UPDATE customer
             SET name = %s, phone = %s, member_tier = %s
             WHERE cust_id = %s"""
    return run_command(sql, (data["name"], data["phone"], data["member_tier"], cust_id))

def delete_customer(cust_id):
    """ลบ ลูกค้า ตาม cust_id"""
    return run_command("DELETE FROM customer WHERE cust_id = %s", (cust_id,))

# ---------- เมนูอาหาร (menu_item) ----------
def search_items(filters):
    """ค้นหา เมนูอาหาร ตามเงื่อนไข (name, category)"""
    sql = "SELECT * FROM menu_item WHERE 1=1"
    params = []

    if filters.get("name"):
        sql += " AND name LIKE %s"
        params.append("%" + filters["name"] + "%")
    if filters.get("category"):
        sql += " AND category LIKE %s"
        params.append("%" + filters["category"] + "%")

    sql += " ORDER BY item_id"
    return run_query(sql, params)

def get_item(item_id):
    """ดึง เมนูอาหาร 1 รายการตาม item_id (ใช้ตอนเปิดฟอร์มแก้ไข)"""
    rows = run_query("SELECT * FROM menu_item WHERE item_id = %s", (item_id,))
    return rows[0] if rows else None

def create_item(data):
    """เพิ่ม เมนูอาหาร ใหม่ — data มีคีย์: name, category, price, is_available"""
    sql = """INSERT INTO menu_item (name, category, price, is_available)
             VALUES (%s, %s, %s, %s)"""
    return run_command(sql, (data["name"], data["category"], data["price"], data["is_available"]))

def update_item(item_id, data):
    """แก้ไข เมนูอาหาร ตาม item_id"""
    sql = """UPDATE menu_item
             SET name = %s, category = %s, price = %s, is_available = %s
             WHERE item_id = %s"""
    return run_command(sql, (data["name"], data["category"], data["price"], data["is_available"], item_id))

def delete_item(item_id):
    """ลบ เมนูอาหาร ตาม item_id"""
    return run_command("DELETE FROM menu_item WHERE item_id = %s", (item_id,))

# ---------- ออเดอร์ (food_order) ----------
def search_orders(filters):
    """ค้นหา ออเดอร์ ตามเงื่อนไข (cust_id, table_id, status)
    แสดง order_id, cust_id, ชื่อลูกค้า, table_id, order_time, status, total"""
    sql = """
        SELECT
            fo.order_id,
            fo.cust_id,
            c.name AS customer_name,
            fo.table_id,
            fo.order_time,
            fo.status,
            IFNULL(t.total, 0) AS total
        FROM food_order AS fo
        INNER JOIN customer AS c ON fo.cust_id = c.cust_id
        LEFT JOIN (
            SELECT oi.order_id, SUM(oi.qty * mi.price) AS total
            FROM order_item AS oi
            INNER JOIN menu_item AS mi ON oi.item_id = mi.item_id
            GROUP BY oi.order_id
        ) AS t ON fo.order_id = t.order_id
        WHERE 1=1
    """
    params = []

    if filters.get("cust_id"):
        sql += " AND fo.cust_id = %s"
        params.append(filters["cust_id"])
    if filters.get("table_id"):
        sql += " AND fo.table_id = %s"
        params.append(filters["table_id"])
    if filters.get("status"):
        sql += " AND fo.status = %s"
        params.append(filters["status"])

    sql += " ORDER BY fo.order_id"
    return run_query(sql, params)

def get_order(order_id):
    """ดึง ออเดอร์ 1 รายการตาม order_id (ใช้ตอนเปิดฟอร์มแก้ไข)"""
    rows = run_query("SELECT * FROM food_order WHERE order_id = %s", (order_id,))
    return rows[0] if rows else None

def check_table_free(table_id, order_id=None):
    """ตรวจว่าโต๊ะมีอยู่จริงและไม่มีออเดอร์ open อื่นอยู่"""
    table = run_query(
        "SELECT table_id FROM dining_table WHERE table_id = %s",
        (table_id,)
    )
    if not table:
        raise ValueError(f"ไม่พบโต๊ะ {table_id}")

    rows = run_query(
        """SELECT COUNT(*) AS n
           FROM food_order
           WHERE table_id = %s
             AND status = 'open'
             AND order_id <> %s""",
        (table_id, order_id or 0)
    )
    if rows[0]["n"] > 0:
        raise ValueError(f"โต๊ะ {table_id} ยังมีออเดอร์ที่ยังไม่ชำระเงิน")
    return True

def create_order(data):
    """เพิ่ม ออเดอร์ ใหม่ — ถ้า open ต้องตรวจโต๊ะก่อน"""
    if data["status"] == "open":
        check_table_free(data["table_id"])

    sql = """INSERT INTO food_order (cust_id, table_id, order_time, status)
             VALUES (%s, %s, %s, %s)"""
    return run_command(sql, (
        data["cust_id"], data["table_id"],
        blank_to_none(data["order_time"]), data["status"]
    ))

def update_order(order_id, data):
    """แก้ไข ออเดอร์ ตาม order_id"""
    if data["status"] == "open":
        check_table_free(data["table_id"], order_id)

    sql = """UPDATE food_order
             SET cust_id = %s, table_id = %s, order_time = %s, status = %s
             WHERE order_id = %s"""
    return run_command(sql, (
        data["cust_id"], data["table_id"],
        blank_to_none(data["order_time"]), data["status"], order_id
    ))

def delete_order(order_id):
    """ลบ ออเดอร์ ตาม order_id"""
    return run_command("DELETE FROM food_order WHERE order_id = %s", (order_id,))

# ============================================================
#  REPORT (รายงาน — ใช้ JOIN + GROUP BY + subquery)
#  ★ ชื่อคอลัมน์ใน SELECT จะกลายเป็นหัวตารางบนเว็บ — ใช้ AS 'ชื่อภาษาไทย' ได้
# ============================================================
def report_summary():
    """ตัวเลขสรุปบนการ์ด dashboard"""
    sql = """
        SELECT
            (SELECT COUNT(*) FROM customer) AS 'ลูกค้า',
            (SELECT COUNT(*) FROM menu_item) AS 'เมนู',
            (SELECT COUNT(*) FROM food_order) AS 'ออเดอร์',
            (SELECT IFNULL(SUM(oi.qty * mi.price), 0)
             FROM order_item AS oi
             INNER JOIN menu_item AS mi ON oi.item_id = mi.item_id) AS 'ยอดขายรวม',
            (SELECT COUNT(*) FROM food_order WHERE status = 'open') AS 'ออเดอร์ที่กำลังเปิด',
            (SELECT COUNT(*) FROM dining_table) AS 'จำนวนโต๊ะ'
    """
    return run_query(sql)[0]

def report_popular_items():
    """📈 เมนูขายดี (Best Sellers)"""
    sql = """
        SELECT
            mi.item_id AS 'รหัสเมนู',
            mi.name AS 'เมนู',
            SUM(oi.qty) AS 'จำนวนที่ขาย',
            SUM(oi.qty * mi.price) AS 'ยอดขาย'
        FROM order_item AS oi
        INNER JOIN menu_item AS mi ON oi.item_id = mi.item_id
        GROUP BY mi.item_id, mi.name
        ORDER BY SUM(oi.qty) DESC
        LIMIT 5
    """
    return run_query(sql)

def report_daily_sales():
    """💰 ยอดขายรวมต่อวัน (Daily Sales)"""
    sql = """
        SELECT
            DATE(fo.order_time) AS 'วันที่',
            SUM(oi.qty * mi.price) AS 'ยอดขายรวม'
        FROM food_order AS fo
        INNER JOIN order_item AS oi ON fo.order_id = oi.order_id
        INNER JOIN menu_item AS mi ON oi.item_id = mi.item_id
        GROUP BY DATE(fo.order_time)
        ORDER BY DATE(fo.order_time)
    """
    return run_query(sql)

def report_big_orders():
    """🧾 ออเดอร์ยอดเกิน 500 บาท (HAVING)"""
    sql = """
        SELECT
            fo.order_id AS 'รหัสออเดอร์',
            c.name AS 'ลูกค้า',
            fo.table_id AS 'โต๊ะ',
            fo.order_time AS 'เวลา',
            SUM(oi.qty * mi.price) AS 'ยอดรวม'
        FROM food_order AS fo
        INNER JOIN customer AS c ON fo.cust_id = c.cust_id
        INNER JOIN order_item AS oi ON fo.order_id = oi.order_id
        INNER JOIN menu_item AS mi ON oi.item_id = mi.item_id
        GROUP BY fo.order_id, c.name, fo.table_id, fo.order_time
        HAVING SUM(oi.qty * mi.price) > 500
        ORDER BY SUM(oi.qty * mi.price) DESC
    """
    return run_query(sql)

# ============================================================
#  รายการรายงานที่แสดงบนหน้า /report  (เรียงตามลำดับที่แสดง)
#  ★ วิธีเพิ่มรายงานใหม่ (ไม่ต้องแก้ไฟล์อื่น):
#    1) เขียนฟังก์ชัน report_xxx() ด้านบน ให้ return run_query(sql)
#    2) เพิ่ม 1 บรรทัดในรายการนี้:  ("ชื่อใน-url", "หัวข้อที่แสดง", ชื่อฟังก์ชัน)
#  ★ รายการนี้ต้องอยู่ท้ายไฟล์ (หลังฟังก์ชันทั้งหมด) ไม่งั้น Python หาชื่อฟังก์ชันไม่เจอ
#  ★ ห้ามตั้งชื่อ url ว่า "summary" (ใช้แล้วสำหรับการ์ดสรุป)
# ============================================================
REPORTS = [
    ("popular-items", "📈 เมนูขายดี (Best Sellers)",        report_popular_items),
    ("daily-sales",   "💰 ยอดขายรวมต่อวัน (Daily Sales)",   report_daily_sales),
    ("big-orders",    "🧾 ออเดอร์ยอดเกิน 500 บาท (HAVING)", report_big_orders),
    # ("my-report", "📋 รายงานของฉัน", report_my_report),   ← ตัวอย่างการเพิ่มรายงานที่ 4
]
