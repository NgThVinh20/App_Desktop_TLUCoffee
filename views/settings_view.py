import customtkinter as ctk
from config.settings import *
from config.database import Database
import tkinter.messagebox as msgbox
from dotenv import load_dotenv, set_key
import os

load_dotenv()


class SettingsView(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=BG_PRIMARY)
        self.app  = app
        self.user = app.current_user
        self.pack(fill="both", expand=True)
        self._build()

    #  BUILD UI
    def _build(self):
        # ── Header
        header = ctk.CTkFrame(self, fg_color="white",
                               height=64, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)

        h = ctk.CTkFrame(header, fg_color="white")
        h.pack(fill="both", expand=True, padx=24)

        left = ctk.CTkFrame(h, fg_color="white")
        left.pack(side="left", fill="y")
        ctk.CTkLabel(left, text="Cài đặt hệ thống",
                     font=("Segoe UI", 18, "bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", pady=(12, 0))
        ctk.CTkLabel(left, text="Quản lý thông tin và cấu hình ứng dụng",
                     font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).pack(anchor="w")

        # ── Body: Sidebar tab trái + Content phải
        body = ctk.CTkFrame(self, fg_color=BG_PRIMARY)
        body.pack(fill="both", expand=True, padx=20, pady=16)

        # Tab sidebar
        tab_frame = ctk.CTkFrame(body, fg_color="white",
                                  corner_radius=12,
                                  border_width=1,
                                  border_color="#e5e7eb",
                                  width=180)
        tab_frame.pack(side="left", fill="y", padx=(0, 12))
        tab_frame.pack_propagate(False)

        # Content area
        self.content = ctk.CTkFrame(body, fg_color="white",
                                     corner_radius=12,
                                     border_width=1,
                                     border_color="#e5e7eb")
        self.content.pack(side="left", fill="both", expand=True)

        # Tạo các tab
        self.tab_buttons = {}
        tabs = [
            ("store",    "🏪", "Cấu hình cửa hàng"),
            ("account",  "👤", "Tài khoản")
        ]

        ctk.CTkLabel(tab_frame, text="CÀI ĐẶT",
                     font=("Segoe UI", 10, "bold"),
                     text_color=TEXT_SECONDARY).pack(
                         anchor="w", padx=14, pady=(14, 8))

        for key, icon, label in tabs:
            btn = ctk.CTkButton(
                tab_frame,
                text=f"{icon}  {label}",
                font=FONT_SMALL,
                anchor="w",
                height=38,
                corner_radius=8,
                fg_color="transparent",
                text_color=TEXT_PRIMARY,
                hover_color=BG_SECONDARY,
                command=lambda k=key: self._switch_tab(k)
            )
            btn.pack(fill="x", padx=8, pady=2)
            self.tab_buttons[key] = btn

        # Mặc định mở tab đầu tiên
        self._switch_tab("store")

    def _switch_tab(self, key: str):
        """Chuyển tab."""
        # Highlight tab active
        for k, btn in self.tab_buttons.items():
            if k == key:
                btn.configure(fg_color=BG_SECONDARY,
                              text_color=PRIMARY_COLOR,
                              font=("Segoe UI", 12, "bold"))
            else:
                btn.configure(fg_color="transparent",
                              text_color=TEXT_PRIMARY,
                              font=FONT_SMALL)

        # Xóa content cũ
        for w in self.content.winfo_children():
            w.destroy()

        # Load tab mới
        if key == "store":
            self._tab_store()
        elif key == "account":
            self._tab_account()
        elif key == "database":
            self._tab_database()
        elif key == "about":
            self._tab_about()

   
    #  TAB: CẤU HÌNH CỬA HÀNG
  
    def _tab_store(self):
        scroll = ctk.CTkScrollableFrame(self.content, fg_color="white")
        scroll.pack(fill="both", expand=True, padx=24, pady=20)

        ctk.CTkLabel(scroll, text="Thông tin cửa hàng",
                     font=("Segoe UI", 15, "bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", pady=(0, 16))

        # Tên quán
        ctk.CTkLabel(scroll, text="Tên quán",
                     font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).pack(anchor="w")
        self.store_name_var = ctk.StringVar(value="TLU Coffee Shop")
        ctk.CTkEntry(scroll, textvariable=self.store_name_var,
                     height=38, corner_radius=8).pack(
                         fill="x", pady=(4, 12))

        # Số điện thoại
        ctk.CTkLabel(scroll, text="Số điện thoại",
                     font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).pack(anchor="w")
        self.store_phone_var = ctk.StringVar(value="024 3852 1447")
        ctk.CTkEntry(scroll, textvariable=self.store_phone_var,
                     height=38, corner_radius=8).pack(
                         fill="x", pady=(4, 12))

        # Địa chỉ
        ctk.CTkLabel(scroll, text="Địa chỉ",
                     font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).pack(anchor="w")
        self.store_addr_var = ctk.StringVar(
            value="175 Tây Sơn, Đống Đa, Hà Nội")
        ctk.CTkEntry(scroll, textvariable=self.store_addr_var,
                     height=38, corner_radius=8).pack(
                         fill="x", pady=(4, 12))

        # Giờ mở / đóng cửa
        row = ctk.CTkFrame(scroll, fg_color="white")
        row.pack(fill="x", pady=(0, 12))
        row.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(row, text="Giờ mở cửa",
                     font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).grid(
                         row=0, column=0, sticky="w")
        self.open_var = ctk.StringVar(value="07:00")
        ctk.CTkEntry(row, textvariable=self.open_var,
                     height=38, corner_radius=8).grid(
                         row=1, column=0, sticky="ew", padx=(0, 8))

        ctk.CTkLabel(row, text="Giờ đóng cửa",
                     font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).grid(
                         row=0, column=1, sticky="w")
        self.close_var = ctk.StringVar(value="22:00")
        ctk.CTkEntry(row, textvariable=self.close_var,
                     height=38, corner_radius=8).grid(
                         row=1, column=1, sticky="ew")

        # Nút lưu
        ctk.CTkButton(scroll, text="💾  Lưu thay đổi",
                      font=("Segoe UI", 12, "bold"),
                      fg_color=PRIMARY_COLOR,
                      hover_color=PRIMARY_HOVER,
                      height=42, corner_radius=8,
                      command=self._save_store).pack(
                          fill="x", pady=(8, 0))

    def _save_store(self):
        msgbox.showinfo("Thành công", "Đã lưu thông tin cửa hàng!")

    
    #  TAB: TÀI KHOẢN
   
    def _tab_account(self):
        scroll = ctk.CTkScrollableFrame(self.content, fg_color="white")
        scroll.pack(fill="both", expand=True, padx=24, pady=20)

        ctk.CTkLabel(scroll, text="Thông tin tài khoản",
                     font=("Segoe UI", 15, "bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", pady=(0, 16))

        # Avatar + tên
        top = ctk.CTkFrame(scroll, fg_color=BG_SECONDARY,
                            corner_radius=10)
        top.pack(fill="x", pady=(0, 16))

        inner_top = ctk.CTkFrame(top, fg_color="transparent")
        inner_top.pack(fill="x", padx=16, pady=14)

        initials = "".join([
            n[0].upper()
            for n in self.user['full_name'].split()[:2]
        ])
        av = ctk.CTkFrame(inner_top, fg_color=PRIMARY_COLOR,
                           width=52, height=52, corner_radius=26)
        av.pack(side="left")
        av.pack_propagate(False)
        ctk.CTkLabel(av, text=initials,
                     font=("Segoe UI", 18, "bold"),
                     text_color="white").place(
                         relx=.5, rely=.5, anchor="center")

        info = ctk.CTkFrame(inner_top, fg_color="transparent")
        info.pack(side="left", padx=12)
        ctk.CTkLabel(info, text=self.user['full_name'],
                     font=("Segoe UI", 14, "bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(info, text=self.user['email'],
                     font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).pack(anchor="w")

        role_map = {
            "admin":   "Admin",   "manager": "Quản lý",
            "cashier": "Thu ngân","barista":  "Barista",
            "server":  "Phục vụ","kitchen":  "Bếp"
        }
        ctk.CTkLabel(info,
                     text=role_map.get(self.user['role'], self.user['role']),
                     font=("Segoe UI", 11),
                     text_color=PRIMARY_COLOR).pack(anchor="w")

        # ── Đổi mật khẩu
        ctk.CTkLabel(scroll, text="Đổi mật khẩu",
                     font=("Segoe UI", 13, "bold"),
                     text_color=TEXT_PRIMARY).pack(
                         anchor="w", pady=(0, 10))

        ctk.CTkLabel(scroll, text="Mật khẩu hiện tại",
                     font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).pack(anchor="w")
        self.old_pw_var = ctk.StringVar()
        ctk.CTkEntry(scroll, textvariable=self.old_pw_var,
                     show="•", height=38,
                     corner_radius=8).pack(fill="x", pady=(4, 12))

        ctk.CTkLabel(scroll, text="Mật khẩu mới",
                     font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).pack(anchor="w")
        self.new_pw_var = ctk.StringVar()
        ctk.CTkEntry(scroll, textvariable=self.new_pw_var,
                     show="•", height=38,
                     corner_radius=8).pack(fill="x", pady=(4, 12))

        ctk.CTkLabel(scroll, text="Xác nhận mật khẩu mới",
                     font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).pack(anchor="w")
        self.new_pw2_var = ctk.StringVar()
        ctk.CTkEntry(scroll, textvariable=self.new_pw2_var,
                     show="•", height=38,
                     corner_radius=8).pack(fill="x", pady=(4, 12))

        self.pw_error_var = ctk.StringVar()
        ctk.CTkLabel(scroll, textvariable=self.pw_error_var,
                     font=FONT_SMALL,
                     text_color=DANGER_COLOR).pack()

        ctk.CTkButton(scroll, text="🔑  Đổi mật khẩu",
                      font=("Segoe UI", 12, "bold"),
                      fg_color=PRIMARY_COLOR,
                      hover_color=PRIMARY_HOVER,
                      height=42, corner_radius=8,
                      command=self._change_password).pack(
                          fill="x", pady=(8, 0))

    def _change_password(self):
        import bcrypt
        from dao.user_dao import UserDAO

        old_pw = self.old_pw_var.get()
        new_pw = self.new_pw_var.get()
        new_pw2 = self.new_pw2_var.get()

        if not all([old_pw, new_pw, new_pw2]):
            self.pw_error_var.set("Vui lòng nhập đầy đủ thông tin!")
            return
        if new_pw != new_pw2:
            self.pw_error_var.set("Mật khẩu xác nhận không khớp!")
            return
        if len(new_pw) < 6:
            self.pw_error_var.set("Mật khẩu mới ít nhất 6 ký tự!")
            return

        # Kiểm tra mật khẩu cũ
        user = UserDAO.get_by_id(self.user['id'])
        if not UserDAO.verify_password(old_pw, user['password_hash']):
            self.pw_error_var.set("Mật khẩu hiện tại không đúng!")
            return

        # Cập nhật mật khẩu mới
        hashed = bcrypt.hashpw(new_pw.encode(), bcrypt.gensalt()).decode()
        Database.execute_query(
            "UPDATE users SET password_hash=%s WHERE id=%s",
            (hashed, self.user['id']))

        self.pw_error_var.set("")
        self.old_pw_var.set("")
        self.new_pw_var.set("")
        self.new_pw2_var.set("")
        msgbox.showinfo("Thành công", "Đã đổi mật khẩu thành công!")


    