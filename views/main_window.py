import customtkinter as ctk
from config.settings import *
from datetime import datetime

class MainWindow(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=BG_PRIMARY)
        self.app  = app
        self.user = app.current_user
        self.pack(fill="both", expand=True)
        self.current_view = None
        self._build()
        # Mặc định mở Dashboard
        self.show_view("dashboard")

    def _build(self):
        # ── Chia layout: Sidebar trái + Content phải
        self.sidebar = ctk.CTkFrame(self, fg_color=PRIMARY_COLOR,
                                     width=220, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.content = ctk.CTkFrame(self, fg_color=BG_PRIMARY,
                                     corner_radius=0)
        self.content.pack(side="left", fill="both", expand=True)

        self._build_sidebar()

    def _build_sidebar(self):
        # ── Logo khu vực
        logo_area = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_area.pack(fill="x", padx=16, pady=(20, 8))

        logo_box = ctk.CTkFrame(logo_area, fg_color="white",
                                 width=36, height=36, corner_radius=8)
        logo_box.pack(side="left")
        logo_box.pack_propagate(False)
        ctk.CTkLabel(logo_box, text="☕", font=("Segoe UI", 18),
                     text_color=PRIMARY_COLOR).place(relx=.5, rely=.5,
                                                      anchor="center")

        title_box = ctk.CTkFrame(logo_area, fg_color="transparent")
        title_box.pack(side="left", padx=10)
        ctk.CTkLabel(title_box, text="TLU Coffee",
                     font=("Segoe UI", 13, "bold"),
                     text_color="white").pack(anchor="w")
        ctk.CTkLabel(title_box, text="Management Portal",
                     font=("Segoe UI", 9),
                     text_color="#9FE1CB").pack(anchor="w")

        # ── Divider
        ctk.CTkFrame(self.sidebar, fg_color="#2d5a4f",
                     height=1).pack(fill="x", padx=16, pady=10)

        # ── Menu items
        self.nav_buttons = {}
        menu_items = [
            ("dashboard",  "⊞",  "Dashboard"),
            ("pos",        "⊟",  "Bán hàng"),
            ("menu",       "☰",  "Menu"),
            ("orders",     "⊡",  "Orders"),
            ("staff",      "⊛",  "Staff"),
            ("inventory",  "⊠",  "Kho hàng"),
            ("settings",   "⚙",  "Settings"),
        ]

        nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_frame.pack(fill="x", padx=10)

        for key, icon, label in menu_items:
            btn = ctk.CTkButton(
                nav_frame,
                text=f"  {icon}   {label}",
                font=("Segoe UI", 13),
                anchor="w",
                height=42,
                corner_radius=8,
                fg_color="transparent",
                text_color="white",
                hover_color="#2d5a4f",
                command=lambda k=key: self.show_view(k)
            )
            btn.pack(fill="x", pady=2)
            self.nav_buttons[key] = btn

        # ── Spacer
        ctk.CTkFrame(self.sidebar, fg_color="transparent").pack(
            fill="both", expand=True)

        # ── User info + Logout ở dưới cùng
        ctk.CTkFrame(self.sidebar, fg_color="#2d5a4f",
                     height=1).pack(fill="x", padx=16, pady=8)

        user_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        user_frame.pack(fill="x", padx=12, pady=(0, 8))

        # Avatar chữ cái
        initials = "".join([n[0].upper()
                             for n in self.user['full_name'].split()[:2]])
        avatar = ctk.CTkFrame(user_frame, fg_color="#2d5a4f",
                               width=36, height=36, corner_radius=18)
        avatar.pack(side="left")
        avatar.pack_propagate(False)
        ctk.CTkLabel(avatar, text=initials,
                     font=("Segoe UI", 12, "bold"),
                     text_color="white").place(relx=.5, rely=.5,
                                                anchor="center")

        info = ctk.CTkFrame(user_frame, fg_color="transparent")
        info.pack(side="left", padx=8, fill="x", expand=True)
        name = self.user['full_name']
        # Rút gọn tên nếu quá dài
        display_name = name if len(name) <= 14 else name[:14] + "..."
        ctk.CTkLabel(info, text=display_name,
                     font=("Segoe UI", 11, "bold"),
                     text_color="white").pack(anchor="w")
        role_map = {"admin":"Admin","manager":"Quản lý",
                    "cashier":"Thu ngân","barista":"Barista",
                    "server":"Phục vụ","kitchen":"Bếp"}
        ctk.CTkLabel(info,
                     text=role_map.get(self.user['role'], self.user['role']),
                     font=("Segoe UI", 10),
                     text_color="#9FE1CB").pack(anchor="w")

        # Logout
        ctk.CTkButton(self.sidebar, text="⎋  Đăng xuất",
                      font=("Segoe UI", 11),
                      fg_color="transparent",
                      text_color="#9FE1CB",
                      hover_color="#2d5a4f",
                      anchor="w",
                      height=32,
                      command=self.app.logout).pack(
                          fill="x", padx=10, pady=(0, 12))

    def _set_active_nav(self, key: str):
        """Highlight nút nav đang active."""
        for k, btn in self.nav_buttons.items():
            if k == key:
                btn.configure(fg_color="#2d5a4f", text_color="white",
                              font=("Segoe UI", 13, "bold"))
            else:
                btn.configure(fg_color="transparent", text_color="white",
                              font=("Segoe UI", 13))

    def clear_content(self):
        """Xóa nội dung content area."""
        for widget in self.content.winfo_children():
            widget.destroy()

    def show_view(self, key: str):
        """Chuyển màn hình trong content area."""
        self.clear_content()
        self._set_active_nav(key)
        self.current_view = key

        if key == "dashboard":
            from views.dashboard_view import DashboardView
            DashboardView(self.content, self.app)

        elif key == "pos":
            from views.pos_view import POSView
            POSView(self.content, self.app)

        elif key == "menu":
            from views.menu_view import MenuView
            MenuView(self.content, self.app)

        elif key == "orders":
            self._placeholder("⊡", "Lịch sử đơn hàng", "Sắp ra mắt...")

        elif key == "staff":
            self._placeholder("⊛", "Quản lý nhân viên", "Sắp ra mắt...")

        elif key == "inventory":
            self._placeholder("⊠", "Kho nguyên liệu", "Sắp ra mắt...")

        elif key == "settings":
            self._placeholder("⚙", "Cài đặt hệ thống", "Sắp ra mắt...")

    def _placeholder(self, icon, title, subtitle):
        """Màn hình placeholder cho các view chưa làm."""
        frame = ctk.CTkFrame(self.content, fg_color=BG_PRIMARY)
        frame.pack(fill="both", expand=True)
        ctk.CTkLabel(frame, text=icon,
                     font=("Segoe UI", 48),
                     text_color=TEXT_SECONDARY).pack(expand=True, pady=(120, 8))
        ctk.CTkLabel(frame, text=title,
                     font=("Segoe UI", 20, "bold"),
                     text_color=TEXT_PRIMARY).pack()
        ctk.CTkLabel(frame, text=subtitle,
                     font=FONT_NORMAL,
                     text_color=TEXT_SECONDARY).pack(pady=4)