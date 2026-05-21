import customtkinter as ctk
from config.settings import *
from dao.order_dao import OrderDAO
from datetime import datetime
import tkinter.messagebox as msgbox


class OrdersView(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=BG_PRIMARY)
        self.app        = app
        self.user       = app.current_user
        self.all_orders = []
        self.pack(fill="both", expand=True)
        self._build()
        self._load_data()

   
    #  BUILD UI
   
    def _build(self):
        # ── Header
        header = ctk.CTkFrame(self, fg_color="white",
                               height=64, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)

        h = ctk.CTkFrame(header, fg_color="white")
        h.pack(fill="both", expand=True, padx=24)

        # Tiêu đề
        left = ctk.CTkFrame(h, fg_color="white")
        left.pack(side="left", fill="y")
        ctk.CTkLabel(left, text="Lịch sử đơn hàng",
                     font=("Segoe UI", 18, "bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", pady=(12, 0))
        ctk.CTkLabel(left, text="Xem và quản lý tất cả giao dịch",
                     font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).pack(anchor="w")

        # Bộ lọc bên phải
        right = ctk.CTkFrame(h, fg_color="white")
        right.pack(side="right", fill="y", pady=14)

        # Từ ngày
        ctk.CTkLabel(right, text="Từ:",
                     font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).pack(side="left", padx=(0, 4))
        self.from_date_var = ctk.StringVar()
        ctk.CTkEntry(right, textvariable=self.from_date_var,
                     placeholder_text="dd/mm/yyyy",
                     width=110, height=36,
                     corner_radius=8).pack(side="left", padx=(0, 8))

        # Đến ngày
        ctk.CTkLabel(right, text="Đến:",
                     font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).pack(side="left", padx=(0, 4))
        self.to_date_var = ctk.StringVar()
        ctk.CTkEntry(right, textvariable=self.to_date_var,
                     placeholder_text="dd/mm/yyyy",
                     width=110, height=36,
                     corner_radius=8).pack(side="left", padx=(0, 8))

        # Nút Lọc
        ctk.CTkButton(right, text="🔍 Lọc",
                      font=FONT_SMALL,
                      fg_color=PRIMARY_COLOR,
                      hover_color=PRIMARY_HOVER,
                      height=36, corner_radius=8, width=80,
                      command=self._filter).pack(side="left", padx=(0, 6))

        # Nút Reset
        ctk.CTkButton(right, text="↺ Reset",
                      font=FONT_SMALL,
                      fg_color=BG_SECONDARY,
                      text_color=TEXT_PRIMARY,
                      hover_color="#e5e7eb",
                      height=36, corner_radius=8, width=80,
                      command=self._reset_filter).pack(side="left")

        # ── Body
        body = ctk.CTkFrame(self, fg_color=BG_PRIMARY)
        body.pack(fill="both", expand=True, padx=20, pady=16)

        # ── Bảng đơn hàng
        table_card = ctk.CTkFrame(body, fg_color="white",
                                   corner_radius=12,
                                   border_width=1,
                                   border_color="#e5e7eb")
        table_card.pack(fill="both", expand=True)

        # Header bảng
        thead = ctk.CTkFrame(table_card, fg_color=BG_SECONDARY,
                              corner_radius=0, height=40)
        thead.pack(fill="x")
        thead.pack_propagate(False)

        cols = [
            ("Mã đơn",     0.02),
            ("Thời gian",  0.16),
            ("Tổng tiền",  0.32),
            ("Thanh toán", 0.44),
            ("Nhân viên",  0.57),
            ("Trạng thái", 0.72),
            ("Thao tác",   0.87),
        ]
        for label, relx in cols:
            ctk.CTkLabel(thead, text=label,
                         font=("Segoe UI", 11, "bold"),
                         text_color=TEXT_SECONDARY).place(
                             relx=relx, rely=0.5, anchor="w")

        # Scrollable rows
        self.table_scroll = ctk.CTkScrollableFrame(
            table_card, fg_color="white")
        self.table_scroll.pack(fill="both", expand=True)

        # Footer
        footer = ctk.CTkFrame(table_card, fg_color="white",
                               height=40, corner_radius=0)
        footer.pack(fill="x")
        footer.pack_propagate(False)
        self.page_label = ctk.CTkLabel(
            footer, text="",
            font=FONT_SMALL, text_color=TEXT_SECONDARY)
        self.page_label.pack(side="left", padx=16, pady=10)

   
    #  LOAD & FILTER
   
    def _load_data(self):
        self.all_orders = OrderDAO.get_all()
        self._filter()

    def _filter(self):
        from_date = None
        to_date   = None

        try:
            if self.from_date_var.get().strip():
                from_date = datetime.strptime(
                    self.from_date_var.get().strip(), "%d/%m/%Y").date()
        except ValueError:
            pass

        try:
            if self.to_date_var.get().strip():
                to_date = datetime.strptime(
                    self.to_date_var.get().strip(), "%d/%m/%Y").date()
        except ValueError:
            pass

        orders = self.all_orders

        if from_date:
            orders = [o for o in orders
                      if o.get('created_at') and
                      o['created_at'].date() >= from_date]
        if to_date:
            orders = [o for o in orders
                      if o.get('created_at') and
                      o['created_at'].date() <= to_date]

        self._render_table(orders)

    def _reset_filter(self):
        self.from_date_var.set("")
        self.to_date_var.set("")
        self._render_table(self.all_orders)

    #  RENDER BẢNG
    def _render_table(self, orders: list):
        # Xóa widget cũ
        for w in self.table_scroll.winfo_children():
            w.destroy()

        if not orders:
            ctk.CTkLabel(self.table_scroll,
                         text="Không tìm thấy đơn hàng nào",
                         font=FONT_NORMAL,
                         text_color=TEXT_SECONDARY).pack(pady=40)
            self.page_label.configure(text="0 đơn")
            return

        status_cfg = {
            "completed":  ("Hoàn tất",   "#E1F5EE", "#0F6E56"),
            "processing": ("Đang xử lý", "#FAEEDA", "#854F0B"),
            "pending":    ("Chờ xử lý",  "#E6F1FB", "#185FA5"),
            "cancelled":  ("Đã hủy",     "#FCEBEB", "#A32D2D"),
        }
        pay_map = {
            "cash":     "Tiền mặt",
            "card":     "Thẻ/POS",
            "transfer": "Chuyển khoản",
            "momo":     "Momo",
        }

        for i, order in enumerate(orders):
            bg  = "white" if i % 2 == 0 else "#fafafa"
            row = ctk.CTkFrame(self.table_scroll,
                               fg_color=bg, height=48,
                               corner_radius=0)
            row.pack(fill="x")
            row.pack_propagate(False)

            # Mã đơn
            ctk.CTkLabel(row, text=order['order_code'],
                         font=("Segoe UI", 11, "bold"),
                         text_color=PRIMARY_COLOR,
                         anchor="w").place(relx=0.02, rely=0.5,
                                           anchor="w", relwidth=0.13)

            # Thời gian
            time_str = (order['created_at'].strftime("%H:%M  %d/%m")
                        if order.get('created_at') else "—")
            ctk.CTkLabel(row, text=time_str,
                         font=FONT_SMALL,
                         text_color=TEXT_SECONDARY,
                         anchor="w").place(relx=0.16, rely=0.5,
                                           anchor="w", relwidth=0.14)

            # Tổng tiền
            ctk.CTkLabel(row,
                         text=f"{float(order['total_amount']):,.0f}đ",
                         font=("Segoe UI", 12, "bold"),
                         text_color=TEXT_PRIMARY).place(
                             relx=0.32, rely=0.5, anchor="w")

            # Thanh toán
            ctk.CTkLabel(row,
                         text=pay_map.get(order['payment_method'], "—"),
                         font=FONT_SMALL,
                         text_color=TEXT_SECONDARY).place(
                             relx=0.44, rely=0.5, anchor="w")

            # Nhân viên
            ctk.CTkLabel(row,
                         text=order.get('staff_name', '—'),
                         font=FONT_SMALL,
                         text_color=TEXT_SECONDARY).place(
                             relx=0.57, rely=0.5, anchor="w")

            # Trạng thái badge
            st             = order['status']
            lb, bg_s, fg_s = status_cfg.get(
                st, ("—", BG_SECONDARY, TEXT_SECONDARY))
            ctk.CTkLabel(row, text=lb,
                         font=("Segoe UI", 10, "bold"),
                         fg_color=bg_s, text_color=fg_s,
                         corner_radius=6,
                         padx=8, pady=3).place(
                             relx=0.72, rely=0.5, anchor="w")

            # Nút chi tiết
            ctk.CTkButton(row, text="👁 Chi tiết",
                          width=80, height=30,
                          corner_radius=6,
                          fg_color=BG_SECONDARY,
                          text_color=TEXT_PRIMARY,
                          hover_color="#e5e7eb",
                          font=FONT_SMALL,
                          command=lambda o=order: self._show_detail(o)
                          ).place(relx=0.87, rely=0.5, anchor="w")

            # Divider
            ctk.CTkFrame(self.table_scroll,
                         fg_color="#f3f4f6", height=1).pack(fill="x")

        self.page_label.configure(
            text=f"Hiển thị {len(orders)} trong tổng số "
                 f"{len(self.all_orders)} đơn")

 
    #  CHI TIẾT ĐƠN HÀNG
    
    def _show_detail(self, order: dict):
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Chi tiết — {order['order_code']}")
        dialog.geometry("520x580")
        dialog.resizable(False, False)
        dialog.grab_set()

        dialog.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width()  - 520) // 2
        y = self.winfo_rooty() + (self.winfo_height() - 580) // 2
        dialog.geometry(f"520x580+{x}+{y}")

        scroll = ctk.CTkScrollableFrame(dialog, fg_color="white")
        scroll.pack(fill="both", expand=True, padx=8, pady=8)

        #  Tiêu đề + badge trạng thái
        status_cfg = {
            "completed":  ("Hoàn tất",   "#E1F5EE", "#0F6E56"),
            "processing": ("Đang xử lý", "#FAEEDA", "#854F0B"),
            "pending":    ("Chờ xử lý",  "#E6F1FB", "#185FA5"),
            "cancelled":  ("Đã hủy",     "#FCEBEB", "#A32D2D"),
        }
        st_label, st_bg, st_fg = status_cfg.get(
            order['status'], ("—", BG_SECONDARY, TEXT_SECONDARY))

        top = ctk.CTkFrame(scroll, fg_color="white")
        top.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(top,
                     text=f"#{order['order_code']}",
                     font=("Segoe UI", 16, "bold"),
                     text_color=PRIMARY_COLOR).pack(side="left")
        ctk.CTkLabel(top, text=st_label,
                     font=("Segoe UI", 10, "bold"),
                     fg_color=st_bg, text_color=st_fg,
                     corner_radius=6, padx=8, pady=4).pack(side="right")

        #  Thông tin đơn
        pay_map = {
            "cash":     "Tiền mặt",
            "card":     "Thẻ/POS",
            "transfer": "Chuyển khoản",
            "momo":     "Momo"
        }
        time_str = (order['created_at'].strftime("%H:%M — %d/%m/%Y")
                    if order.get('created_at') else "—")

        info_data = [
            ("🕐 Thời gian",  time_str),
            ("👤 Nhân viên",  order.get('staff_name', '—')),
            ("💳 Thanh toán", pay_map.get(order['payment_method'], '—')),
            ("🪑 Số bàn",
             str(order['table_number'])
             if order.get('table_number') else "Mang về"),
            ("📝 Ghi chú",   order.get('note') or "Không có"),
        ]

        info_card = ctk.CTkFrame(scroll, fg_color=BG_SECONDARY,
                                  corner_radius=10)
        info_card.pack(fill="x", pady=(0, 12))
        for label, value in info_data:
            r = ctk.CTkFrame(info_card, fg_color="transparent")
            r.pack(fill="x", padx=14, pady=4)
            ctk.CTkLabel(r, text=label,
                         font=FONT_SMALL,
                         text_color=TEXT_SECONDARY,
                         width=110, anchor="w").pack(side="left")
            ctk.CTkLabel(r, text=value,
                         font=("Segoe UI", 12, "bold"),
                         text_color=TEXT_PRIMARY).pack(side="left")

        #  Danh sách món
        ctk.CTkLabel(scroll, text="🛒  Danh sách món",
                     font=("Segoe UI", 13, "bold"),
                     text_color=TEXT_PRIMARY).pack(
                         anchor="w", pady=(0, 6))

        items      = OrderDAO.get_items(order['id'])
        items_card = ctk.CTkFrame(scroll, fg_color="white",
                                   corner_radius=10,
                                   border_width=1,
                                   border_color="#e5e7eb")
        items_card.pack(fill="x", pady=(0, 12))

        # Header bảng món
        thead = ctk.CTkFrame(items_card, fg_color=BG_SECONDARY,
                              corner_radius=0, height=34)
        thead.pack(fill="x")
        thead.pack_propagate(False)
        for text, relx in [("Tên món",     0.02),
                            ("SL",          0.55),
                            ("Đơn giá",    0.65),
                            ("Thành tiền",  0.80)]:
            ctk.CTkLabel(thead, text=text,
                         font=("Segoe UI", 10, "bold"),
                         text_color=TEXT_SECONDARY).place(
                             relx=relx, rely=0.5, anchor="w")

        for item in items:
            r = ctk.CTkFrame(items_card, fg_color="white", height=36)
            r.pack(fill="x")
            r.pack_propagate(False)
            ctk.CTkLabel(r, text=item['item_name'],
                         font=FONT_SMALL,
                         text_color=TEXT_PRIMARY,
                         anchor="w").place(relx=0.02, rely=0.5,
                                           anchor="w", relwidth=0.50)
            ctk.CTkLabel(r, text=str(item['quantity']),
                         font=FONT_SMALL,
                         text_color=TEXT_SECONDARY).place(
                             relx=0.55, rely=0.5, anchor="w")
            ctk.CTkLabel(r,
                         text=f"{float(item['unit_price']):,.0f}đ",
                         font=FONT_SMALL,
                         text_color=TEXT_SECONDARY).place(
                             relx=0.65, rely=0.5, anchor="w")
            ctk.CTkLabel(r,
                         text=f"{float(item['subtotal']):,.0f}đ",
                         font=("Segoe UI", 11, "bold"),
                         text_color=PRIMARY_COLOR).place(
                             relx=0.80, rely=0.5, anchor="w")
            ctk.CTkFrame(items_card,
                         fg_color="#f3f4f6", height=1).pack(fill="x")

        #  Tổng cộng
        total_card = ctk.CTkFrame(scroll, fg_color=BG_SECONDARY,
                                   corner_radius=10)
        total_card.pack(fill="x", pady=(0, 12))

        subtotal = float(order['subtotal'])
        discount = float(order['discount'])
        total    = float(order['total_amount'])

        for label, value, bold in [
            ("Tạm tính",  f"{subtotal:,.0f}đ",  False),
            ("Giảm giá",  f"-{discount:,.0f}đ", False),
            ("TỔNG TIỀN", f"{total:,.0f}đ",     True),
        ]:
            r = ctk.CTkFrame(total_card, fg_color="transparent")
            r.pack(fill="x", padx=14, pady=4)
            ctk.CTkLabel(r, text=label,
                         font=("Segoe UI", 12, "bold") if bold
                         else FONT_SMALL,
                         text_color=PRIMARY_COLOR if bold
                         else TEXT_SECONDARY).pack(side="left")
            ctk.CTkLabel(r, text=value,
                         font=("Segoe UI", 14, "bold") if bold
                         else FONT_SMALL,
                         text_color=PRIMARY_COLOR if bold
                         else TEXT_PRIMARY).pack(side="right")

        #  Nút đóng
        ctk.CTkButton(scroll, text="Đóng",
                      font=FONT_NORMAL,
                      fg_color=BG_SECONDARY,
                      text_color=TEXT_PRIMARY,
                      hover_color="#e5e7eb",
                      height=40, corner_radius=8,
                      command=dialog.destroy).pack(
                          fill="x", pady=(8, 0))