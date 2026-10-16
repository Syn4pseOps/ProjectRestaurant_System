-- ============================================================
--  schema.sql — ระบบร้านอาหาร (นิสิตออกแบบและเขียนเอง)
--  กติกา: 1 ออเดอร์มีหลายเมนู (M:N: order × menu_item ผ่าน order_item),
--         เมนูชุด combo = M:N (menu_item × menu_item)
--  ต้องมี: PK ทุกตาราง, FK ครบ, ชื่อตรงกับ db.py, sample data
-- ============================================================
CREATE TABLE customer (
    cust_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    phone VARCHAR(10),
    member_tier VARCHAR(20)
    -- TODO: name, phone, member_tier
);
CREATE TABLE menu_item (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    category VARCHAR(100),
    price DECIMAL(5,2),
    is_available BOOLEAN
    -- TODO: name, category, price, is_available
);
CREATE TABLE dining_table (
    table_id INT AUTO_INCREMENT PRIMARY KEY,
    seats INT,
    zone VARCHAR(30)
    -- TODO: seats, zone
);
CREATE TABLE food_order (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    cust_id INT,
    table_id INT,
    order_time DATETIME,
    status ENUM('open','paid'),
    FOREIGN KEY (cust_id) REFERENCES customer(cust_id),
    FOREIGN KEY (table_id) REFERENCES dining_table(table_id)

    -- TODO: cust_id (FK), table_id (FK), order_time (DATETIME), status ENUM('open','paid')
    -- ★ ไม่ต้องมีคอลัมน์ยอดรวม — คำนวณจาก order_item × menu_item (ดู search_orders ใน db.py)
);
CREATE TABLE order_item (         -- M:N: food_order × menu_item
    -- TODO: order_id (FK), item_id (FK), qty, note ; PRIMARY KEY (order_id, item_id)
    order_id INT,
    item_id INT,
    qty INT,
    note VARCHAR(100),
    PRIMARY KEY (order_id, item_id),
    FOREIGN KEY (order_id) REFERENCES food_order(order_id),
    FOREIGN KEY (item_id) REFERENCES menu_item(item_id)
);
CREATE TABLE combo (              -- M:N: menu_item × menu_item
    combo_id INT AUTO_INCREMENT PRIMARY KEY,
    item_id INT,
    sub_item_id INT,
    amount INT,
    FOREIGN KEY (item_id) REFERENCES menu_item(item_id),
    FOREIGN KEY (sub_item_id) REFERENCES menu_item(item_id)
    -- TODO: item_id (FK -> menu_item), sub_item_id (FK -> menu_item), amount
);
-- TODO: INSERT ข้อมูลตัวอย่างทุกตาราง
--   ★ ควรมีออเดอร์ status 'open' อย่างน้อย 1 โต๊ะ ไว้ทดสอบ "เปิดออเดอร์ซ้ำโต๊ะเดิมไม่ได้"
-- ============================================================
-- SAMPLE DATA
-- ============================================================

INSERT INTO customer (name, phone, member_tier)
VALUES
('Armmy', '0941019022', 'Daimond'),
('Beammy', '0941019122', 'Platinum'),
('XiaoMing', '0844445556', 'Elite'),
('Moomy', '0941113344', 'Member'),
('XiaoLong', '0941018521', 'Sliver'),
('LongTu', '0811019122', 'Gold'),
('XiaoFeng', '0844445555', 'Elite'),
('WangLing', '0941111044', 'Daimond'),
('ArWang', '0998881122', 'Elite'),
('WangP', '0615347891', 'Member');

