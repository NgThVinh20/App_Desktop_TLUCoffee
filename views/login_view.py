import customtkinter as ctk
from config.settings import *
from dao.user_dao import UserDAO

class LoginView(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=BG_PRIMARY)
        self.app = app
        self.pack(fill="both", expand=True)
        self._build()

    def _build(self):
        # Canvas cuộn để tránh bị cắt
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Frame căn giữa
        center = ctk.CTkFrame(self, fg_color=BG_PRIMARY)
        center.grid(row=0, column=0, pady=30)

        # ── Logo
        logo_frame = ctk.CTkFrame(center, fg_color=PRIMARY_COLOR,
                                   width=64, height=64, corner_radius=14)
        logo_frame.pack(pady=(0, 10))
        logo_frame.pack_propagate(False)
        ctk.CTkLabel(logo_frame, text="☕", font=("Segoe UI", 30),
                     text_color="white").place(relx=.5, rely=.5, anchor="center")

        # ── Tiêu đề
        ctk.CTkLabel(center, text=APP_NAME,
                     font=("Segoe UI", 24, "bold"),
                     text_color=PRIMARY_COLOR).pack()
        ctk.CTkLabel(center, text="MANAGEMENT PORTAL",
             font=("Segoe UI", 10),
             text_color=TEXT_SECONDARY).pack(pady=(2, 20))

        # ── Card (KHÔNG dùng width/height cố định)
        card = ctk.CTkFrame(center, fg_color="white", corner_radius=16,
                             border_width=1, border_color="#e5e7eb")
        card.pack(padx=20, fill="x", ipadx=10, ipady=10)

        inner = ctk.CTkFrame(card, fg_color="white")
        inner.pack(fill="both", expand=True, padx=32, pady=32)

        # ── Email
        ctk.CTkLabel(inner, text="Email Address",
                     font=FONT_SMALL, text_color=TEXT_SECONDARY).pack(anchor="w")
        self.email_var = ctk.StringVar(value="admin@tlucoffee.vn")
        self.email_entry = ctk.CTkEntry(
            inner, textvariable=self.email_var,
            placeholder_text="email@tlucoffee.vn",
            fg_color="#f3f4f6", border_width=0,
            font=FONT_NORMAL, text_color=TEXT_PRIMARY,
            height=46, corner_radius=8)
        self.email_entry.pack(fill="x", pady=(4, 14))

        # ── Password
        ctk.CTkLabel(inner, text="Password",
                     font=FONT_SMALL, text_color=TEXT_SECONDARY).pack(anchor="w")
        self.pass_var = ctk.StringVar(value="Admin@123")

        pass_frame = ctk.CTkFrame(inner, fg_color="#f3f4f6",
                                   corner_radius=8)
        pass_frame.pack(fill="x", pady=(4, 8))

        self.pass_entry = ctk.CTkEntry(
            pass_frame, textvariable=self.pass_var,
            show="•", fg_color="#f3f4f6", border_width=0,
            font=FONT_NORMAL, text_color=TEXT_PRIMARY,
            height=46, corner_radius=8)
        self.pass_entry.pack(side="left", fill="x", expand=True)

        self.show_pass = False
        self.eye_btn = ctk.CTkButton(
            pass_frame, text="👁", width=40, height=46,
            fg_color="transparent", hover=False,
            font=("Segoe UI", 15), text_color=TEXT_SECONDARY,
            command=self._toggle_pass)
        self.eye_btn.pack(side="right")
        # Nút show/hide password
        self.show_pass = False
        self.eye_btn = ctk.CTkButton(
            pass_frame, text="👁", width=32, height=32,
            fg_color="transparent", hover=False,
            font=("Segoe UI", 15), text_color=TEXT_SECONDARY,
            command=self._toggle_pass)
        self.eye_btn.place(relx=1, x=-8, rely=.5, anchor="e")

        # ── Remember me & Forgot password
        opt_row = ctk.CTkFrame(inner, fg_color="white")
        opt_row.pack(fill="x", pady=(4, 16))
        self.remember_var = ctk.BooleanVar()
        ctk.CTkCheckBox(opt_row, text="Remember Me",
                        variable=self.remember_var,
                        font=FONT_SMALL, text_color=TEXT_SECONDARY,
                        fg_color=PRIMARY_COLOR,
                        hover_color=PRIMARY_HOVER,
                        checkbox_width=18, checkbox_height=18).pack(side="left")
        ctk.CTkButton(opt_row, text="Forgot Password?",
                      font=FONT_SMALL, text_color=ACCENT_COLOR,
                      fg_color="transparent", hover=False,
                      command=lambda: None).pack(side="right")

        # ── Lỗi
        self.error_var = ctk.StringVar()
        ctk.CTkLabel(inner, textvariable=self.error_var,
                     font=FONT_SMALL,
                     text_color=DANGER_COLOR).pack(pady=(0, 6))

        # ── Nút Sign In
        ctk.CTkButton(inner, text="Sign In to Dashboard  →",
                      font=("Segoe UI", 13, "bold"),
                      fg_color=PRIMARY_COLOR,
                      hover_color=PRIMARY_HOVER,
                      height=48, corner_radius=8,
                      command=self._login).pack(fill="x")

        # ── Divider
        div = ctk.CTkFrame(inner, fg_color="#e5e7eb", height=1)
        div.pack(fill="x", pady=18)

        # ── Link tạo tài khoản
        link_row = ctk.CTkFrame(inner, fg_color="white")
        link_row.pack()
        ctk.CTkLabel(link_row, text="New to the platform?",
                     font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).pack(side="left")
        ctk.CTkButton(link_row, text="Create Staff Account",
                      font=("Segoe UI", 11, "bold"),
                      text_color=PRIMARY_COLOR,
                      fg_color="transparent", hover=False,
                      command=self.app.show_register).pack(side="left", padx=6)

        # Enter để login
        self.pass_entry.bind("<Return>", lambda e: self._login())

    def _toggle_pass(self):
        self.show_pass = not self.show_pass
        self.pass_entry.configure(show="" if self.show_pass else "•")

    def _login(self):
        email    = self.email_var.get().strip()
        password = self.pass_var.get()

        if not email or not password:
            self.error_var.set("Vui lòng nhập đầy đủ thông tin!")
            return

        user = UserDAO.get_by_email(email)
        if not user:
            self.error_var.set("Email không tồn tại hoặc tài khoản bị khóa!")
            return

        if not UserDAO.verify_password(password, user['password_hash']):
            self.error_var.set("Mật khẩu không đúng!")
            return

        UserDAO.update_last_login(user['id'])
        self.error_var.set("")
        self.app.show_main(user)