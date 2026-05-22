import customtkinter as ctk
from config.settings import *
from dao.order_dao import OrderDAO
from dao.menu_dao import MenuDAO
from dao.shift_dao import ShiftDAO
from datetime import datetime, date, timedelta


class DashboardView(ctk.CTkFrame):
    """
    Màn hình Dashboard — trang chủ sau khi đăng nhập.
    Hiển thị tổng quan: doanh thu, đơn hàng, món bán chạy,
    đơn gần đây, thống kê 7 ngày và nhân viên ca hiện tại.
    """

    def __init__(self, parent, app):
        super().__init__(parent, fg_color=BG_PRIMARY)
        self.app  = app
        self.user = app.current_user
        self.pack(fill="both", expand=True)
        self._build()

    def _go_to(self, key):
        """Chuyển sang màn hình khác trong MainWindow."""
        parent = self.master
        while parent and not hasattr(parent, 'show_view'):
            parent = parent.master
        if parent:
            parent.show_view(key)

    def _build(self):
        """Dựng toàn bộ giao diện Dashboard."""
        # ── Header
        header = ctk.CTkFrame(self, fg_color="white",
                               height=64, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)

        h = ctk.CTkFrame(header, fg_color="white")
        h.pack(fill="both", expand=True, padx=24)

        left = ctk.CTkFrame(h, fg_color="white")
        left.pack(side="left", fill="y")
        ctk.CTkLabel(left, text="Trang quản lý nội bộ",
                     font=("Segoe UI", 9),
                     text_color=TEXT_SECONDARY).pack(anchor="w", pady=(12, 0))
        now  = datetime.now()
        name = self.user['full_name'].split()[-1]
        ctk.CTkLabel(left, text=f"Xin chào, {name}",
                     font=("Segoe UI", 18, "bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w")

        right = ctk.CTkFrame(h, fg_color="white")
        right.pack(side="right", fill="y", pady=12)
        ctk.CTkLabel(right,
                     text=f"Hôm nay: {now.strftime('%d/%m/%Y')}",
                     font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).pack(side="left", padx=12)
        ctk.CTkButton(right, text="+ Tạo đơn hàng mới",
                      font=("Segoe UI", 12, "bold"),
                      fg_color=PRIMARY_COLOR, hover_color=PRIMARY_HOVER,
                      height=36, corner_radius=8,
                      command=lambda: self._go_to("pos")
                      ).pack(side="left")

        # ── Scrollable content
        scroll = ctk.CTkScrollableFrame(self, fg_color=BG_PRIMARY)
        scroll.pack(fill="both", expand=True, padx=20, pady=16)

        self._build_metric_cards(scroll)
        self._build_recent_orders(scroll)
        self._build_weekly_chart(scroll)      # ← THỐNG KÊ TUẦN
        self._build_bottom_row(scroll)

    # ══════════════════════════════════════════
    #  3 CARD METRIC
    # ══════════════════════════════════════════
    def _build_metric_cards(self, parent):
        """Vẽ 3 card số liệu tổng quan: doanh thu, đơn hàng, món bán chạy."""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(0, 16))
        row.grid_columnconfigure((0, 1, 2), weight=1)

        revenue  = OrderDAO.get_revenue_today()
        counts   = OrderDAO.get_count_today()
        top_list = MenuDAO.get_top_selling(1)
        top_item = top_list[0]['item_name'] if top_list else "—"
        top_sold = top_list[0]['total_sold'] if top_list else 0

        self._metric_card(
            row, col=0,
            icon="💰", icon_bg="#E6F1FB",
            badge="+12.5%", badge_color="#E1F5EE", badge_text="#0F6E56",
            label="Doanh thu hôm nay",
            value=f"{revenue:,.0f}đ",
            sub=""
        )

        total = int(counts.get('total', 0) or 0)
        self._metric_card(
            row, col=1,
            icon="🛒", icon_bg="#E1F5EE",
            badge="Hôm nay",
            badge_color="#E1F5EE", badge_text="#0F6E56",
            label="Tổng đơn hàng",
            value=str(total),
            sub="Tổng số đơn đã tạo trong ngày"
        )

        self._hot_card(row, col=2, item_name=top_item, sold=top_sold)

    def _metric_card(self, parent, col, icon, icon_bg,
                     badge, badge_color, badge_text,
                     label, value, sub):
        """Vẽ 1 card metric nền trắng — tái sử dụng cho nhiều loại số liệu."""
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=12,
                             border_width=1, border_color="#e5e7eb")
        card.grid(row=0, column=col, padx=6, sticky="nsew")

        inner = ctk.CTkFrame(card, fg_color="white")
        inner.pack(fill="both", expand=True, padx=16, pady=16)

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
                     fg_color=badge_color, text_color=badge_text,
                     corner_radius=6, padx=6, pady=2).pack(side="right")

        ctk.CTkLabel(inner, text=label,
                     font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).pack(anchor="w", pady=(12, 0))
        ctk.CTkLabel(inner, text=value,
                     font=("Segoe UI", 26, "bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w")
        if sub:
            ctk.CTkLabel(inner, text=sub,
                         font=("Segoe UI", 10),
                         text_color=TEXT_SECONDARY).pack(anchor="w", pady=(2, 0))

    def _hot_card(self, parent, col, item_name, sold):
        """Vẽ card món bán chạy nhất — nền tối xanh."""
        card = ctk.CTkFrame(parent, fg_color="#2d4a3e", corner_radius=12)
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
                     fg_color=ACCENT_COLOR, text_color="white",
                     corner_radius=6, padx=6, pady=2).pack(side="right")

        ctk.CTkLabel(inner, text=item_name,
                     font=("Segoe UI", 20, "bold"),
                     text_color="white", wraplength=160).pack(
                         anchor="w", pady=(12, 4))
        ctk.CTkLabel(inner, text=f"{sold} lượt bán hôm nay",
                     font=FONT_SMALL, text_color="#9FE1CB").pack(anchor="w")
        ctk.CTkButton(inner, text="Xem chi tiết Menu →",
                      font=("Segoe UI", 11),
                      fg_color="transparent",
                      border_width=1, border_color="#9FE1CB",
                      text_color="#9FE1CB", hover_color="#1a3d35",
                      height=32, corner_radius=8,
                      command=lambda: self._go_to("menu")
                      ).pack(anchor="w", pady=(12, 0))

    # ══════════════════════════════════════════
    #  ĐƠN HÀNG GẦN ĐÂY
    # ══════════════════════════════════════════
    def _build_recent_orders(self, parent):
        """Vẽ bảng 6 đơn hàng gần nhất."""
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=12,
                             border_width=1, border_color="#e5e7eb")
        card.pack(fill="x", pady=(0, 16))

        h = ctk.CTkFrame(card, fg_color="white")
        h.pack(fill="x", padx=20, pady=(16, 8))
        ctk.CTkLabel(h, text="Đơn hàng gần đây",
                     font=("Segoe UI", 14, "bold"),
                     text_color=TEXT_PRIMARY).pack(side="left")
        ctk.CTkButton(h, text="Xem tất cả →",
                      font=FONT_SMALL, text_color=PRIMARY_COLOR,
                      fg_color="transparent", hover=False,
                      command=lambda: self._go_to("orders")
                      ).pack(side="right")

        status_map = {
            "completed":  ("Hoàn tất",   "#E1F5EE", "#0F6E56"),
            "processing": ("Đang xử lý", "#FAEEDA", "#854F0B"),
            "pending":    ("Chờ xử lý",  "#E6F1FB", "#185FA5"),
            "cancelled":  ("Đã hủy",     "#FCEBEB", "#A32D2D"),
        }
        pay_map = {
            "cash": "Tiền mặt", "card": "Thẻ",
            "transfer": "Chuyển khoản", "momo": "Momo"
        }

        for i, o in enumerate(OrderDAO.get_recent(6)):
            if i > 0:
                ctk.CTkFrame(card, fg_color="#f3f4f6",
                             height=1).pack(fill="x", padx=20)
            row = ctk.CTkFrame(card, fg_color="white")
            row.pack(fill="x", padx=20, pady=4)

            left = ctk.CTkFrame(row, fg_color="white")
            left.pack(side="left")
            ctk.CTkLabel(left, text=o['order_code'],
                         font=("Segoe UI", 12, "bold"),
                         text_color=TEXT_PRIMARY).pack(side="left", padx=(0, 16))
            ctk.CTkLabel(left,
                         text=f"{float(o['total_amount']):,.0f}đ",
                         font=("Segoe UI", 12, "bold"),
                         text_color=PRIMARY_COLOR).pack(side="left", padx=(0, 16))
            ctk.CTkLabel(left,
                         text=pay_map.get(o['payment_method'], "—"),
                         font=FONT_SMALL,
                         text_color=TEXT_SECONDARY).pack(side="left")

            right = ctk.CTkFrame(row, fg_color="white")
            right.pack(side="right")
            time_str = o['created_at'].strftime("%H:%M  %d/%m") \
                if o.get('created_at') else "—"
            ctk.CTkLabel(right, text=time_str,
                         font=FONT_SMALL,
                         text_color=TEXT_SECONDARY).pack(side="left", padx=(0, 12))
            lb, bg, fg = status_map.get(o['status'], ("—", "#f3f4f6", "#666"))
            ctk.CTkLabel(right, text=lb,
                         font=("Segoe UI", 10, "bold"),
                         fg_color=bg, text_color=fg,
                         corner_radius=6,
                         padx=8, pady=3).pack(side="left")

        ctk.CTkFrame(card, fg_color="transparent", height=8).pack()

    # ══════════════════════════════════════════
    #  THỐNG KÊ 7 NGÀY QUA  ← MỚI
    # ══════════════════════════════════════════
    def _build_weekly_chart(self, parent):
        """
        Vẽ biểu đồ cột doanh thu 7 ngày qua.
        Lấy dữ liệu từ OrderDAO.get_revenue_7days(),
        tính chiều cao mỗi cột theo tỷ lệ với ngày cao nhất.
        """
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=12,
                             border_width=1, border_color="#e5e7eb")
        card.pack(fill="x", pady=(0, 16))

        # ── Header
        h = ctk.CTkFrame(card, fg_color="white")
        h.pack(fill="x", padx=20, pady=(16, 4))
        ctk.CTkLabel(h, text="Doanh thu 7 ngày qua",
                     font=("Segoe UI", 14, "bold"),
                     text_color=TEXT_PRIMARY).pack(side="left")

        # ── Lấy dữ liệu
        try:
            raw = OrderDAO.get_revenue_7days()
        except Exception:
            raw = []

        # Tạo dict ngày → doanh thu
        revenue_map = {}
        for r in raw:
            d = r['ngay']
            if hasattr(d, 'date'):
                d = d.date()
            revenue_map[d] = float(r['doanh_thu'])

        # Tạo danh sách 7 ngày liên tiếp (hôm nay là ngày cuối)
        today   = date.today()
        days    = [today - timedelta(days=6 - i) for i in range(7)]
        values  = [revenue_map.get(d, 0) for d in days]
        max_val = max(values) if any(v > 0 for v in values) else 1

        # ── Tổng doanh thu tuần
        total_week = sum(values)
        ctk.CTkLabel(h,
                     text=f"Tổng: {total_week:,.0f}đ",
                     font=("Segoe UI", 12, "bold"),
                     text_color=PRIMARY_COLOR).pack(side="right")

        # ── Vùng biểu đồ
        chart_frame = ctk.CTkFrame(card, fg_color="white")
        chart_frame.pack(fill="x", padx=20, pady=(8, 16))

        BAR_H    = 120   # chiều cao tối đa của cột
        DAY_NAMES = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]

        for i, (d, val) in enumerate(zip(days, values)):
            col = ctk.CTkFrame(chart_frame, fg_color="white")
            col.pack(side="left", fill="both", expand=True, padx=3)

            is_today = (d == today)

            # Giá trị tiền phía trên cột
            if val > 0:
                val_text = f"{val/1000:.0f}k" if val < 1_000_000 \
                    else f"{val/1_000_000:.1f}M"
            else:
                val_text = ""
            ctk.CTkLabel(col, text=val_text,
                         font=("Segoe UI", 9, "bold"),
                         text_color=PRIMARY_COLOR).pack()

            # Cột bar
            bar_h = max(4, int(BAR_H * val / max_val)) if val > 0 else 4
            spacer_h = BAR_H - bar_h

            # Khoảng trống phía trên để căn đáy
            ctk.CTkFrame(col, fg_color="white",
                         height=spacer_h).pack()

            # Thanh màu
            bar_color = PRIMARY_COLOR if is_today else "#9FE1CB"
            ctk.CTkFrame(col, fg_color=bar_color,
                         height=bar_h, corner_radius=4).pack(fill="x")

            # Nhãn ngày phía dưới
            day_name = DAY_NAMES[d.weekday()]
            label_text = f"{day_name}\n{d.strftime('%d/%m')}"
            ctk.CTkLabel(col, text=label_text,
                         font=("Segoe UI", 9, "bold") if is_today
                         else ("Segoe UI", 9),
                         text_color=PRIMARY_COLOR if is_today
                         else TEXT_SECONDARY,
                         justify="center").pack(pady=(4, 0))

        # ── Chú thích
        legend = ctk.CTkFrame(card, fg_color="white")
        legend.pack(anchor="e", padx=20, pady=(0, 12))

        ctk.CTkFrame(legend, fg_color=PRIMARY_COLOR,
                     width=12, height=12, corner_radius=2).pack(side="left")
        ctk.CTkLabel(legend, text=" Hôm nay",
                     font=("Segoe UI", 9),
                     text_color=TEXT_SECONDARY).pack(side="left", padx=(0, 12))

        ctk.CTkFrame(legend, fg_color="#9FE1CB",
                     width=12, height=12, corner_radius=2).pack(side="left")
        ctk.CTkLabel(legend, text=" Các ngày khác",
                     font=("Segoe UI", 9),
                     text_color=TEXT_SECONDARY).pack(side="left")

    # ══════════════════════════════════════════
    #  HÀNG DƯỚI CÙNG
    # ══════════════════════════════════════════
    def _build_bottom_row(self, parent):
        """Vẽ 2 card dưới cùng: thống kê nhanh + nhân viên ca hiện tại."""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(0, 20))
        row.grid_columnconfigure((0, 1), weight=1)

        self._build_quick_stats(row, col=0)
        self._build_current_shift(row, col=1)

    def _build_quick_stats(self, parent, col):
        """Card thống kê nhanh — thời gian phục vụ và điểm hài lòng."""
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=12,
                             border_width=1, border_color="#e5e7eb")
        card.grid(row=0, column=col, padx=(0, 8), sticky="nsew")

        ctk.CTkLabel(card, text="Thống kê nhanh",
                     font=("Segoe UI", 13, "bold"),
                     text_color=TEXT_PRIMARY).pack(
                         anchor="w", padx=16, pady=(14, 10))

        for icon, label, val in [
            ("⏱", "Thời gian phục vụ TB", "4m 20s"),
            ("👍", "Hài lòng khách hàng",  "4.8 / 5.0"),
        ]:
            r = ctk.CTkFrame(card, fg_color="white")
            r.pack(fill="x", padx=16, pady=4)
            ctk.CTkLabel(r, text=f"{icon}  {label}",
                         font=FONT_SMALL,
                         text_color=TEXT_SECONDARY).pack(side="left")
            ctk.CTkLabel(r, text=val,
                         font=("Segoe UI", 12, "bold"),
                         text_color=TEXT_PRIMARY).pack(side="right")

        ctk.CTkFrame(card, height=12, fg_color="white").pack()

    def _build_current_shift(self, parent, col):
        """
        Card nhân viên đang làm ca hiện tại.
        Tự xác định ca theo giờ thực tế và lọc từ lịch tuần.
        """
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=12,
                             border_width=1, border_color="#e5e7eb")
        card.grid(row=0, column=col, padx=(8, 0), sticky="nsew")

        h = ctk.CTkFrame(card, fg_color="white")
        h.pack(fill="x", padx=16, pady=(14, 6))
        ctk.CTkLabel(h, text="Nhân viên ca hiện tại",
                     font=("Segoe UI", 13, "bold"),
                     text_color=TEXT_PRIMARY).pack(side="left")
        ctk.CTkButton(h, text="Xem lịch →",
                      font=FONT_SMALL, text_color=PRIMARY_COLOR,
                      fg_color="transparent", hover=False,
                      command=lambda: self._go_to("shift")
                      ).pack(side="right")

        now_hour = datetime.now().hour
        now_minute = datetime.now().minute
        if 6 <= now_hour < 13 or (now_hour == 13 and now_minute < 30):
            current_shift      = "morning"
            shift_label        = "Ca sáng  (06:00 – 13:30)"
            badge_bg, badge_fg = "#E1F5EE", "#0F6E56"
        elif (now_hour == 13 and now_minute >= 30) or (14 <= now_hour < 17):
            current_shift      = "afternoon"
            shift_label        = "Ca chiều (13:30 – 17:00)"
            badge_bg, badge_fg = "#FAEEDA", "#854F0B"
        else:
            current_shift      = "evening"
            shift_label        = "Ca tối   (17:00 – 22:00)"
            badge_bg, badge_fg = "#EEEDFE", "#3C3489"

        ctk.CTkLabel(card, text=shift_label,
                     font=("Segoe UI", 10, "bold"),
                     fg_color=badge_bg, text_color=badge_fg,
                     corner_radius=6, padx=8, pady=3).pack(
                         anchor="w", padx=16, pady=(0, 8))

        try:
            today      = date.today()
            week_start = today - timedelta(days=today.weekday())
            all_shifts = ShiftDAO.get_by_week(week_start)
            on_duty    = [
                s for s in all_shifts
                if s['shift_type'] == current_shift
                and self._eq_date(s['shift_date'], today)
            ]
        except Exception:
            on_duty = []

        ROLE_DISPLAY = {
            "admin": "Admin",    "manager": "Quản lý",
            "cashier": "Thu ngân", "barista": "Barista",
            "server": "Phục vụ",  "kitchen": "Bếp",
        }
        ROLE_COLORS = {
            "admin":   ("#EEEDFE", "#3C3489"),
            "manager": ("#E6F1FB", "#185FA5"),
            "cashier": ("#E1F5EE", "#0F6E56"),
            "barista": ("#FAEEDA", "#854F0B"),
            "server":  ("#FCF0FB", "#7C3A89"),
            "kitchen": ("#F1EFE8", "#5F5E5A"),
        }

        if on_duty:
            for s in on_duty:
                r = ctk.CTkFrame(card, fg_color="white")
                r.pack(fill="x", padx=16, pady=3)

                initials = "".join(
                    n[0].upper() for n in s['full_name'].split()[:2])
                av = ctk.CTkFrame(r, fg_color=PRIMARY_COLOR,
                                   width=30, height=30, corner_radius=15)
                av.pack(side="left")
                av.pack_propagate(False)
                ctk.CTkLabel(av, text=initials,
                             font=("Segoe UI", 10, "bold"),
                             text_color="white").place(
                                 relx=.5, rely=.5, anchor="center")

                ctk.CTkLabel(r, text=s['full_name'],
                             font=("Segoe UI", 11, "bold"),
                             text_color=TEXT_PRIMARY).pack(
                                 side="left", padx=8)

                rb, rf = ROLE_COLORS.get(
                    s['role'], (BG_SECONDARY, TEXT_PRIMARY))
                ctk.CTkLabel(r,
                             text=ROLE_DISPLAY.get(s['role'], s['role']),
                             font=("Segoe UI", 9, "bold"),
                             fg_color=rb, text_color=rf,
                             corner_radius=4, padx=5, pady=1
                             ).pack(side="right")

            ctk.CTkLabel(card,
                         text=f"✓  {len(on_duty)} nhân viên đang trực",
                         font=FONT_SMALL,
                         text_color=SUCCESS_COLOR).pack(
                             anchor="w", padx=16, pady=(8, 14))
        else:
            ctk.CTkLabel(card,
                         text="Chưa phân ca cho buổi này",
                         font=FONT_SMALL,
                         text_color=TEXT_SECONDARY).pack(
                             padx=16, pady=(0, 14))

    # ══════════════════════════════════════════
    #  HELPER
    # ══════════════════════════════════════════
    @staticmethod
    def _eq_date(db_val, d: date) -> bool:
        """So sánh ngày từ DB (date hoặc datetime) với date bình thường."""
        if hasattr(db_val, 'date'):
            return db_val.date() == d
        return db_val == d