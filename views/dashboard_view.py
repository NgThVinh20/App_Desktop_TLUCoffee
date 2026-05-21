import customtkinter as ctk
from config.settings import *
from dao.order_dao import OrderDAO
from dao.menu_dao import MenuDAO
from datetime import datetime

class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=BG_PRIMARY)
        self.app  = app
        self.user = app.current_user
        self.pack(fill="both", expand=True)
        self._build()
    def _go_to_pos(self):
        parent = self.master
        while parent and not hasattr(parent, 'show_view'):
            parent = parent.master
        if parent:
            parent.show_view("pos")
    def _build(self):
        # ── Header
        header = ctk.CTkFrame(self, fg_color="white", height=64,
                               corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)

        h_inner = ctk.CTkFrame(header, fg_color="white")
        h_inner.pack(fill="both", expand=True, padx=24)

        # Tiêu đề
        left = ctk.CTkFrame(h_inner, fg_color="white")
        left.pack(side="left", fill="y")
        ctk.CTkLabel(left, text="OPERATIONS DASHBOARD",
                     font=("Segoe UI", 9),
                     text_color=TEXT_SECONDARY).pack(anchor="w", pady=(12, 0))
        now   = datetime.now()
        hour  = now.hour
        greet = "buổi sáng" if hour < 12 else "buổi chiều" if hour < 18 else "buổi tối"
        name  = self.user['full_name'].split()[-1]
        ctk.CTkLabel(left,
                     text=f"Chào {greet}, {name}",
                     font=("Segoe UI", 18, "bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w")

        # Nút tạo đơn
        right = ctk.CTkFrame(h_inner, fg_color="white")
        right.pack(side="right", fill="y", pady=12)
        ctk.CTkLabel(right,
                     text=f"Hôm nay: {now.strftime('%d/%m/%Y')}",
                     font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).pack(side="left", padx=12)
        ctk.CTkButton(right, text="+ Tạo đơn hàng mới",
                      font=("Segoe UI", 12, "bold"),
                      fg_color=PRIMARY_COLOR,
                      hover_color=PRIMARY_HOVER,
                      height=36, corner_radius=8,
                       command=self._go_to_pos).pack(side="left")

        # ── Scrollable content
        scroll = ctk.CTkScrollableFrame(self, fg_color=BG_PRIMARY)
        scroll.pack(fill="both", expand=True, padx=20, pady=16)

        # ── Metric cards
        self._build_metric_cards(scroll)

        # ── Đơn hàng gần đây
        self._build_recent_orders(scroll)

        # ── Bottom row
        self._build_bottom_row(scroll)

    def _build_metric_cards(self, parent):
        """3 thẻ số liệu tổng quan."""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(0, 16))
        row.grid_columnconfigure((0, 1, 2), weight=1)

        # Lấy dữ liệu
        revenue  = OrderDAO.get_revenue_today()
        counts   = OrderDAO.get_count_today()
        top_list = MenuDAO.get_top_selling(1)
        top_item = top_list[0]['item_name'] if top_list else "—"
        top_sold = top_list[0]['total_sold'] if top_list else 0

        # Card 1 — Doanh thu
        self._metric_card(
            row, col=0,
            icon="💰", icon_bg="#E6F1FB",
            badge="+12.5%", badge_color="#E1F5EE", badge_text="#0F6E56",
            label="Doanh thu hôm nay",
            value=f"{revenue:,.0f}đ",
            sub="So với trung bình ngày thường"
        )

        # Card 2 — Tổng đơn
        total     = counts.get('total', 0) or 0
        processing = int(counts.get('processing', 0) or 0)
        completed  = int(counts.get('completed', 0) or 0)
        self._metric_card(
            row, col=1,
            icon="🛒", icon_bg="#E1F5EE",
            badge=f"+{processing} đang xử lý",
            badge_color="#FAEEDA", badge_text="#854F0B",
            label="Tổng đơn hàng",
            value=str(total),
            sub=f"Đang xử lý: {processing}  •  Hoàn tất: {completed}"
        )

        # Card 3 — Món bán chạy (nền tối)
        self._hot_card(row, col=2, item_name=top_item, sold=top_sold)

    def _metric_card(self, parent, col, icon, icon_bg,
                     badge, badge_color, badge_text,
                     label, value, sub):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=12,
                             border_width=1, border_color="#e5e7eb")
        card.grid(row=0, column=col, padx=6, sticky="nsew")

        inner = ctk.CTkFrame(card, fg_color="white")
        inner.pack(fill="both", expand=True, padx=16, pady=16)

        # Top row: icon + badge
        top = ctk.CTkFrame(inner, fg_color="white")
        top.pack(fill="x")

        icon_box = ctk.CTkFrame(top, fg_color=icon_bg,
                                 width=40, height=40, corner_radius=10)
        icon_box.pack(side="left")
        icon_box.pack_propagate(False)
        ctk.CTkLabel(icon_box, text=icon,
                     font=("Segoe UI", 18)).place(relx=.5, rely=.5,
                                                   anchor="center")

        ctk.CTkLabel(top, text=badge,
                     font=("Segoe UI", 10, "bold"),
                     fg_color=badge_color,
                     text_color=badge_text,
                     corner_radius=6,
                     padx=6, pady=2).pack(side="right")

        # Label + Value
        ctk.CTkLabel(inner, text=label,
                     font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).pack(anchor="w", pady=(12, 0))
        ctk.CTkLabel(inner, text=value,
                     font=("Segoe UI", 26, "bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(inner, text=sub,
                     font=("Segoe UI", 10),
                     text_color=TEXT_SECONDARY).pack(anchor="w", pady=(2, 0))

    def _hot_card(self, parent, col, item_name, sold):
        card = ctk.CTkFrame(parent, fg_color="#2d4a3e",
                             corner_radius=12)
        card.grid(row=0, column=col, padx=6, sticky="nsew")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=16, pady=16)

        top = ctk.CTkFrame(inner, fg_color="transparent")
        top.pack(fill="x")
        ctk.CTkLabel(top, text="Món bán chạy nhất",
                     font=("Segoe UI", 10),
                     text_color="#9FE1CB").pack(side="left")
        ctk.CTkLabel(top, text="HOT 🔥",
                     font=("Segoe UI", 10, "bold"),
                     fg_color=ACCENT_COLOR,
                     text_color="white",
                     corner_radius=6,
                     padx=6, pady=2).pack(side="right")

        ctk.CTkLabel(inner, text=item_name,
                     font=("Segoe UI", 20, "bold"),
                     text_color="white",
                     wraplength=160).pack(anchor="w", pady=(12, 4))
        ctk.CTkLabel(inner, text=f"{sold} lượt bán hôm nay",
                     font=FONT_SMALL,
                     text_color="#9FE1CB").pack(anchor="w")
        ctk.CTkButton(inner, text="Xem chi tiết Menu →",
                  font=("Segoe UI", 11),
                  fg_color="transparent",
                  border_width=1,
                  border_color="#9FE1CB",
                  text_color="#9FE1CB",
                  hover_color="#1a3d35",
                  height=32, corner_radius=8,
                  command=self._go_to_menu
                  ).pack(anchor="w", pady=(12, 0))
    def _go_to_menu(self):
        # Tìm ngược lên widget cha cho đến khi gặp MainWindow
        parent = self.master
        while parent and not hasattr(parent, 'show_view'):
            parent = parent.master
        if parent:
            parent.show_view("menu")
    def _go_to_orders(self):
        """Chuyển sang trang Orders."""
        parent = self.master
        while parent and not hasattr(parent, 'show_view'):
            parent = parent.master
        if parent:
            parent.show_view("orders")
    def _build_recent_orders(self, parent):
        """Danh sách đơn hàng gần đây."""
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=12,
                             border_width=1, border_color="#e5e7eb")
        card.pack(fill="x", pady=(0, 16))

        # Header
        h = ctk.CTkFrame(card, fg_color="white")
        h.pack(fill="x", padx=20, pady=(16, 8))
        ctk.CTkLabel(h, text="Đơn hàng gần đây",
                     font=("Segoe UI", 14, "bold"),
                     text_color=TEXT_PRIMARY).pack(side="left")
        ctk.CTkButton(h, text="Xem tất cả →",
                      font=FONT_SMALL,
                      text_color=PRIMARY_COLOR,
                      fg_color="transparent", hover=False,
                      command=self._go_to_orders).pack(side="right")
        # Dữ liệu
        orders = OrderDAO.get_recent(6)

        status_map = {
            "completed":  ("Hoàn tất",    "#E1F5EE", "#0F6E56"),
            "processing": ("Đang xử lý",  "#FAEEDA", "#854F0B"),
            "pending":    ("Chờ xử lý",   "#E6F1FB", "#185FA5"),
            "cancelled":  ("Đã hủy",      "#FCEBEB", "#A32D2D"),
        }
        pay_map = {
            "cash": "Tiền mặt", "card": "Thẻ",
            "transfer": "Chuyển khoản", "momo": "Momo"
        }

        for i, o in enumerate(orders):
            row = ctk.CTkFrame(card, fg_color="white")
            row.pack(fill="x", padx=20, pady=4)

            if i > 0:
                ctk.CTkFrame(card, fg_color="#f3f4f6",
                             height=1).pack(fill="x", padx=20)

            # Mã đơn
            ctk.CTkLabel(row, text=o['order_code'],
                         font=("Segoe UI", 12, "bold"),
                         text_color=TEXT_PRIMARY,
                         width=110, anchor="w").pack(side="left")

            # Tổng tiền
            ctk.CTkLabel(row,
                         text=f"{float(o['total_amount']):,.0f}đ",
                         font=("Segoe UI", 12, "bold"),
                         text_color=PRIMARY_COLOR,
                         width=90).pack(side="left")

            # Phương thức
            ctk.CTkLabel(row,
                         text=pay_map.get(o['payment_method'], "—"),
                         font=FONT_SMALL,
                         text_color=TEXT_SECONDARY,
                         width=90).pack(side="left")

            # Trạng thái badge
            st = o['status']
            label, bg, fg = status_map.get(st, ("—", "#f3f4f6", "#666"))
            ctk.CTkLabel(row, text=label,
                         font=("Segoe UI", 10, "bold"),
                         fg_color=bg, text_color=fg,
                         corner_radius=6,
                         padx=8, pady=3).pack(side="right")

            # Thời gian
            if o['created_at']:
                time_str = o['created_at'].strftime("%H:%M  %d/%m")
            else:
                time_str = "—"
            ctk.CTkLabel(row, text=time_str,
                         font=FONT_SMALL,
                         text_color=TEXT_SECONDARY,
                         width=80).pack(side="right", padx=8)

        ctk.CTkFrame(card, fg_color="transparent",
                     height=8).pack()

    def _build_bottom_row(self, parent):
        """Hàng dưới: thống kê nhanh + tồn kho."""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(0, 20))
        row.grid_columnconfigure((0, 1), weight=1)

        # Card trái — Thống kê nhanh
        left = ctk.CTkFrame(row, fg_color="white", corner_radius=12,
                             border_width=1, border_color="#e5e7eb")
        left.grid(row=0, column=0, padx=(0, 8), sticky="nsew")

        ctk.CTkLabel(left, text="Thống kê nhanh",
                     font=("Segoe UI", 13, "bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", padx=16, pady=(14, 10))

        stats = [
            ("⏱", "Thời gian phục vụ TB", "4m 20s"),
            ("👍", "Hài lòng khách hàng",  "4.8 / 5.0"),
            ("👥", "Nhân sự đang trực",    "5 nhân viên"),
        ]
        for icon, label, val in stats:
            r = ctk.CTkFrame(left, fg_color="white")
            r.pack(fill="x", padx=16, pady=4)
            ctk.CTkLabel(r, text=f"{icon}  {label}",
                         font=FONT_SMALL,
                         text_color=TEXT_SECONDARY).pack(side="left")
            ctk.CTkLabel(r, text=val,
                         font=("Segoe UI", 12, "bold"),
                         text_color=TEXT_PRIMARY).pack(side="right")
        ctk.CTkFrame(left, height=12, fg_color="white").pack()

        # Card phải — Tồn kho cảnh báo
        from dao.inventory_dao import InventoryDAO
        right = ctk.CTkFrame(row, fg_color="white", corner_radius=12,
                              border_width=1, border_color="#e5e7eb")
        right.grid(row=0, column=1, padx=(8, 0), sticky="nsew")

        ctk.CTkLabel(right, text="Tồn kho cần chú ý",
                     font=("Segoe UI", 13, "bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", padx=16, pady=(14,10))

        low_items = InventoryDAO.get_low_stock()
        if low_items:
            for item in low_items[:4]:
                r = ctk.CTkFrame(right, fg_color="white")
                r.pack(fill="x", padx=16, pady=4)
                pct = (item['quantity'] / item['min_quantity'] * 100
                       if item['min_quantity'] > 0 else 100)
                color = DANGER_COLOR if pct <= 0 else WARNING_COLOR
                ctk.CTkLabel(r, text=f"⚠ {item['name']}",
                             font=FONT_SMALL,
                             text_color=color).pack(side="left")
                ctk.CTkLabel(r,
                             text=f"{float(item['quantity']):.1f} {item['unit']}",
                             font=("Segoe UI", 11, "bold"),
                             text_color=color).pack(side="right")
        else:
            ctk.CTkLabel(right, text="✓ Tất cả nguyên liệu đủ hàng",
                         font=FONT_SMALL,
                         text_color=SUCCESS_COLOR).pack(padx=16, pady=8)
        ctk.CTkFrame(right, height=12, fg_color="white").pack()
 