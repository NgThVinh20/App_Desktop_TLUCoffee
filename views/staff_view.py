import customtkinter as ctk
from config.settings import *
from dao.user_dao import UserDAO
import tkinter.messagebox as msgbox


class StaffView(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=BG_PRIMARY)
        self.app       = app
        self.user      = app.current_user
        self.all_staff = []
        self.pack(fill="both", expand=True)
        self._build()
        self._load_data()

    # ════════════════════════════════════════
    #  BUILD UI
    # ════════════════════════════════════════
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
        ctk.CTkLabel(left, text="Quản lý nhân viên",
                     font=("Segoe UI", 18, "bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", pady=(12, 0))
        ctk.CTkLabel(left, text="Quản lý tài khoản và thông tin nhân viên",
                     font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).pack(anchor="w")

        right = ctk.CTkFrame(h, fg_color="white")
        right.pack(side="right", fill="y", pady=14)

        self.search_var = ctk.StringVar()
        self.search_var.trace("w", lambda *a: self._filter())
        ctk.CTkEntry(right, textvariable=self.search_var,
                     placeholder_text="Tìm nhân viên...",
                     width=180, height=36,
                     corner_radius=8).pack(side="left", padx=(0, 8))

        self.role_var = ctk.StringVar(value="Tất cả")
        ctk.CTkOptionMenu(right,
                          values=["Tất cả", "Admin", "Quản lý",
                                  "Thu ngân", "Barista", "Phục vụ", "Bếp"],
                          variable=self.role_var,
                          fg_color=BG_SECONDARY,
                          button_color=BG_SECONDARY,
                          button_hover_color=PRIMARY_HOVER,
                          text_color=TEXT_PRIMARY,
                          width=120, height=36,
                          command=lambda _: self._filter()
                          ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(right, text="+ Thêm nhân viên",
                      font=("Segoe UI", 12, "bold"),
                      fg_color=PRIMARY_COLOR,
                      hover_color=PRIMARY_HOVER,
                      height=36, corner_radius=8,
                      command=self._open_form).pack(side="left")

        # ── Body
        body = ctk.CTkFrame(self, fg_color=BG_PRIMARY)
        body.pack(fill="both", expand=True, padx=20, pady=16)

        table_card = ctk.CTkFrame(body, fg_color="white",
                                   corner_radius=12,
                                   border_width=1,
                                   border_color="#e5e7eb")
        table_card.pack(fill="both", expand=True)

        # ── Header bảng — 7 cột (thêm "Tham gia")
        thead = ctk.CTkFrame(table_card, fg_color=BG_SECONDARY,
                              corner_radius=0, height=40)
        thead.pack(fill="x")
        thead.pack_propagate(False)

        cols = [
            ("Nhân viên",  0.02),
            ("Email",      0.25),
            ("Vai trò",    0.44),
            ("Điện thoại", 0.57),
            ("Tham gia",   0.69),   # ← CỘT MỚI
            ("Trạng thái", 0.79),
            ("Thao tác",   0.90),
        ]
        for label, relx in cols:
            ctk.CTkLabel(thead, text=label,
                         font=("Segoe UI", 11, "bold"),
                         text_color=TEXT_SECONDARY).place(
                             relx=relx, rely=0.5, anchor="w")

        self.table_scroll = ctk.CTkScrollableFrame(
            table_card, fg_color="white")
        self.table_scroll.pack(fill="both", expand=True)

        footer = ctk.CTkFrame(table_card, fg_color="white",
                               height=40, corner_radius=0)
        footer.pack(fill="x")
        footer.pack_propagate(False)
        self.page_label = ctk.CTkLabel(
            footer, text="",
            font=FONT_SMALL, text_color=TEXT_SECONDARY)
        self.page_label.pack(side="left", padx=16, pady=10)

    # ════════════════════════════════════════
    #  LOAD & FILTER
    # ════════════════════════════════════════
    def _load_data(self):
        self.all_staff = UserDAO.get_all()
        self._filter()

    def _filter(self):
        kw = self.search_var.get().lower()
        role_map_rev = {
            "Tất cả":   None,
            "Admin":    "admin",
            "Quản lý":  "manager",
            "Thu ngân": "cashier",
            "Barista":  "barista",
            "Phục vụ":  "server",
            "Bếp":      "kitchen",
        }
        selected_role = role_map_rev.get(self.role_var.get())
        staff = self.all_staff

        if selected_role:
            staff = [s for s in staff if s['role'] == selected_role]
        if kw:
            staff = [s for s in staff
                     if kw in s['full_name'].lower()
                     or kw in s['email'].lower()]
        self._render_table(staff)

    # ════════════════════════════════════════
    #  RENDER BẢNG
    # ════════════════════════════════════════
    def _render_table(self, staff: list):
        for w in self.table_scroll.winfo_children():
            w.destroy()

        if not staff:
            ctk.CTkLabel(self.table_scroll,
                         text="Không tìm thấy nhân viên nào",
                         font=FONT_NORMAL,
                         text_color=TEXT_SECONDARY).pack(pady=40)
            self.page_label.configure(text="0 nhân viên")
            return

        role_map = {
            "admin":   ("Admin",    "#EEEDFE", "#3C3489"),
            "manager": ("Quản lý",  "#E6F1FB", "#185FA5"),
            "cashier": ("Thu ngân", "#E1F5EE", "#0F6E56"),
            "barista": ("Barista",  "#FAEEDA", "#854F0B"),
            "server":  ("Phục vụ",  "#FCF0FB", "#7C3A89"),
            "kitchen": ("Bếp",      "#F1EFE8", "#5F5E5A"),
        }

        for i, s in enumerate(staff):
            bg  = "white" if i % 2 == 0 else "#fafafa"
            row = ctk.CTkFrame(self.table_scroll,
                               fg_color=bg, height=52,
                               corner_radius=0)
            row.pack(fill="x")
            row.pack_propagate(False)

            # ── Avatar + Tên
            initials = "".join([
                n[0].upper() for n in s['full_name'].split()[:2]
            ])
            av_frame = ctk.CTkFrame(row, fg_color="transparent")
            av_frame.place(relx=0.02, rely=0.5, anchor="w")

            av = ctk.CTkFrame(av_frame, fg_color=PRIMARY_COLOR,
                               width=34, height=34, corner_radius=17)
            av.pack(side="left")
            av.pack_propagate(False)
            ctk.CTkLabel(av, text=initials,
                         font=("Segoe UI", 11, "bold"),
                         text_color="white").place(
                             relx=.5, rely=.5, anchor="center")

            name_box = ctk.CTkFrame(av_frame, fg_color="transparent")
            name_box.pack(side="left", padx=8)
            ctk.CTkLabel(name_box, text=s['full_name'],
                         font=("Segoe UI", 12, "bold"),
                         text_color=TEXT_PRIMARY,
                         anchor="w").pack(anchor="w")
            ctk.CTkLabel(name_box, text=f"ID: {s['id']:04d}",
                         font=("Segoe UI", 10),
                         text_color=TEXT_SECONDARY,
                         anchor="w").pack(anchor="w")

            # ── Email
            ctk.CTkLabel(row, text=s['email'],
                         font=FONT_SMALL,
                         text_color=TEXT_SECONDARY,
                         anchor="w").place(relx=0.25, rely=0.5,
                                           anchor="w", relwidth=0.17)

            # ── Vai trò badge
            role_label, role_bg, role_fg = role_map.get(
                s['role'], (s['role'], BG_SECONDARY, TEXT_PRIMARY))
            ctk.CTkLabel(row, text=role_label,
                         font=("Segoe UI", 10, "bold"),
                         fg_color=role_bg, text_color=role_fg,
                         corner_radius=6,
                         padx=8, pady=3).place(
                             relx=0.44, rely=0.5, anchor="w")

            # ── Điện thoại
            ctk.CTkLabel(row,
                         text=s.get('phone') or "—",
                         font=FONT_SMALL,
                         text_color=TEXT_SECONDARY).place(
                             relx=0.57, rely=0.5, anchor="w")

            # ── Ngày tham gia  ← MỚI
            if s.get('created_at'):
                join_date = s['created_at'].strftime("%d/%m/%Y")
            else:
                join_date = "—"
            ctk.CTkLabel(row, text=join_date,
                         font=FONT_SMALL,
                         text_color=TEXT_SECONDARY).place(
                             relx=0.69, rely=0.5, anchor="w")

            # ── Trạng thái
            is_active = s.get('is_active', 1)
            ctk.CTkLabel(row,
                         text="● Hoạt động" if is_active else "● Đã khóa",
                         font=FONT_SMALL,
                         text_color=SUCCESS_COLOR if is_active
                         else DANGER_COLOR).place(
                             relx=0.79, rely=0.5, anchor="w")

            # ── Nút thao tác
            act = ctk.CTkFrame(row, fg_color="transparent")
            act.place(relx=0.90, rely=0.5, anchor="w")

            ctk.CTkButton(act, text="✏",
                          width=32, height=32,
                          corner_radius=6,
                          fg_color=BG_SECONDARY,
                          text_color=TEXT_PRIMARY,
                          hover_color="#e5e7eb",
                          font=("Segoe UI", 14),
                          command=lambda st=s: self._open_form(st)
                          ).pack(side="left", padx=2)

            ctk.CTkButton(act, text="👁",
                          width=32, height=32,
                          corner_radius=6,
                          fg_color="#E6F1FB",
                          text_color="#185FA5",
                          hover_color="#dbeafe",
                          font=("Segoe UI", 14),
                          command=lambda st=s: self._show_profile(st)
                          ).pack(side="left", padx=2)

            if s['id'] != self.user['id']:
                ctk.CTkButton(act, text="🗑",
                              width=32, height=32,
                              corner_radius=6,
                              fg_color="#FCEBEB",
                              text_color=DANGER_COLOR,
                              hover_color="#fecaca",
                              font=("Segoe UI", 14),
                              command=lambda st=s: self._delete(st)
                              ).pack(side="left", padx=2)

            ctk.CTkFrame(self.table_scroll,
                         fg_color="#f3f4f6", height=1).pack(fill="x")

        self.page_label.configure(
            text=f"Hiển thị {len(staff)} trong tổng số "
                 f"{len(self.all_staff)} nhân viên")

    # ════════════════════════════════════════
    #  DELETE
    # ════════════════════════════════════════
    def _delete(self, staff: dict):
        confirm = msgbox.askyesno(
            "Xác nhận",
            f"Bạn muốn KHÓA tài khoản này?\n"
            "(Dữ liệu lịch sử đơn hàng liên quan sẽ được giữ lại)",
            icon="warning")
        if confirm:
            UserDAO.update(
                staff['id'], staff['full_name'],
                staff['role'], staff.get('phone'), 0)
            self._load_data()
            msgbox.showinfo("Thành công",
                            f"Đã khóa tài khoản '{staff['full_name']}'!")

    # ════════════════════════════════════════
    #  FORM THÊM / SỬA
    # ════════════════════════════════════════
    def _open_form(self, staff: dict = None):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Thêm nhân viên" if not staff else "Chỉnh sửa nhân viên")
        dialog.geometry("480x520")
        dialog.resizable(False, False)
        dialog.grab_set()

        dialog.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width()  - 480) // 2
        y = self.winfo_rooty() + (self.winfo_height() - 520) // 2
        dialog.geometry(f"480x520+{x}+{y}")

        inner = ctk.CTkScrollableFrame(dialog, fg_color="white")
        inner.pack(fill="both", expand=True, padx=8, pady=8)

        ctk.CTkLabel(inner,
                     text="Thêm nhân viên" if not staff
                     else "Chỉnh sửa nhân viên",
                     font=("Segoe UI", 16, "bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", pady=(0, 16))

        # Họ tên
        ctk.CTkLabel(inner, text="Họ và tên",
                     font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).pack(anchor="w")
        name_var = ctk.StringVar(value=staff['full_name'] if staff else "")
        ctk.CTkEntry(inner, textvariable=name_var,
                     placeholder_text="Nguyễn Văn A",
                     height=38, corner_radius=8).pack(fill="x", pady=(4, 12))

        # Email
        ctk.CTkLabel(inner, text="Email",
                     font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).pack(anchor="w")
        email_var = ctk.StringVar(value=staff['email'] if staff else "")
        email_entry = ctk.CTkEntry(inner, textvariable=email_var,
                                    placeholder_text="ten@tlucoffee.vn",
                                    height=38, corner_radius=8)
        email_entry.pack(fill="x", pady=(4, 12))
        if staff:
            email_entry.configure(state="disabled", fg_color=BG_SECONDARY)

        # Điện thoại
        ctk.CTkLabel(inner, text="Số điện thoại",
                     font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).pack(anchor="w")
        phone_var = ctk.StringVar(value=staff.get('phone', '') if staff else "")
        ctk.CTkEntry(inner, textvariable=phone_var,
                     placeholder_text="090 xxx xxxx",
                     height=38, corner_radius=8).pack(fill="x", pady=(4, 12))

        # Vai trò
        ctk.CTkLabel(inner, text="Vai trò",
                     font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).pack(anchor="w")
        roles_display = ["Admin", "Quản lý", "Thu ngân",
                         "Barista", "Phục vụ", "Bếp"]
        roles_value   = ["admin", "manager", "cashier",
                         "barista", "server", "kitchen"]
        current_role  = "Barista"
        if staff and staff['role'] in roles_value:
            current_role = roles_display[roles_value.index(staff['role'])]
        role_var = ctk.StringVar(value=current_role)
        ctk.CTkOptionMenu(inner,
                          values=roles_display,
                          variable=role_var,
                          fg_color=BG_SECONDARY,
                          button_color=PRIMARY_COLOR,
                          button_hover_color=PRIMARY_HOVER,
                          text_color=TEXT_PRIMARY,
                          height=38).pack(fill="x", pady=(4, 12))

        # Mật khẩu (chỉ khi thêm mới)
        pass_var = None
        if not staff:
            ctk.CTkLabel(inner, text="Mật khẩu",
                         font=FONT_SMALL,
                         text_color=TEXT_SECONDARY).pack(anchor="w")
            pass_var = ctk.StringVar()
            ctk.CTkEntry(inner, textvariable=pass_var,
                         show="•", height=38,
                         corner_radius=8).pack(fill="x", pady=(4, 12))

        # Trạng thái (chỉ khi sửa)
        active_var = ctk.BooleanVar(
            value=bool(staff.get('is_active', 1)) if staff else True)
        if staff:
            ctk.CTkLabel(inner, text="Trạng thái",
                         font=FONT_SMALL,
                         text_color=TEXT_SECONDARY).pack(anchor="w")
            ctk.CTkCheckBox(inner, text="Tài khoản đang hoạt động",
                            variable=active_var,
                            font=FONT_SMALL,
                            fg_color=PRIMARY_COLOR,
                            hover_color=PRIMARY_HOVER).pack(
                                anchor="w", pady=(4, 12))

        error_var = ctk.StringVar()
        ctk.CTkLabel(inner, textvariable=error_var,
                     font=FONT_SMALL,
                     text_color=DANGER_COLOR).pack(pady=(0, 6))

        btn_row = ctk.CTkFrame(inner, fg_color="white")
        btn_row.pack(fill="x")

        def _save():
            name  = name_var.get().strip()
            email = email_var.get().strip()
            phone = phone_var.get().strip() or None
            role  = roles_value[roles_display.index(role_var.get())]

            if not name:
                error_var.set("Vui lòng nhập họ tên!")
                return

            if staff:
                UserDAO.update(staff['id'], name, role,
                               phone, int(active_var.get()))
            else:
                pw = pass_var.get()
                if not email:
                    error_var.set("Vui lòng nhập email!")
                    return
                if len(pw) < 6:
                    error_var.set("Mật khẩu ít nhất 6 ký tự!")
                    return
                if UserDAO.get_by_email(email):
                    error_var.set("Email đã được sử dụng!")
                    return
                UserDAO.create(name, email, pw, role, phone)

            dialog.destroy()
            self._load_data()

        ctk.CTkButton(btn_row, text="Hủy",
                      font=FONT_NORMAL,
                      fg_color=BG_SECONDARY,
                      text_color=TEXT_PRIMARY,
                      hover_color="#e5e7eb",
                      height=40, corner_radius=8,
                      command=dialog.destroy).pack(
                          side="left", fill="x",
                          expand=True, padx=(0, 6))

        ctk.CTkButton(btn_row, text="💾  Lưu thay đổi",
                      font=("Segoe UI", 12, "bold"),
                      fg_color=PRIMARY_COLOR,
                      hover_color=PRIMARY_HOVER,
                      height=40, corner_radius=8,
                      command=_save).pack(
                          side="left", fill="x", expand=True)

    # ════════════════════════════════════════
    #  HỒ SƠ NHÂN VIÊN
    # ════════════════════════════════════════
    def _show_profile(self, staff: dict):
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Hồ sơ — {staff['full_name']}")
        dialog.geometry("480x520")
        dialog.resizable(False, False)
        dialog.grab_set()

        dialog.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width()  - 480) // 2
        y = self.winfo_rooty() + (self.winfo_height() - 520) // 2
        dialog.geometry(f"480x520+{x}+{y}")

        scroll = ctk.CTkScrollableFrame(dialog, fg_color="white")
        scroll.pack(fill="both", expand=True, padx=8, pady=8)

        role_map = {
            "admin":   ("Admin",    "#EEEDFE", "#3C3489"),
            "manager": ("Quản lý",  "#E6F1FB", "#185FA5"),
            "cashier": ("Thu ngân", "#E1F5EE", "#0F6E56"),
            "barista": ("Barista",  "#FAEEDA", "#854F0B"),
            "server":  ("Phục vụ",  "#FCF0FB", "#7C3A89"),
            "kitchen": ("Bếp",      "#F1EFE8", "#5F5E5A"),
        }

        # Avatar lớn + tên
        top = ctk.CTkFrame(scroll, fg_color=PRIMARY_COLOR, corner_radius=12)
        top.pack(fill="x", pady=(0, 16))

        initials = "".join([
            n[0].upper() for n in staff['full_name'].split()[:2]
        ])
        av = ctk.CTkFrame(top, fg_color="#2d5a4f",
                           width=70, height=70, corner_radius=35)
        av.pack(pady=(20, 8))
        av.pack_propagate(False)
        ctk.CTkLabel(av, text=initials,
                     font=("Segoe UI", 26, "bold"),
                     text_color="white").place(
                         relx=.5, rely=.5, anchor="center")

        ctk.CTkLabel(top, text=staff['full_name'],
                     font=("Segoe UI", 16, "bold"),
                     text_color="white").pack()

        role_label, _, _ = role_map.get(
            staff['role'], (staff['role'], BG_SECONDARY, TEXT_PRIMARY))
        ctk.CTkLabel(top, text=role_label,
                     font=("Segoe UI", 11),
                     fg_color="#2d5a4f",
                     text_color="#9FE1CB",
                     corner_radius=6,
                     padx=10, pady=3).pack(pady=(4, 16))

        # Thông tin chi tiết
        info_card = ctk.CTkFrame(scroll, fg_color=BG_SECONDARY,
                                  corner_radius=10)
        info_card.pack(fill="x", pady=(0, 12))

        is_active = staff.get('is_active', 1)

        # Ngày tham gia ← MỚI
        if staff.get('created_at'):
            join_str = staff['created_at'].strftime("%d/%m/%Y")
        else:
            join_str = "Chưa có thông tin"

        info_rows = [
            ("👤 Mã nhân viên", f"EMP-{staff['id']:04d}"),
            ("✉  Email",        staff['email']),
            ("📞 Điện thoại",   staff.get('phone') or "Chưa cập nhật"),
            ("📅 Ngày tham gia", join_str),          # ← MỚI
            ("🔐 Trạng thái",
             "Đang hoạt động" if is_active else "Đã bị khóa"),
            ("🕐 Đăng nhập lần cuối",
             staff['last_login'].strftime("%H:%M %d/%m/%Y")
             if staff.get('last_login') else "Chưa đăng nhập"),
        ]

        for label, value in info_rows:
            r = ctk.CTkFrame(info_card, fg_color="transparent")
            r.pack(fill="x", padx=16, pady=6)
            ctk.CTkLabel(r, text=label,
                         font=FONT_SMALL,
                         text_color=TEXT_SECONDARY,
                         width=140, anchor="w").pack(side="left")
            ctk.CTkLabel(r, text=value,
                         font=("Segoe UI", 12, "bold"),
                         text_color=TEXT_PRIMARY).pack(side="left")

        # Nút đặt lại mật khẩu
        ctk.CTkButton(scroll, text="🔑  Đặt lại mật khẩu",
                      font=FONT_NORMAL,
                      fg_color=WARNING_COLOR,
                      text_color="white",
                      hover_color="#d97706",
                      height=38, corner_radius=8,
                      command=lambda: self._reset_password(
                          staff, dialog)).pack(fill="x", pady=(0, 8))

        # Nút khóa / mở tài khoản
        if staff['id'] != self.user['id']:
            ctk.CTkButton(scroll,
                          text="🔓 Mở tài khoản" if not is_active
                          else "🔒 Khóa tài khoản",
                          font=FONT_NORMAL,
                          fg_color=SUCCESS_COLOR if not is_active
                          else DANGER_COLOR,
                          text_color="white",
                          hover_color="#059669" if not is_active
                          else "#dc2626",
                          height=38, corner_radius=8,
                          command=lambda: self._toggle_active(
                              staff, dialog)).pack(fill="x", pady=(0, 8))

        ctk.CTkButton(scroll, text="Đóng",
                      font=FONT_NORMAL,
                      fg_color=BG_SECONDARY,
                      text_color=TEXT_PRIMARY,
                      hover_color="#e5e7eb",
                      height=40, corner_radius=8,
                      command=dialog.destroy).pack(fill="x")

    # ════════════════════════════════════════
    #  CHỨC NĂNG PHỤ
    # ════════════════════════════════════════
    def _reset_password(self, staff: dict, parent_dialog):
        dialog = ctk.CTkToplevel(parent_dialog)
        dialog.title("Đặt lại mật khẩu")
        dialog.geometry("380x240")
        dialog.resizable(False, False)
        dialog.grab_set()

        inner = ctk.CTkFrame(dialog, fg_color="white")
        inner.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(inner,
                     text=f"Đặt lại mật khẩu cho\n{staff['full_name']}",
                     font=("Segoe UI", 13, "bold"),
                     text_color=TEXT_PRIMARY,
                     justify="center").pack(pady=(0, 16))

        ctk.CTkLabel(inner, text="Mật khẩu mới",
                     font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).pack(anchor="w")
        pw_var = ctk.StringVar()
        ctk.CTkEntry(inner, textvariable=pw_var,
                     show="•", height=38,
                     corner_radius=8).pack(fill="x", pady=(4, 12))

        error_var = ctk.StringVar()
        ctk.CTkLabel(inner, textvariable=error_var,
                     font=FONT_SMALL,
                     text_color=DANGER_COLOR).pack()

        def _confirm():
            pw = pw_var.get()
            if len(pw) < 6:
                error_var.set("Mật khẩu ít nhất 6 ký tự!")
                return
            import bcrypt
            hashed = bcrypt.hashpw(
                pw.encode(), bcrypt.gensalt()).decode()
            from config.database import Database
            Database.execute_query(
                "UPDATE users SET password_hash=%s WHERE id=%s",
                (hashed, staff['id']))
            dialog.destroy()
            msgbox.showinfo("Thành công", "Đã đặt lại mật khẩu!")

        ctk.CTkButton(inner, text="✓ Xác nhận",
                      font=("Segoe UI", 12, "bold"),
                      fg_color=PRIMARY_COLOR,
                      hover_color=PRIMARY_HOVER,
                      height=40, corner_radius=8,
                      command=_confirm).pack(fill="x", pady=(8, 0))

    def _toggle_active(self, staff: dict, dialog):
        is_active  = staff.get('is_active', 1)
        new_status = 0 if is_active else 1
        action     = "khóa" if is_active else "mở"

        confirm = msgbox.askyesno(
            "Xác nhận",
            f"Bạn có chắc muốn {action} tài khoản\n"
            f"'{staff['full_name']}'?")
        if confirm:
            UserDAO.update(
                staff['id'], staff['full_name'],
                staff['role'], staff.get('phone'), new_status)
            dialog.destroy()
            self._load_data()