INSERT INTO menu_item (name, category, price, is_available)
VALUES
('ต้มยำกุ้งแม่น้ำ', 'Thai', 450.00, TRUE),
('แกงมัสมั่นเนื้อ', 'Thai', 520.00, TRUE),
('ผัดไทยกุ้งแม่น้ำ', 'Thai', 380.00, TRUE),
('พะแนงเป็ด', 'Thai', 420.00, TRUE),
('ปลากะพงทอดน้ำปลา', 'Thai', 550.00, TRUE),
('Grilled Australian Beef Tenderloin', 'International', 890.00, TRUE),
('Pan-Seared Salmon', 'International', 650.00, TRUE),
('Truffle Mushroom Risotto', 'International', 480.00, TRUE),
('Classic Beef Burger', 'International', 420.00, TRUE),
('Spaghetti Carbonara', 'International', 390.00, TRUE),
('เป็ดปักกิ่ง', 'Chinese', 980.00, TRUE),
('เสี่ยวหลงเปา', 'Chinese', 320.00, TRUE),
('กุ้งผัดซอสเสฉวน', 'Chinese', 520.00, TRUE),
('หมูกรอบฮ่องกง', 'Chinese', 450.00, TRUE),
('ปลานึ่งซีอิ๊ว', 'Chinese', 680.00, TRUE);

INSERT INTO dining_table (seats, zone)
VALUES
(2, 'Indoor'),
(2, 'Indoor'),
(4, 'Indoor'),
(4, 'Indoor'),
(6, 'Indoor'),
(2, 'Outdoor'),
(4, 'Outdoor'),
(4, 'Outdoor'),
(6, 'Outdoor'),
(8, 'Outdoor'),
(2, 'Garden'),
(2, 'Garden'),
(4, 'Garden'),
(6, 'Garden'),
(8, 'Garden');

INSERT INTO food_order (cust_id, table_id, order_time, status)
VALUES
(1, 3, '2026-09-29 11:30:00', 'paid'),
(2, 7, '2026-09-29 12:15:00', 'open'),
(3, 11, '2026-09-29 12:30:00', 'paid'),
(4, 5, '2026-09-29 13:00:00', 'open'),
(5, 9, '2026-09-29 13:20:00', 'paid'),
(6, 13, '2026-09-29 18:00:00', 'open'),
(7, 2, '2026-09-29 18:30:00', 'paid'),
(8, 6, '2026-09-29 19:00:00', 'open'),
(9, 14, '2026-09-29 19:15:00', 'open'),
(10, 4, '2026-09-29 20:00:00', 'paid');

INSERT INTO order_item (order_id, item_id, qty, note)
VALUES
(1, 1, 2, 'ไม่เผ็ด'),
(1, 3, 1, 'ไม่ใส่ถั่ว'),
(1, 8, 1, NULL),
(2, 6, 2, 'Medium'),
(2, 10, 1, NULL),
(3, 11, 1, NULL),
(3, 12, 2, 'เสิร์ฟร้อน'),
(4, 2, 1, 'ไม่ใส่ถั่ว'),
(4, 5, 1, NULL),
(5, 4, 2, 'ไม่เผ็ด'),
(5, 9, 1, NULL),
(5, 13, 1, 'เผ็ดน้อย'),
(6, 7, 2, NULL),
(6, 15, 1, 'ไม่ใส่ขิง'),
(7, 1, 1, 'เผ็ดน้อย'),
(7, 14, 2, NULL),
(8, 3, 2, 'ไม่ใส่กุ้ง'),
(8, 8, 1, NULL),
(9, 11, 1, NULL),
(9, 13, 2, 'เผ็ดปานกลาง'),
(9, 15, 1, NULL),
(10, 5, 1, NULL),
(10, 6, 1, 'Medium'),
(10, 10, 2, 'ไม่ใส่ชีส');

INSERT INTO combo (item_id, sub_item_id, amount)
VALUES
(1, 3, 1),
(1, 5, 1),
(2, 4, 1),
(2, 14, 1),
(6, 8, 1),
(6, 10, 1),
(7, 8, 1),
(7, 15, 1),
(11, 12, 2),
(11, 14, 1),
(13, 12, 1),
(13, 15, 1),
(15, 12, 2);
