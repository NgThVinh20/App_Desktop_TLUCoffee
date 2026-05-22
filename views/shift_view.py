import customtkinter as ctk
from config.settings import *
from dao.shift_dao import ShiftDAO
from datetime import date, timedelta
import tkinter.messagebox as msgbox

# ══════════════════════════════════════════════════════
#  HẰNG SỐ
# ══════════════════════════════════════════════════════
SHIFT_TYPES = {
    "morning":   ("Ca sáng",  "06:00", "13:30", "#E1F5EE", "#0F6E56"),
    "afternoon": ("Ca chiều", "13:30", "17:00", "#FAEEDA", "#854F0B"),
    "evening":   ("Ca tối",   "17:00", "22:00", "#EEEDFE", "#3C3489"),
}
DAY_NAMES = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5",
             "Thứ 6", "Thứ 7", "Chủ nhật"]
ROLE_MAP = {
    "admin":   "Admin",    "manager": "Quản lý",
    "cashier": "Thu ngân", "barista": "Barista",
    "server":  "Phục vụ",  "kitchen": "Bếp",
}


def get_week_start(d: date) -> date:
    """Trả về thứ 2 của tuần chứa ngày d."""
    return d - timedelta(days=d.weekday())


# ══════════════════════════════════════════════════════
#  MAIN VIEW
# ══════════════════════════════════════════════════════
class ShiftView(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=BG_PRIMARY)
        self.app        = app
        self.user       = app.current_user
        self.week_start = get_week_start(date.today())
        self.shifts     = []
        self.pack(fill="both", expand=True)

        # Kiểm tra quyền — chỉ admin và manager mới được xem
        if self.user['role'] not in ('admin', 'manager'):
            self._build_no_permission()
            return

        self._build()
        self._load()

    # ─────────────────────────────────
    #  BUILD UI
    # ─────────────────────────────────
    def _build(self):
        # ── Header
        header = ctk.CTkFrame(self, fg_color="white",
                               height=64, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)

        h = ctk.CTkFrame(header, fg_color="white")
        h.pack(fill="both", expand=True, padx=24)

        # Tiêu đề trái
        left = ctk.CTkFrame(h, fg_color="white")
        left.pack(side="left", fill="y")
        ctk.CTkLabel(left, text="Lịch phân ca",
                     font=("Segoe UI", 18, "bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", pady=(12, 0))
        ctk.CTkLabel(left, text="Quản lý ca làm việc theo tuần",
                     font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).pack(anchor="w")

        # Điều hướng tuần + nút thêm ca (bên phải)
        right = ctk.CTkFrame(h, fg_color="white")
        right.pack(side="right", fill="y", pady=14)

        ctk.CTkButton(right, text="◀",
                      width=34, height=36, corner_radius=8,
                      fg_color=BG_SECONDARY, text_color=TEXT_PRIMARY,
                      hover_color="#e5e7eb", font=("Segoe UI", 14),
                      command=self._prev_week
                      ).pack(side="left", padx=(0, 4))

        self.week_label = ctk.CTkLabel(
            right, text="", width=200,
            font=("Segoe UI", 12, "bold"),
            text_color=TEXT_PRIMARY)
        self.week_label.pack(side="left", padx=4)

        ctk.CTkButton(right, text="▶",
                      width=34, height=36, corner_radius=8,
                      fg_color=BG_SECONDARY, text_color=TEXT_PRIMARY,
                      hover_color="#e5e7eb", font=("Segoe UI", 14),
                      command=self._next_week
                      ).pack(side="left", padx=(4, 8))

        ctk.CTkButton(right, text="Tuần này",
                      height=36, corner_radius=8,
                      fg_color=BG_SECONDARY, text_color=TEXT_PRIMARY,
                      hover_color="#e5e7eb", font=FONT_SMALL,
                      command=self._this_week
                      ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(right, text="+ Thêm ca",
                      font=("Segoe UI", 12, "bold"),
                      fg_color=PRIMARY_COLOR, hover_color=PRIMARY_HOVER,
                      height=36, corner_radius=8,
                      command=lambda: self._open_form()
                      ).pack(side="left")

        # ── Vùng cuộn chứa toàn bộ nội dung
        self.scroll = ctk.CTkScrollableFrame(self, fg_color=BG_PRIMARY)
        self.scroll.pack(fill="both", expand=True, padx=16, pady=12)

    # ─────────────────────────────────
    #  LOAD & RENDER
    # ─────────────────────────────────
    def _load(self):
        # Cập nhật nhãn tuần
        week_end = self.week_start + timedelta(days=6)
        self.week_label.configure(
            text=f"{self.week_start.strftime('%d/%m')} "
                 f"— {week_end.strftime('%d/%m/%Y')}")

        # Lấy dữ liệu từ DB
        try:
            self.shifts = ShiftDAO.get_by_week(self.week_start)
        except Exception as e:
            self.shifts = []
            print(f"Lỗi load ca: {e}")

        # Xóa nội dung cũ rồi vẽ lại
        for w in self.scroll.winfo_children():
            w.destroy()

        self._build_stats()
        self._build_table()
        self._build_summary()

    # ─────────────────────────────────
    #  THỐNG KÊ NHANH (4 card trên cùng)
    # ─────────────────────────────────
    def _build_stats(self):
        row = ctk.CTkFrame(self.scroll, fg_color="transparent")
        row.pack(fill="x", pady=(0, 12))
        row.grid_columnconfigure((0, 1, 2, 3), weight=1)

        staff_ids    = {s['user_id'] for s in self.shifts}
        total_staff  = len(staff_ids)
        total_shifts = len(self.shifts)
        total_hours  = total_shifts * 8

        # Đếm ngày có ít nhất 2 ca
        days_ok = 0
        for i in range(7):
            d = self.week_start + timedelta(days=i)
            if sum(1 for s in self.shifts if self._eq(s['shift_date'], d)) >= 2:
                days_ok += 1

        cards = [
            ("👥", "Nhân viên có ca",  str(total_staff),  "người"),
            ("📋", "Tổng lượt ca",     str(total_shifts), "ca trong tuần"),
            ("⏱",  "Tổng giờ công",    str(total_hours),  "giờ làm việc"),
            ("📅", "Ngày đủ ca",        str(days_ok),      "/ 7 ngày"),
        ]

        for col, (icon, label, val, unit) in enumerate(cards):
            card = ctk.CTkFrame(row, fg_color="white", corner_radius=12,
                                border_width=1, border_color="#e5e7eb")
            card.grid(row=0, column=col, padx=5, sticky="nsew")

            inner = ctk.CTkFrame(card, fg_color="white")
            inner.pack(fill="both", expand=True, padx=14, pady=12)

            ctk.CTkLabel(inner, text=icon,
                         font=("Segoe UI", 20)).pack(anchor="w")
            ctk.CTkLabel(inner, text=label,
                         font=FONT_SMALL,
                         text_color=TEXT_SECONDARY).pack(anchor="w", pady=(6, 0))
            ctk.CTkLabel(inner, text=val,
                         font=("Segoe UI", 22, "bold"),
                         text_color=TEXT_PRIMARY).pack(anchor="w")
            ctk.CTkLabel(inner, text=unit,
                         font=("Segoe UI", 10),
                         text_color=TEXT_SECONDARY).pack(anchor="w")

    # ─────────────────────────────────
    #  BẢNG LỊCH 7 NGÀY × 3 CA
    # ─────────────────────────────────
    def _build_table(self):
        card = ctk.CTkFrame(self.scroll, fg_color="white",
                             corner_radius=12,
                             border_width=1, border_color="#e5e7eb")
        card.pack(fill="x", pady=(0, 12))

        # Tiêu đề
        ctk.CTkLabel(card, text="Bảng lịch theo tuần",
                     font=("Segoe UI", 13, "bold"),
                     text_color=TEXT_PRIMARY).pack(
                         anchor="w", padx=16, pady=(12, 8))

        # ── Header cột: Ca | T2 | T3 | ... | CN
        LABEL_W = 100   # độ rộng cột "Ca làm" bên trái
        thead = ctk.CTkFrame(card, fg_color=BG_SECONDARY,
                              height=44, corner_radius=0)
        thead.pack(fill="x")
        thead.pack_propagate(False)

        ctk.CTkLabel(thead, text="Ca làm",
                     font=("Segoe UI", 11, "bold"),
                     text_color=TEXT_SECONDARY,
                     width=LABEL_W).place(x=8, rely=0.5, anchor="w")

        today = date.today()
        for i in range(7):
            d       = self.week_start + timedelta(days=i)
            is_today = (d == today)
            # Chia đều 7 cột trong phần còn lại
            relx = (LABEL_W / 1000) + (i + 0.5) * ((1 - LABEL_W / 1000) / 7)
            ctk.CTkLabel(thead,
                         text=f"{DAY_NAMES[i]}\n{d.strftime('%d/%m')}",
                         font=("Segoe UI", 10, "bold") if is_today
                         else ("Segoe UI", 10),
                         text_color=PRIMARY_COLOR if is_today
                         else TEXT_SECONDARY,
                         justify="center").place(
                             relx=relx, rely=0.5, anchor="center")

        # ── 3 hàng ca
        for shift_key, (shift_label, t_start, t_end, bg_c, fg_c) in SHIFT_TYPES.items():
            # Divider
            ctk.CTkFrame(card, fg_color="#f3f4f6", height=1).pack(fill="x")

            row_outer = ctk.CTkFrame(card, fg_color="white")
            row_outer.pack(fill="x")

            # Nhãn ca (cột trái)
            label_col = ctk.CTkFrame(row_outer, fg_color="white",
                                      width=LABEL_W)
            label_col.pack(side="left", fill="y")
            label_col.pack_propagate(False)

            ctk.CTkLabel(label_col, text=shift_label,
                         font=("Segoe UI", 10, "bold"),
                         fg_color=bg_c, text_color=fg_c,
                         corner_radius=6, padx=6, pady=2
                         ).pack(padx=8, pady=(10, 2))
            ctk.CTkLabel(label_col, text=f"{t_start}–{t_end}",
                         font=("Segoe UI", 9),
                         text_color=TEXT_SECONDARY).pack()

            # 7 ô ngày
            days_frame = ctk.CTkFrame(row_outer, fg_color="white")
            days_frame.pack(side="left", fill="both", expand=True)
            days_frame.grid_columnconfigure(tuple(range(7)), weight=1)

            for i in range(7):
                d = self.week_start + timedelta(days=i)

                cell = ctk.CTkFrame(days_frame, fg_color="white")
                cell.grid(row=0, column=i, sticky="nsew",
                          padx=3, pady=6)

                # Nhân viên trong ô này
                cell_shifts = [
                    s for s in self.shifts
                    if s['shift_type'] == shift_key
                    and self._eq(s['shift_date'], d)
                ]

                if cell_shifts:
                    for s in cell_shifts:
                        self._draw_chip(cell, s, bg_c, fg_c)
                else:
                    # Ô trống → nút thêm nhanh
                    ctk.CTkButton(
                        cell, text="+ Thêm",
                        font=("Segoe UI", 9),
                        fg_color=BG_SECONDARY,
                        text_color=TEXT_SECONDARY,
                        hover_color="#e5e7eb",
                        height=26, corner_radius=6,
                        command=lambda dt=d, sk=shift_key:
                            self._open_form(dt, sk)
                    ).pack(fill="x", padx=2)

        ctk.CTkFrame(card, fg_color="transparent", height=8).pack()

    def _draw_chip(self, parent, shift: dict, bg: str, fg: str):
        """Card nhỏ 1 nhân viên trong ô lịch."""
        chip = ctk.CTkFrame(parent, fg_color=bg, corner_radius=6)
        chip.pack(fill="x", padx=2, pady=2)

        top = ctk.CTkFrame(chip, fg_color="transparent")
        top.pack(fill="x", padx=6, pady=(4, 0))

        # Tên (lấy tên cuối cho ngắn)
        short_name = shift['full_name'].split()[-1]
        ctk.CTkLabel(top, text=short_name,
                     font=("Segoe UI", 10, "bold"),
                     text_color=fg, anchor="w"
                     ).pack(side="left", fill="x", expand=True)

        # Nút xóa
        ctk.CTkButton(top, text="✕",
                      width=16, height=16,
                      fg_color="transparent",
                      text_color=fg, hover=False,
                      font=("Segoe UI", 9),
                      command=lambda s=shift: self._delete(s)
                      ).pack(side="right")

        # Ghi chú (nếu có)
        if shift.get('task_note'):
            note = shift['task_note']
            if len(note) > 20:
                note = note[:20] + "…"
            ctk.CTkLabel(chip, text=note,
                         font=("Segoe UI", 8),
                         text_color=fg, anchor="w"
                         ).pack(anchor="w", padx=6, pady=(0, 4))
        else:
            ctk.CTkFrame(chip, fg_color="transparent",
                         height=4).pack()

    # ─────────────────────────────────
    #  TỔNG HỢP CA NHÂN VIÊN (dưới cùng)
    # ─────────────────────────────────
    def _build_summary(self):
        card = ctk.CTkFrame(self.scroll, fg_color="white",
                             corner_radius=12,
                             border_width=1, border_color="#e5e7eb")
        card.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(card, text="Tổng hợp ca nhân viên trong tuần",
                     font=("Segoe UI", 13, "bold"),
                     text_color=TEXT_PRIMARY).pack(
                         anchor="w", padx=16, pady=(12, 6))

        # Header bảng
        thead = ctk.CTkFrame(card, fg_color=BG_SECONDARY,
                              height=36, corner_radius=0)
        thead.pack(fill="x")
        thead.pack_propagate(False)

        for label, relx in [("Nhân viên", 0.02), ("Vai trò", 0.32),
                             ("Số ca", 0.52), ("Tổng giờ", 0.64),
                             ("Các buổi", 0.76)]:
            ctk.CTkLabel(thead, text=label,
                         font=("Segoe UI", 10, "bold"),
                         text_color=TEXT_SECONDARY).place(
                             relx=relx, rely=0.5, anchor="w")

        # Nhóm ca theo nhân viên
        staff_map = {}
        for s in self.shifts:
            uid = s['user_id']
            if uid not in staff_map:
                staff_map[uid] = {
                    'name':   s['full_name'],
                    'role':   s['role'],
                    'shifts': []
                }
            staff_map[uid]['shifts'].append(s)

        if not staff_map:
            ctk.CTkLabel(card,
                         text="Chưa có nhân viên nào được phân ca tuần này",
                         font=FONT_NORMAL,
                         text_color=TEXT_SECONDARY).pack(pady=20)
            return

        ROLE_COLORS = {
            "admin":   ("#EEEDFE", "#3C3489"),
            "manager": ("#E6F1FB", "#185FA5"),
            "cashier": ("#E1F5EE", "#0F6E56"),
            "barista": ("#FAEEDA", "#854F0B"),
            "server":  ("#FCF0FB", "#7C3A89"),
            "kitchen": ("#F1EFE8", "#5F5E5A"),
        }

        for i, (uid, data) in enumerate(staff_map.items()):
            bg  = "white" if i % 2 == 0 else "#fafafa"
            row = ctk.CTkFrame(card, fg_color=bg,
                                height=44, corner_radius=0)
            row.pack(fill="x")
            row.pack_propagate(False)

            # Avatar + tên
            initials = "".join(
                n[0].upper() for n in data['name'].split()[:2])
            av_wrap = ctk.CTkFrame(row, fg_color="transparent")
            av_wrap.place(relx=0.02, rely=0.5, anchor="w")

            av = ctk.CTkFrame(av_wrap, fg_color=PRIMARY_COLOR,
                               width=28, height=28, corner_radius=14)
            av.pack(side="left")
            av.pack_propagate(False)
            ctk.CTkLabel(av, text=initials,
                         font=("Segoe UI", 9, "bold"),
                         text_color="white").place(
                             relx=.5, rely=.5, anchor="center")
            ctk.CTkLabel(av_wrap, text=data['name'],
                         font=("Segoe UI", 11, "bold"),
                         text_color=TEXT_PRIMARY).pack(
                             side="left", padx=6)

            # Vai trò
            rb, rf = ROLE_COLORS.get(data['role'], (BG_SECONDARY, TEXT_PRIMARY))
            ctk.CTkLabel(row,
                         text=ROLE_MAP.get(data['role'], data['role']),
                         font=("Segoe UI", 10, "bold"),
                         fg_color=rb, text_color=rf,
                         corner_radius=6, padx=6, pady=2
                         ).place(relx=0.32, rely=0.5, anchor="w")

            # Số ca + giờ
            n = len(data['shifts'])
            ctk.CTkLabel(row, text=f"{n} ca",
                         font=("Segoe UI", 12, "bold"),
                         text_color=TEXT_PRIMARY
                         ).place(relx=0.52, rely=0.5, anchor="w")
            ctk.CTkLabel(row, text=f"{n * 8}h",
                         font=FONT_SMALL,
                         text_color=TEXT_SECONDARY
                         ).place(relx=0.64, rely=0.5, anchor="w")

            # Badges các buổi
            badge_wrap = ctk.CTkFrame(row, fg_color="transparent")
            badge_wrap.place(relx=0.76, rely=0.5, anchor="w")
            done = {s['shift_type'] for s in data['shifts']}
            for sk, (sl, _, _, bc, fc) in SHIFT_TYPES.items():
                if sk in done:
                    ctk.CTkLabel(badge_wrap, text=sl,
                                 font=("Segoe UI", 9),
                                 fg_color=bc, text_color=fc,
                                 corner_radius=4, padx=5, pady=1
                                 ).pack(side="left", padx=2)

            ctk.CTkFrame(card, fg_color="#f3f4f6",
                         height=1).pack(fill="x")

        ctk.CTkFrame(card, fg_color="transparent", height=8).pack()

    # ─────────────────────────────────
    #  FORM THÊM CA
    # ─────────────────────────────────
    def _open_form(self, preset_date: date = None,
                   preset_shift: str = None):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Thêm ca làm việc")
        dialog.geometry("440x460")
        dialog.resizable(False, False)
        dialog.grab_set()

        dialog.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width()  - 440) // 2
        y = self.winfo_rooty() + (self.winfo_height() - 460) // 2
        dialog.geometry(f"440x460+{x}+{y}")

        inner = ctk.CTkScrollableFrame(dialog, fg_color="white")
        inner.pack(fill="both", expand=True, padx=8, pady=8)

        ctk.CTkLabel(inner, text="Thêm ca làm việc",
                     font=("Segoe UI", 15, "bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", pady=(0, 16))

        # ── Chọn nhân viên
        ctk.CTkLabel(inner, text="Nhân viên",
                     font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).pack(anchor="w")
        try:
            all_staff  = ShiftDAO.get_all_staff()
        except Exception:
            all_staff = []

        staff_names = [s['full_name'] for s in all_staff]
        staff_ids   = [s['id']        for s in all_staff]

        if not staff_names:
            ctk.CTkLabel(inner, text="Không có nhân viên!",
                         text_color=DANGER_COLOR).pack()
            return

        staff_var = ctk.StringVar(value=staff_names[0])
        ctk.CTkOptionMenu(inner, values=staff_names,
                          variable=staff_var,
                          fg_color=BG_SECONDARY,
                          button_color=PRIMARY_COLOR,
                          button_hover_color=PRIMARY_HOVER,
                          text_color=TEXT_PRIMARY,
                          height=38).pack(fill="x", pady=(4, 12))

        # ── Ngày làm
        ctk.CTkLabel(inner, text="Ngày làm việc (dd/mm/yyyy)",
                     font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).pack(anchor="w")
        default_d = preset_date.strftime("%d/%m/%Y") \
            if preset_date else date.today().strftime("%d/%m/%Y")
        date_var = ctk.StringVar(value=default_d)
        ctk.CTkEntry(inner, textvariable=date_var,
                     height=38, corner_radius=8
                     ).pack(fill="x", pady=(4, 12))

        # ── Chọn ca
        ctk.CTkLabel(inner, text="Ca làm việc",
                     font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).pack(anchor="w")
        shift_options = {
            "Ca sáng  (06:00 – 14:00)": "morning",
            "Ca chiều (14:00 – 22:00)": "afternoon",
            "Ca tối   (22:00 – 06:00)": "evening",
        }
        default_disp = "Ca sáng  (06:00 – 14:00)"
        if preset_shift:
            for disp, val in shift_options.items():
                if val == preset_shift:
                    default_disp = disp
                    break
        shift_var = ctk.StringVar(value=default_disp)
        ctk.CTkOptionMenu(inner, values=list(shift_options.keys()),
                          variable=shift_var,
                          fg_color=BG_SECONDARY,
                          button_color=PRIMARY_COLOR,
                          button_hover_color=PRIMARY_HOVER,
                          text_color=TEXT_PRIMARY,
                          height=38).pack(fill="x", pady=(4, 12))

        # ── Ghi chú
        ctk.CTkLabel(inner, text="Ghi chú công việc (tuỳ chọn)",
                     font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).pack(anchor="w")
        note_box = ctk.CTkTextbox(inner, height=70, corner_radius=8)
        note_box.pack(fill="x", pady=(4, 12))

        # ── Lỗi
        error_var = ctk.StringVar()
        ctk.CTkLabel(inner, textvariable=error_var,
                     font=FONT_SMALL,
                     text_color=DANGER_COLOR).pack(pady=(0, 6))

        # ── Nút Hủy / Lưu
        btn_row = ctk.CTkFrame(inner, fg_color="white")
        btn_row.pack(fill="x")

        def _save():
            # Parse ngày
            try:
                from datetime import datetime as dt
                shift_date = dt.strptime(
                    date_var.get().strip(), "%d/%m/%Y").date()
            except ValueError:
                error_var.set("Ngày không hợp lệ! Dùng dd/mm/yyyy")
                return

            # Nhân viên
            try:
                uid = staff_ids[staff_names.index(staff_var.get())]
            except ValueError:
                error_var.set("Vui lòng chọn nhân viên!")
                return

            # Loại ca
            shift_type          = shift_options[shift_var.get()]
            _, t_start, t_end, _, _ = SHIFT_TYPES[shift_type]

            # Kiểm tra trùng
            try:
                if ShiftDAO.check_conflict(uid, shift_date, shift_type):
                    error_var.set("Nhân viên đã có ca này trong ngày đó!")
                    return
            except Exception as e:
                error_var.set(f"Lỗi kiểm tra: {e}")
                return

            note = note_box.get("1.0", "end").strip() or None

            try:
                ShiftDAO.create(uid, shift_date, shift_type,
                                t_start + ":00", t_end + ":00", note)
                dialog.destroy()
                self._load()
            except Exception as e:
                error_var.set(f"Lỗi lưu: {e}")

        ctk.CTkButton(btn_row, text="Hủy",
                      font=FONT_NORMAL,
                      fg_color=BG_SECONDARY, text_color=TEXT_PRIMARY,
                      hover_color="#e5e7eb",
                      height=40, corner_radius=8,
                      command=dialog.destroy
                      ).pack(side="left", fill="x",
                             expand=True, padx=(0, 6))

        ctk.CTkButton(btn_row, text="💾  Lưu ca",
                      font=("Segoe UI", 12, "bold"),
                      fg_color=PRIMARY_COLOR, hover_color=PRIMARY_HOVER,
                      height=40, corner_radius=8,
                      command=_save
                      ).pack(side="left", fill="x", expand=True)

    # ─────────────────────────────────
    #  XÓA CA
    # ─────────────────────────────────
    def _delete(self, shift: dict):
        label = SHIFT_TYPES[shift['shift_type']][0]
        ok = msgbox.askyesno(
            "Xác nhận xóa",
            f"Xóa ca của '{shift['full_name']}'?\n"
            f"{label} — {self._fmt(shift['shift_date'])}",
            icon="warning")
        if ok:
            try:
                ShiftDAO.delete(shift['id'])
                self._load()
            except Exception as e:
                msgbox.showerror("Lỗi", str(e))

    # ─────────────────────────────────
    #  ĐIỀU HƯỚNG TUẦN
    # ─────────────────────────────────
    def _prev_week(self):
        self.week_start -= timedelta(weeks=1)
        self._load()

    def _next_week(self):
        self.week_start += timedelta(weeks=1)
        self._load()

    def _this_week(self):
        self.week_start = get_week_start(date.today())
        self._load()

    # ─────────────────────────────────
    #  HELPERS
    # ─────────────────────────────────
    @staticmethod
    def _eq(db_val, d: date) -> bool:
        """So sánh ngày từ DB (date hoặc datetime) với date."""
        if hasattr(db_val, 'date'):
            return db_val.date() == d
        return db_val == d
    @staticmethod
    def _build_no_permission(self):
        """Hiển thị thông báo không có quyền truy cập."""
        frame = ctk.CTkFrame(self, fg_color=BG_PRIMARY)
        frame.pack(fill="both", expand=True)

        ctk.CTkLabel(frame, text="🔒",
                     font=("Segoe UI", 48),
                     text_color=TEXT_SECONDARY).pack(expand=True,
                                                      pady=(120, 8))
        ctk.CTkLabel(frame, text="Không có quyền truy cập",
                     font=("Segoe UI", 20, "bold"),
                     text_color=TEXT_PRIMARY).pack()
        ctk.CTkLabel(frame,
                     text="Chỉ Admin và Quản lý mới được xem lịch phân ca",
                     font=FONT_NORMAL,
                     text_color=TEXT_SECONDARY).pack(pady=4)
    @staticmethod
    def _fmt(db_val) -> str:
        if hasattr(db_val, 'strftime'):
            return db_val.strftime("%d/%m/%Y")
        return str(db_val)