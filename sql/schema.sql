
CREATE DATABASE IF NOT EXISTS cafe_tlu
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE cafe_tlu;


-- BẢNG 1: users — Tài khoản nhân viên

CREATE TABLE IF NOT EXISTS users (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    full_name     VARCHAR(100)  NOT NULL,
    email         VARCHAR(100)  NOT NULL UNIQUE,
    password_hash VARCHAR(255)  NOT NULL,
    role          ENUM('admin','manager','cashier','barista','server','kitchen') 
                  NOT NULL DEFAULT 'barista',
    phone         VARCHAR(20),
    avatar_path   VARCHAR(255),
    is_active     TINYINT(1)   NOT NULL DEFAULT 1,
    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login    DATETIME
);


-- BẢNG 2: categories — Danh mục món

CREATE TABLE IF NOT EXISTS categories (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    description TEXT,
    sort_order  INT          NOT NULL DEFAULT 0
);


-- BẢNG 3: menu_items — Món ăn uống

CREATE TABLE IF NOT EXISTS menu_items (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    category_id  INT           NOT NULL,
    name         VARCHAR(150)  NOT NULL,
    description  TEXT,
    base_price   DECIMAL(10,2) NOT NULL DEFAULT 0,
    image_path   VARCHAR(255),
    is_available TINYINT(1)   NOT NULL DEFAULT 1,
    is_featured  TINYINT(1)   NOT NULL DEFAULT 0,
    created_at   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT
);


-- BẢNG 4: item_variants — size S/M/L

CREATE TABLE IF NOT EXISTS item_variants (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    item_id     INT           NOT NULL,
    size_name   VARCHAR(20)   NOT NULL,  -- S, M, L, Nhỏ, Vừa, Lớn
    extra_price DECIMAL(10,2) NOT NULL DEFAULT 0,
    FOREIGN KEY (item_id) REFERENCES menu_items(id) ON DELETE CASCADE
);


-- BẢNG 5: orders — Đơn hàng

CREATE TABLE IF NOT EXISTS orders (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    order_code     VARCHAR(20)   NOT NULL UNIQUE,  -- TLU-2024-0001
    user_id        INT           NOT NULL,
    table_number   INT,
    subtotal       DECIMAL(12,2) NOT NULL DEFAULT 0,
    discount       DECIMAL(12,2) NOT NULL DEFAULT 0,
    tax            DECIMAL(12,2) NOT NULL DEFAULT 0,
    total_amount   DECIMAL(12,2) NOT NULL DEFAULT 0,
    payment_method ENUM('cash','card','transfer','momo') DEFAULT 'cash',
    status         ENUM('pending','processing','completed','cancelled') 
                   NOT NULL DEFAULT 'pending',
    note           TEXT,
    created_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT
);


-- BẢNG 6: order_items — Chi tiết từng món trong đơn

CREATE TABLE IF NOT EXISTS order_items (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    order_id   INT           NOT NULL,
    item_id    INT           NOT NULL,
    variant_id INT,
    item_name  VARCHAR(150)  NOT NULL,  -- Lưu tên lúc đặt (phòng khi sau đổi tên)
    unit_price DECIMAL(10,2) NOT NULL,
    quantity   INT           NOT NULL DEFAULT 1,
    subtotal   DECIMAL(10,2) NOT NULL,
    note       TEXT,
    FOREIGN KEY (order_id)   REFERENCES orders(id)        ON DELETE CASCADE,
    FOREIGN KEY (item_id)    REFERENCES menu_items(id)    ON DELETE RESTRICT,
    FOREIGN KEY (variant_id) REFERENCES item_variants(id) ON DELETE SET NULL
);


-- BẢNG 7: shifts — Lịch phân ca

CREATE TABLE IF NOT EXISTS shifts (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT         NOT NULL,
    shift_date  DATE        NOT NULL,
    shift_type  ENUM('morning','afternoon','evening') NOT NULL,
    start_time  TIME        NOT NULL,
    end_time    TIME        NOT NULL,
    task_note   TEXT,
    created_at  DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_shift (user_id, shift_date, shift_type)
);


-- BẢNG 8: attendance — Chấm công

CREATE TABLE IF NOT EXISTS attendance (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    user_id    INT      NOT NULL,
    shift_id   INT,
    check_in   DATETIME,
    check_out  DATETIME,
    status     ENUM('on_time','late','absent','half_day') DEFAULT 'on_time',
    work_date  DATE     NOT NULL,
    note       TEXT,
    FOREIGN KEY (user_id)  REFERENCES users(id)   ON DELETE CASCADE,
    FOREIGN KEY (shift_id) REFERENCES shifts(id)  ON DELETE SET NULL
);







-- INDEX để tăng tốc truy vấn thường dùng

CREATE INDEX idx_orders_created    ON orders(created_at);
CREATE INDEX idx_orders_status     ON orders(status);
CREATE INDEX idx_attendance_date   ON attendance(work_date);
CREATE INDEX idx_menu_category     ON menu_items(category_id);
CREATE INDEX idx_shifts_date       ON shifts(shift_date);