import customtkinter as ctk
from config.settings import *
from dao.user_dao import UserDAO
import re

class RegisterView(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=BG_PRIMARY)
        self.app = app
        self.pack(fill="both", expand=True)
        self._build()

    def _build(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        center = ctk.CTkFrame(self, fg_color=BG_PRIMARY)
        center.grid(row=0, column=0)

        # Logo
        logo_frame = ctk.CTkFrame(center, fg_color=PRIMARY_COLOR,
                                   width=60, height=60, corner_radius=12)
        logo_frame.pack(pady=(0,12))
        logo_frame.pack_propagate(False)
        ctk.CTkLabel(logo_frame, text="☕", font=("Segoe UI", 28),
                     text_color="white").place(relx=.5, rely=.5, anchor="center")

        ctk.CTkLabel(center, text=APP_NAME,
                     font=("Segoe UI", 22, "bold"),
                     text_color=PRIMARY_COLOR).pack()
        ctk.CTkLabel(center, text="HỆ THỐNG QUẢN TRỊ",
                     font=("Segoe UI", 11),
                     text_color=TEXT_SECONDARY).pack(pady=(0,20))

        # Card
        card = ctk.CTkFrame(center, fg_color="white",
                             corner_radius=16, width=420)
        card.pack(padx=20)
        card.pack_propagate(False)

        inner = ctk.CTkFrame(card, fg_color="white")
        inner.pack(fill="both", expand=True, padx=28, pady=28)

        ctk.CTkLabel(inner, text="Đăng ký nhân viên",
                     font=("Segoe UI", 17, "bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(inner, text="Tạo tài khoản để tham gia đội ngũ",
                     font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).pack(anchor="w", pady=(2,16))

        # Họ tên
        ctk.CTkLabel(inner, text="Họ và tên", font=FONT_SMALL,
                     text_color=TEXT_PRIMARY).pack(anchor="w")
        self.name_var = ctk.StringVar()
        ctk.CTkEntry(inner, textvariable=self.name_var,
                     placeholder_text="Nguyễn Văn A",
                     height=40, corner_radius=8).pack(fill="x", pady=(4,10))

        # Email
        ctk.CTkLabel(inner, text="Email nhân viên", font=FONT_SMALL,
                     text_color=TEXT_PRIMARY).pack(anchor="w")
        self.email_var = ctk.StringVar()
        ctk.CTkEntry(inner, textvariable=self.email_var,
                     placeholder_text="ten@tlucoffee.vn",
                     height=40, corner_radius=8).pack(fill="x", pady=(4,10))

        # Vai trò
        ctk.CTkLabel(inner, text="Vai trò", font=FONT_SMALL,
                     text_color=TEXT_PRIMARY).pack(anchor="w")
        self.role_var = ctk.StringVar(value="barista")
        roles = [("☕ Barista",  "barista"),
                 ("🍽️ Phục vụ", "server"),
                 ("🍳 Bếp",     "kitchen"),
                 ("📋 Quản lý", "manager")]
        role_frame = ctk.CTkFrame(inner, fg_color="white")
        role_frame.pack(fill="x", pady=(4,10))
        for i, (label, value) in enumerate(roles):
            btn = ctk.CTkButton(
                role_frame, text=label, width=85, height=36,
                corner_radius=8, font=FONT_SMALL,
                fg_color=PRIMARY_COLOR if value == "barista" else BG_SECONDARY,
                text_color="white" if value == "barista" else TEXT_PRIMARY,
                hover_color=PRIMARY_HOVER,
                command=lambda v=value: self._select_role(v)
            )
            btn.grid(row=0, column=i, padx=3)
            setattr(self, f"role_btn_{value}", btn)

        # Password
        ctk.CTkLabel(inner, text="Mật khẩu", font=FONT_SMALL,
                     text_color=TEXT_PRIMARY).pack(anchor="w")
        self.pass_var = ctk.StringVar()
        ctk.CTkEntry(inner, textvariable=self.pass_var,
                     show="•", height=40,
                     corner_radius=8).pack(fill="x", pady=(4,10))

        # Confirm password
        ctk.CTkLabel(inner, text="Xác nhận mật khẩu", font=FONT_SMALL,
                     text_color=TEXT_PRIMARY).pack(anchor="w")
        self.pass2_var = ctk.StringVar()
        ctk.CTkEntry(inner, textvariable=self.pass2_var,
                     show="•", height=40,
                     corner_radius=8).pack(fill="x", pady=(4,10))

        # Lỗi
        self.error_var = ctk.StringVar()
        ctk.CTkLabel(inner, textvariable=self.error_var,
                     font=FONT_SMALL,
                     text_color=DANGER_COLOR).pack(pady=(0,4))

        # Nút đăng ký
        ctk.CTkButton(inner, text="Đăng ký  →",
                      font=("Segoe UI", 13, "bold"),
                      fg_color=PRIMARY_COLOR,
                      hover_color=PRIMARY_HOVER,
                      height=44, corner_radius=8,
                      command=self._do_register).pack(fill="x")

        ctk.CTkFrame(inner, height=1,
                     fg_color=BG_SECONDARY).pack(fill="x", pady=14)

        row = ctk.CTkFrame(inner, fg_color="white")
        row.pack()
        ctk.CTkLabel(row, text="Đã có tài khoản?",
                     font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).pack(side="left")
        ctk.CTkButton(row, text="Đăng nhập tại đây",
                      font=("Segoe UI", 11, "bold"),
                      text_color=PRIMARY_COLOR,
                      fg_color="transparent", hover=False,
                      command=self.app.show_login).pack(side="left", padx=4)

    def _select_role(self, selected: str):
        self.role_var.set(selected)
        role_buttons = {
            "barista": self.role_btn_barista,
            "server": self.role_btn_server,
            "kitchen": self.role_btn_kitchen,
            "manager": self.role_btn_manager
        }
        for role, btn in role_buttons.items():
            if role == selected:
                btn.configure(fg_color=PRIMARY_COLOR, text_color="white")
            else:
                btn.configure(fg_color=BG_SECONDARY, text_color=TEXT_PRIMARY)
                
    def is_valid_gmail(email: str) -> bool:
        pattern = r"^[\w\.-]+@gmail\.com$"
        return bool(re.match(pattern, email.lower()))            
    def _do_register(self):
        name  = self.name_var.get().strip()
        email = self.email_var.get().strip()
        role  = self.role_var.get()
        pw    = self.pass_var.get()
        pw2   = self.pass2_var.get()

        if not all([name, email, pw, pw2]):
            self.error_var.set("Vui lòng nhập đầy đủ thông tin!")
            return
        if pw != pw2:
            self.error_var.set("Mật khẩu xác nhận không khớp!")
            return
        if len(pw) < 6:
            self.error_var.set("Mật khẩu phải có ít nhất 6 ký tự!")
            return
        if UserDAO.get_by_email(email):
            self.error_var.set("Email này đã được sử dụng!")
            return
        if not email.lower().endswith("@gmail.com"):
            self.error_var.set("Vui lòng nhập Email đúng định dạng!")
            return
        if not self.is_valid_gmail(email):
            self.error_var.set("Email Gmail không hợp lệ!")
            return
        UserDAO.create(name, email, pw, role)
        self.error_var.set("")
        self.app.show_login()