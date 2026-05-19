import customtkinter as ctk
from config.settings import *
from dao.menu_dao import MenuDAO
import tkinter.messagebox as msgbox

class MenuView(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=BG_PRIMARY)
        self.app  = app
        self.user = app.current_user
        self.all_items = []
        self.selected_category = None
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
        ctk.CTkLabel(left, text="Quản lý thực đơn",
                     font=("Segoe UI", 18, "bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", pady=(12,0))
        ctk.CTkLabel(left,
                     text="Cập nhật và điều chỉnh các món trong cửa hàng",
                     font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).pack(anchor="w")

        right = ctk.CTkFrame(h, fg_color="white")
        right.pack(side="right", fill="y", pady=14)

        # Tìm kiếm
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", lambda *a: self._filter())
        ctk.CTkEntry(right, textvariable=self.search_var,
                     placeholder_text="Tìm kiếm món...",
                     width=200, height=36,
                     corner_radius=8).pack(side="left", padx=(0,10))

        # Nút thêm món
        ctk.CTkButton(right, text="+ Thêm món mới",
                      font=("Segoe UI", 12, "bold"),
                      fg_color=PRIMARY_COLOR,
                      hover_color=PRIMARY_HOVER,
                      height=36, corner_radius=8,
                      command=self._open_form).pack(side="left")

        # ── Body
        body = ctk.CTkFrame(self, fg_color=BG_PRIMARY)
        body.pack(fill="both", expand=True, padx=20, pady=16)

        # ── Filter danh mục + thống kê
        top_row = ctk.CTkFrame(body, fg_color="transparent")
        top_row.pack(fill="x", pady=(0,8))

        # Filter frame
        filter_card = ctk.CTkFrame(top_row, fg_color="white",
                                    corner_radius=10,
                                    border_width=1,
                                    border_color="#e5e7eb")
        filter_card.pack(side="left", fill="y", padx=(0,10))

        ctk.CTkLabel(filter_card, text="Lọc theo danh mục",
                     font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).pack(
                         anchor="w", padx=12, pady=(4,2))

        self.cat_btn_frame = ctk.CTkFrame(filter_card,
                                           fg_color="transparent")
        self.cat_btn_frame.pack(padx=8, pady=(0,2))

        # Thống kê
        self.stat_card = ctk.CTkFrame(top_row,
                                       fg_color=PRIMARY_COLOR,
                                       corner_radius=10, width=140)
        self.stat_card.pack(side="right", fill="y")
        self.stat_card.pack_propagate(False)

        ctk.CTkLabel(self.stat_card, text="TỔNG SỐ MÓN",
                     font=("Segoe UI", 9),
                     text_color="#9FE1CB").pack(pady=(14,0))
        self.total_label = ctk.CTkLabel(
            self.stat_card, text="0",
            font=("Segoe UI", 36, "bold"),
            text_color="white")
        self.total_label.pack()
        ctk.CTkLabel(self.stat_card, text="món trong thực đơn",
                     font=("Segoe UI", 9),
                     text_color="#9FE1CB").pack(pady=(0,14))

        # ── Bảng danh sách
        table_card = ctk.CTkFrame(body, fg_color="white",
                                   corner_radius=12,
                                   border_width=1,
                                   border_color="#e5e7eb")
        table_card.pack(fill="both", expand=True)

        # Header bảng
        thead = ctk.CTkFrame(table_card,
                              fg_color=BG_SECONDARY,
                              corner_radius=0, height=40)
        thead.pack(fill="x")
        thead.pack_propagate(False)

        cols = [
            ("Tên món",     0.35),
            ("Danh mục",    0.15),
            ("Giá bán",     0.12),
            ("Trạng thái",  0.15),
            ("Nổi bật",     0.10),
            ("Hành động",   0.13),
        ]
        for label, rel in cols:
            ctk.CTkLabel(thead, text=label,
                         font=("Segoe UI", 11, "bold"),
                         text_color=TEXT_SECONDARY).place(
                             relx=sum(c[1] for c in cols[:cols.index((label,rel))]),
                             rely=0.5, anchor="w",
                             relwidth=rel)

        # Scrollable rows
        self.table_scroll = ctk.CTkScrollableFrame(
            table_card, fg_color="white")
        self.table_scroll.pack(fill="both", expand=True)

        # Footer phân trang
        self.footer = ctk.CTkFrame(table_card, fg_color="white",
                                    height=40, corner_radius=0)
        self.footer.pack(fill="x")
        self.footer.pack_propagate(False)
        self.page_label = ctk.CTkLabel(
            self.footer, text="",
            font=FONT_SMALL, text_color=TEXT_SECONDARY)
        self.page_label.pack(side="left", padx=16, pady=10)

    # ════════════════════════════════════════
    #  LOAD DATA
    # ════════════════════════════════════════
    def _load_data(self):
        self.all_items = MenuDAO.get_all()
        cats = MenuDAO.get_categories()

        # Xóa nút cũ
        for w in self.cat_btn_frame.winfo_children():
            w.destroy()

        # Tạo nút danh mục
        all_cats = [{"id": None, "name": "Tất cả"}] + cats
        self.cat_btns = {}
        for cat in all_cats:
            is_sel = cat['id'] == self.selected_category
            btn = ctk.CTkButton(
                self.cat_btn_frame,
                text=cat['name'],
                font=FONT_SMALL,
                height=30, corner_radius=15,
                fg_color=PRIMARY_COLOR if is_sel else BG_SECONDARY,
                text_color="white" if is_sel else TEXT_PRIMARY,
                hover_color=PRIMARY_HOVER,
                command=lambda c=cat: self._select_cat(c))
            btn.pack(side="left", padx=3)
            self.cat_btns[cat['id']] = btn

        self.total_label.configure(text=str(len(self.all_items)))
        self._filter()

    def _select_cat(self, cat: dict):
        self.selected_category = cat['id']
        for cid, btn in self.cat_btns.items():
            active = cid == cat['id']
            btn.configure(
                fg_color=PRIMARY_COLOR if active else BG_SECONDARY,
                text_color="white" if active else TEXT_PRIMARY)
        self._filter()

    def _filter(self):
        kw    = self.search_var.get().lower()
        items = self.all_items

        if self.selected_category:
            items = [i for i in items
                     if i['category_id'] == self.selected_category]
        if kw:
            items = [i for i in items
                     if kw in i['name'].lower()
                     or kw in (i.get('description') or '').lower()]

        self._render_table(items)

    def _render_table(self, items: list):
        for w in self.table_scroll.winfo_children():
            w.destroy()

        if not items:
            ctk.CTkLabel(self.table_scroll,
                         text="Không tìm thấy món nào",
                         font=FONT_NORMAL,
                         text_color=TEXT_SECONDARY).pack(pady=40)
            self.page_label.configure(text="0 món")
            return

        status_cfg = {
            1: ("Còn hàng", SUCCESS_COLOR),
            0: ("Hết hàng", DANGER_COLOR),
        }

        for i, item in enumerate(items):
            # Màu nền xen kẽ
            bg = "white" if i % 2 == 0 else "#fafafa"
            row = ctk.CTkFrame(self.table_scroll,
                                fg_color=bg, height=52,
                                corner_radius=0)
            row.pack(fill="x")
            row.pack_propagate(False)

            # Tên món + danh mục nhỏ
            name_frame = ctk.CTkFrame(row, fg_color="transparent")
            name_frame.place(relx=0, rely=0.5, anchor="w",
                              relwidth=0.35, x=12)
            ctk.CTkLabel(name_frame, text=item['name'],
                         font=("Segoe UI", 12, "bold"),
                         text_color=TEXT_PRIMARY,
                         anchor="w").pack(anchor="w")
            ctk.CTkLabel(name_frame,
                         text=item.get('category_name', ''),
                         font=("Segoe UI", 10),
                         text_color=TEXT_SECONDARY,
                         anchor="w").pack(anchor="w")

            # Danh mục badge
            cat_colors = {
                "Cà phê":          ("#E6F1FB", "#185FA5"),
                "Trà & Macchiato": ("#E1F5EE", "#0F6E56"),
                "Bánh ngọt":       ("#FAEEDA", "#854F0B"),
                "Khác":            ("#F1EFE8", "#5F5E5A"),
            }
            cat_name = item.get('category_name', '')
            bg_c, fg_c = cat_colors.get(cat_name, ("#F1EFE8","#5F5E5A"))
            cat_lbl = ctk.CTkLabel(row, text=cat_name,
                                    font=("Segoe UI", 10, "bold"),
                                    fg_color=bg_c, text_color=fg_c,
                                    corner_radius=6, padx=8, pady=3)
            cat_lbl.place(relx=0.35, rely=0.5, anchor="w")

            # Giá
            ctk.CTkLabel(row,
                         text=f"{int(item['base_price']):,}đ",
                         font=("Segoe UI", 12, "bold"),
                         text_color=TEXT_PRIMARY).place(
                             relx=0.50, rely=0.5, anchor="w")

            # Trạng thái
            avail = item.get('is_available', 1)
            st_text, st_color = status_cfg.get(avail, ("—", TEXT_SECONDARY))
            st_lbl = ctk.CTkLabel(row,
                                   text=f"● {st_text}",
                                   font=FONT_SMALL,
                                   text_color=st_color)
            st_lbl.place(relx=0.62, rely=0.5, anchor="w")

            # Nổi bật
            featured = "⭐ Có" if item.get('is_featured') else "—"
            ctk.CTkLabel(row, text=featured,
                         font=FONT_SMALL,
                         text_color=ACCENT_COLOR if item.get('is_featured')
                         else TEXT_SECONDARY).place(
                             relx=0.77, rely=0.5, anchor="w")

            # Hành động
            act = ctk.CTkFrame(row, fg_color="transparent")
            act.place(relx=0.87, rely=0.5, anchor="w")

            ctk.CTkButton(act, text="✏",
                          width=32, height=32,
                          corner_radius=6,
                          fg_color=BG_SECONDARY,
                          text_color=TEXT_PRIMARY,
                          hover_color="#e5e7eb",
                          font=("Segoe UI", 14),
                          command=lambda it=item: self._open_form(it)
                          ).pack(side="left", padx=2)

            ctk.CTkButton(act, text="🗑",
                          width=32, height=32,
                          corner_radius=6,
                          fg_color="#FCEBEB",
                          text_color=DANGER_COLOR,
                          hover_color="#fecaca",
                          font=("Segoe UI", 14),
                          command=lambda it=item: self._delete(it)
                          ).pack(side="left", padx=2)

            # Divider
            ctk.CTkFrame(self.table_scroll,
                         fg_color="#f3f4f6", height=1).pack(fill="x")

        self.page_label.configure(
            text=f"Hiển thị {len(items)} trong tổng số "
                 f"{len(self.all_items)} món")

    # ════════════════════════════════════════
    #  FORM THÊM / SỬA
    # ════════════════════════════════════════
    def _open_form(self, item: dict = None):
        """Mở dialog thêm hoặc sửa món."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Thêm món mới" if not item else "Chỉnh sửa món")
        dialog.geometry("500x580")
        dialog.resizable(False, False)
        dialog.grab_set()  # Modal

        # Căn giữa
        dialog.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width()  - 500) // 2
        y = self.winfo_rooty() + (self.winfo_height() - 580) // 2
        dialog.geometry(f"500x580+{x}+{y}")

        inner = ctk.CTkFrame(dialog, fg_color="white")
        inner.pack(fill="both", expand=True, padx=24, pady=24)

        title = "Thêm món mới" if not item else "Chỉnh sửa món"
        ctk.CTkLabel(inner, text=title,
                     font=("Segoe UI", 16, "bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", pady=(0,16))

        # Tên món
        ctk.CTkLabel(inner, text="Tên món",
                     font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).pack(anchor="w")
        name_var = ctk.StringVar(value=item['name'] if item else "")
        ctk.CTkEntry(inner, textvariable=name_var,
                     height=38, corner_radius=8).pack(
                         fill="x", pady=(4,12))

        # Danh mục + Giá
        row2 = ctk.CTkFrame(inner, fg_color="white")
        row2.pack(fill="x", pady=(0,12))
        row2.grid_columnconfigure((0,1), weight=1)

        cats = MenuDAO.get_categories()
        cat_names = [c['name'] for c in cats]
        cat_ids   = [c['id']   for c in cats]

        current_cat = ""
        if item:
            for c in cats:
                if c['id'] == item['category_id']:
                    current_cat = c['name']
                    break

        ctk.CTkLabel(row2, text="Danh mục",
                     font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).grid(
                         row=0, column=0, sticky="w")
        cat_var = ctk.StringVar(value=current_cat or cat_names[0])
        ctk.CTkOptionMenu(row2, values=cat_names,
                          variable=cat_var,
                          fg_color=BG_SECONDARY,
                          button_color=BG_PRIMARY,
                          button_hover_color=TEXT_SECONDARY,
                          text_color=TEXT_PRIMARY,
                          height=38).grid(
                              row=1, column=0, sticky="ew", padx=(0,8))

        ctk.CTkLabel(row2, text="Giá bán (VNĐ)",
                     font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).grid(
                         row=0, column=1, sticky="w")
        price_var = ctk.StringVar(
            value=str(int(item['base_price'])) if item else "")
        ctk.CTkEntry(row2, textvariable=price_var,
                     placeholder_text="35000",
                     height=38, corner_radius=8).grid(
                         row=1, column=1, sticky="ew")

        # Mô tả
        ctk.CTkLabel(inner, text="Mô tả",
                     font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).pack(anchor="w")
        desc_box = ctk.CTkTextbox(inner, height=80, corner_radius=8)
        desc_box.pack(fill="x", pady=(4,12))
        if item and item.get('description'):
            desc_box.insert("1.0", item['description'])

        # Tùy chọn nâng cao
        ctk.CTkLabel(inner, text="Tùy chọn nâng cao",
                     font=("Segoe UI", 11, "bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", pady=(0,8))

        opt_row = ctk.CTkFrame(inner, fg_color="white")
        opt_row.pack(fill="x", pady=(0,16))

        avail_var   = ctk.BooleanVar(value=bool(item['is_available'])
                                     if item else True)
        featured_var = ctk.BooleanVar(value=bool(item['is_featured'])
                                      if item else False)

        ctk.CTkCheckBox(opt_row, text="Đang kinh doanh",
                        variable=avail_var,
                        font=FONT_SMALL,
                        fg_color=PRIMARY_COLOR,
                        hover_color=PRIMARY_HOVER).pack(side="left", padx=(0,20))
        ctk.CTkCheckBox(opt_row, text="Món nổi bật ⭐",
                        variable=featured_var,
                        font=FONT_SMALL,
                        fg_color=PRIMARY_COLOR,
                        hover_color=PRIMARY_HOVER).pack(side="left")

        # Lỗi
        error_var = ctk.StringVar()
        ctk.CTkLabel(inner, textvariable=error_var,
                     font=FONT_SMALL,
                     text_color=DANGER_COLOR).pack(pady=(0,6))

        # Nút
        btn_row = ctk.CTkFrame(inner, fg_color="white")
        btn_row.pack(fill="x")

        def _save():
            name  = name_var.get().strip()
            price = price_var.get().strip()
            desc  = desc_box.get("1.0", "end").strip()
            cat_name = cat_var.get()
            cat_id   = cat_ids[cat_names.index(cat_name)]

            if not name:
                error_var.set("Vui lòng nhập tên món!")
                return
            try:
                price_val = float(price)
            except ValueError:
                error_var.set("Giá không hợp lệ!")
                return

            if item:
                MenuDAO.update(
                    item['id'], cat_id, name, desc,
                    price_val,
                    int(avail_var.get()),
                    int(featured_var.get()))
            else:
                MenuDAO.create(cat_id, name, desc, price_val)

            dialog.destroy()
            self._load_data()

        ctk.CTkButton(btn_row, text="Hủy",
                      font=FONT_NORMAL,
                      fg_color=BG_SECONDARY,
                      text_color=TEXT_PRIMARY,
                      hover_color="#e5e7eb",
                      height=40, corner_radius=8,
                      command=dialog.destroy).pack(
                          side="left", fill="x", expand=True, padx=(0,6))

        ctk.CTkButton(btn_row, text="💾  Lưu thay đổi",
                      font=("Segoe UI", 12, "bold"),
                      fg_color=PRIMARY_COLOR,
                      hover_color=PRIMARY_HOVER,
                      height=40, corner_radius=8,
                      command=_save).pack(
                          side="left", fill="x", expand=True)

    # ════════════════════════════════════════
    #  XÓA MÓN
    # ════════════════════════════════════════
    def _delete(self, item: dict):
        confirm = msgbox.askyesno(
            "Xác nhận xóa",
            f"Bạn có chắc muốn xóa món\n'{item['name']}'?\n\n"
            "Hành động này không thể hoàn tác!",
            icon="warning")
        if confirm:
            try:
                MenuDAO.delete(item['id'])
                self._load_data()
            except Exception as e:
                msgbox.showerror("Lỗi",
                    f"Không thể xóa món này!\n"
                    f"(Có thể món đã được đặt trong đơn hàng)\n\n{e}")