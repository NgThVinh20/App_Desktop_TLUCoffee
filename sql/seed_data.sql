USE cafe_tlu;

-- ============================================================
-- 1. TÀI KHOẢN NHÂN VIÊN
-- Password mặc định: Admin@123 (đã hash bcrypt)
-- ============================================================
INSERT INTO users (full_name, email, password_hash, role, phone) VALUES
('Admin TLU',       'admin@tlucoffee.vn',   '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMeSSdFp0sCz.Nqu82GNLJVo.2', 'admin',    '024 3852 1447'),
('Nguyễn Văn An',  'an.nv@tlucoffee.vn',   '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMeSSdFp0sCz.Nqu82GNLJVo.2', 'barista',  '090 123 4567'),
('Trần Thu Hà',    'ha.tt@tlucoffee.vn',   '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMeSSdFp0sCz.Nqu82GNLJVo.2', 'manager',  '090 234 5678'),
('Lê Minh Khoa',   'khoa.lm@tlucoffee.vn', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMeSSdFp0sCz.Nqu82GNLJVo.2', 'cashier',  '090 345 6789'),
('Phạm Thị Lan',   'lan.pt@tlucoffee.vn',  '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMeSSdFp0sCz.Nqu82GNLJVo.2', 'server',   '090 456 7890'),
('Đỗ Quang Huy',   'huy.dq@tlucoffee.vn',  '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMeSSdFp0sCz.Nqu82GNLJVo.2', 'kitchen',  '090 567 8901');

-- ============================================================
-- 2. DANH MỤC MÓN
-- ============================================================
INSERT INTO categories (name, description, sort_order) VALUES
('Cà phê',          'Các loại cà phê truyền thống và hiện đại', 1),
('Trà & Macchiato', 'Trà trái cây, trà sữa, macchiato',         2),
('Bánh ngọt',       'Bánh mì, croissant, bánh kem',             3),
('Khác',            'Nước ép, sinh tố, đồ uống đặc biệt',       4);

-- ============================================================
-- 3. THỰC ĐƠN
-- ============================================================
INSERT INTO menu_items (category_id, name, description, base_price, is_available, is_featured) VALUES
-- Cà phê (category_id = 1)
(1, 'Bạc Xỉu Cốt Dừa',   'Cà phê robusta kết hợp kem cốt dừa béo ngậy, đặc trưng TLU',  45000, 1, 1),
(1, 'Cà Phê Sữa Đá',      'Cà phê phin truyền thống với sữa đặc Ông Thọ',                 29000, 1, 0),
(1, 'Bạc Xỉu',            'Nhiều sữa ít cà phê, vị ngọt nhẹ',                             32000, 1, 0),
(1, 'Phin Sữa Đá',        'Cà phê phin pha sữa tươi, đậm đà',                             35000, 1, 0),
(1, 'Latte Art',           'Espresso thượng hạng với lớp bọt sữa tạo hình nghệ thuật',     55000, 1, 1),
(1, 'Cold Brew',           'Cà phê ủ lạnh 12 giờ, vị mượt mà',                            55000, 1, 0),
(1, 'Espresso',            'Espresso nguyên chất double shot',                              35000, 1, 0),
-- Trà & Macchiato (category_id = 2)
(2, 'Trà Đào Cam Sả',     'Thanh mát, giải nhiệt với trà đào và cam tươi',                45000, 1, 1),
(2, 'Trà Sen Vàng',        'Sen tươi, kem béo, trà oolong thượng hạng',                    49000, 1, 0),
(2, 'Trà Sữa Trân Châu',  'Trà sữa đài loan với trân châu đen dẻo',                       39000, 1, 0),
(2, 'Macchiato Caramel',  'Espresso với caramel và bọt sữa',                               49000, 1, 0),
-- Bánh ngọt (category_id = 3)
(3, 'Croissant Phô Mai',  'Bơ thơm, giòn rụm, nhân phô mai béo',                          35000, 1, 0),
(3, 'Bánh Mì Thịt TLU',  'Bánh mì đặc sản quán với nhân thịt nguội đặc biệt',            42000, 1, 1),
(3, 'Bánh Tiramisu',      'Bánh kem cà phê kiểu Ý, thơm ngon',                            45000, 0, 0),
-- Khác (category_id = 4)
(4, 'Nước Ép Cam',        'Cam tươi ép nguyên chất',                                       35000, 1, 0),
(4, 'Sinh Tố Bơ',         'Bơ chín kem mịn, bổ dưỡng',                                    45000, 1, 0);

-- ============================================================
-- 4. BIẾN THỂ SIZE
-- ============================================================
INSERT INTO item_variants (item_id, size_name, extra_price) VALUES
-- Bạc Xỉu Cốt Dừa (item_id=1)
(1, 'M', 0), (1, 'L', 10000),
-- Cà Phê Sữa Đá (item_id=2)
(2, 'M', 0), (2, 'L', 8000),
-- Latte Art (item_id=5)
(5, 'M', 0), (5, 'L', 12000),
-- Trà Đào Cam Sả (item_id=8)
(8, 'M', 0), (8, 'L', 10000),
-- Trà Sữa Trân Châu (item_id=10)
(10, 'S', -5000), (10, 'M', 0), (10, 'L', 10000);

-- ============================================================
-- 5. ĐƠN HÀNG MẪU
-- ============================================================
INSERT INTO orders (order_code, user_id, table_number, subtotal, discount, tax, total_amount, payment_method, status) VALUES
('TLU-2024-0001', 4, 1,  180000, 18000, 0, 162000, 'transfer', 'completed'),
('TLU-2024-0002', 4, 3,   90000,     0, 0,  90000, 'cash',     'completed'),
('TLU-2024-0003', 2, 2,  120000,     0, 0, 120000, 'momo',     'completed'),
('TLU-2024-0004', 4, NULL, 55000,    0, 0,  55000, 'cash',     'completed'),
('TLU-2024-0005', 4, 5,  210000,     0, 0, 210000, 'card',     'cancelled'),
('TLU-2024-0006', 2, 4,   85000,     0, 0,  85000, 'cash',     'processing');

INSERT INTO order_items (order_id, item_id, item_name, unit_price, quantity, subtotal) VALUES
(1, 5,  'Latte Art',         55000, 2, 110000),
(1, 12, 'Croissant Phô Mai', 35000, 2,  70000),
(2, 1,  'Bạc Xỉu Cốt Dừa', 45000, 2,  90000),
(3, 8,  'Trà Đào Cam Sả',   45000, 1,  45000),
(3, 7,  'Espresso',          35000, 1,  35000),
(3, 12, 'Croissant Phô Mai', 35000, 1,  35000),
(4, 4,  'Phin Sữa Đá',      35000, 1,  35000),
(4, 12, 'Croissant Phô Mai', 35000, 0,  20000),
(5, 6,  'Cold Brew',         55000, 2, 110000),
(5, 13, 'Bánh Mì Thịt TLU', 42000, 2,  84000),
(6, 5,  'Latte Art',         55000, 1,  55000),
(6, 3,  'Bạc Xỉu',          32000, 1,  32000);

-- ============================================================
-- 6. TỒN KHO NGUYÊN LIỆU
-- ============================================================
INSERT INTO inventory (item_code, name, unit, quantity, min_quantity) VALUES
('CF-001', 'Arabica Premium',      'Kg',   25.5,  5.0),
('MM-002', 'Sữa tươi thanh trùng', 'Lít',   4.2, 10.0),
('CH-008', 'Bột kem béo Richs',  'Bịch',  0.0,  3.0),
('SN-112', 'Đường nước DaVinci',   'Chai', 15.0,  4.0),
('CF-002', 'Robusta Buôn Ma Thuột','Kg',   18.0,  5.0),
('MM-003', 'Sữa đặc Ông Thọ',     'Lon',   8.0,  5.0),
('TR-001', 'Trà Oolong Thượng Hạng','Kg',  3.5,  1.0),
('FR-001', 'Đào tươi',            'Kg',    2.0,  2.0);

-- ============================================================
-- 7. LỊCH PHÂN CA (tuần hiện tại)
-- ============================================================
INSERT INTO shifts (user_id, shift_date, shift_type, start_time, end_time, task_note) VALUES
(2, CURDATE(),       'morning',   '06:00:00', '14:00:00', 'Brew Setup, Mở quán'),
(4, CURDATE(),       'morning',   '06:00:00', '14:00:00', 'Thu ngân ca sáng'),
(5, CURDATE(),       'afternoon', '14:00:00', '22:00:00', 'Phục vụ bàn ca chiều'),
(6, CURDATE(),       'afternoon', '14:00:00', '22:00:00', 'Bếp ca chiều'),
(2, CURDATE()+1,     'morning',   '06:00:00', '14:00:00', 'Training nhân viên mới'),
(4, CURDATE()+1,     'afternoon', '14:00:00', '22:00:00', 'Thu ngân ca chiều'),
(3, CURDATE()+2,     'morning',   '06:00:00', '14:00:00', 'Kiểm tra kho, họp staff');