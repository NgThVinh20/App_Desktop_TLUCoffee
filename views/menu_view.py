import customtkinter as ctk
from config.settings import *
from dao.menu_dao import MenuDAO
from config.database import Database
import tkinter.messagebox as msgbox


class MenuView(ctk.CTkFrame):
    """
    Màn hình quản lý thực đơn.
    Cho phép xem, thêm, sửa, xóa món ăn và danh mục.
    """

    def __init__(self, parent, app):
        super().__init__(parent, fg_color=BG_PRIMARY)
        self.app             = app
        self.user            = app.current_user
        self.all_items       = []
        self.selected_category = None
        self.pack(fill="both", expand=True)
        self._build()
        self._load_data()

    # ══════════════════════════════════════════
    #  BUILD UI
    # ══════════════════════════════════════════
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
                     text_color=TEXT_PRIMARY).pack(anchor="w", pady=(12, 0))
        ctk.CTkLabel(left,
                     text="Cập nhật và điều chỉnh các món trong cửa hàng",
                     font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).pack(anchor="w")

        right = ctk.CTkFrame(h, fg_color="white")
        right.pack(side="right", fill="y", pady=14)

        # Thanh tìm kiếm
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", lambda *a: self._filter())
        ctk.CTkEntry(right, textvariable=self.search_var,
                     placeholder_text="Tìm kiếm món...",
                     width=200, height=36,
                     corner_radius=8).pack(side="left", padx=(0, 8))

        # Nút thêm danh mục
        ctk.CTkButton(right, text="+ Danh mục",
                      font=("Segoe UI", 12, "bold"),
                      fg_color=BG_SECONDARY,
                      text_color=TEXT_PRIMARY,
                      hover_color="#e5e7eb",
                      height=36, corner_radius=8,
                      command=self._open_category_form
                      ).pack(side="left", padx=(0, 8))

        # Nút thêm món mới
        ctk.CTkButton(right, text="+ Thêm món mới",
                      font=("Segoe UI", 12, "bold"),
                      fg_color=PRIMARY_COLOR,
                      hover_color=PRIMARY_HOVER,
                      height=36, corner_radius=8,
                      command=self._open_form
                      ).pack(side="left")

        # ── Body
        body = ctk.CTkFrame(self, fg_color=BG_PRIMARY)
        body.pack(fill="both", expand=True, padx=20, pady=16)

        # ── Filter + thống kê
        top_row = ctk.CTkFrame(body, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 8))

        # Card filter danh mục
        filter_card = ctk.CTkFrame(top_row, fg_color="white",
                                    corner_radius=10,
                                    border_width=1,
                                    border_color="#e5e7eb")
        filter_card.pack(side="left", fill="y", padx=(0, 10))

        ctk.CTkLabel(filter_card, text="Lọc theo danh mục",
                     font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).pack(
                         anchor="w", padx=12, pady=(4, 2))

        self.cat_btn_frame = ctk.CTkFrame(filter_card, fg_color="transparent")
        self.cat_btn_frame.pack(padx=8, pady=(0, 8))

        # Card thống kê tổng số món
        self.stat_card = ctk.CTkFrame(top_row, fg_color=PRIMARY_COLOR,
                                       corner_radius=10, width=140)
        self.stat_card.pack(side="right", fill="y")
        self.stat_card.pack_propagate(False)

        ctk.CTkLabel(self.stat_card, text="TỔNG SỐ MÓN",
                     font=("Segoe UI", 9),
                     text_color="#9FE1CB").pack(pady=(14, 0))
        self.total_label = ctk.CTkLabel(self.stat_card, text="0",
                                         font=("Segoe UI", 36, "bold"),
                                         text_color="white")
        self.total_label.pack()
        ctk.CTkLabel(self.stat_card, text="món trong thực đơn",
                     font=("Segoe UI", 9),
                     text_color="#9FE1CB").pack(pady=(0, 14))

        # ── Bảng danh sách món
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
            ("Tên món",    0.02),
            ("Danh mục",   0.30),
            ("Giá bán",    0.46),
            ("Trạng thái", 0.59),
            ("Nổi bật",    0.74),
            ("Hành động",  0.87),
        ]
        for label, relx in cols:
            ctk.CTkLabel(thead, text=label,
                         font=("Segoe UI", 11, "bold"),
                         text_color=TEXT_SECONDARY).place(
                             relx=relx, rely=0.5, anchor="w")

        # Vùng cuộn danh sách món
        self.table_scroll = ctk.CTkScrollableFrame(table_card,
                                                    fg_color="white")
        self.table_scroll.pack(fill="both", expand=True)

        # Footer hiển thị số lượng
        self.footer = ctk.CTkFrame(table_card, fg_color="white",
                                    height=40, corner_radius=0)
        self.footer.pack(fill="x")
        self.footer.pack_propagate(False)
        self.page_label = ctk.CTkLabel(self.footer, text="",
                                        font=FONT_SMALL,
                                        text_color=TEXT_SECONDARY)
        self.page_label.pack(side="left", padx=16, pady=10)

    # ══════════════════════════════════════════
    #  LOAD DỮ LIỆU
    # ══════════════════════════════════════════
    def _load_data(self):
        """Tải lại toàn bộ món và danh mục từ DB, vẽ lại giao diện."""
        self.all_items = MenuDAO.get_all()
        cats = MenuDAO.get_categories()

        # Xóa các nút danh mục cũ
        for w in self.cat_btn_frame.winfo_children():
            w.destroy()

        # Vẽ lại nút danh mục
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
        """Lọc món theo danh mục khi bấm nút."""
        self.selected_category = cat['id']
        for cid, btn in self.cat_btns.items():
            active = cid == cat['id']
            btn.configure(
                fg_color=PRIMARY_COLOR if active else BG_SECONDARY,
                text_color="white" if active else TEXT_PRIMARY)
        self._filter()

    def _filter(self):
        """Lọc danh sách món theo danh mục đang chọn và từ khóa tìm kiếm."""
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

    # ══════════════════════════════════════════
    #  RENDER BẢNG MÓN
    # ══════════════════════════════════════════
    def _render_table(self, items: list):
        """Vẽ lại toàn bộ bảng danh sách món."""
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
        cat_colors = {
            "Cà phê":          ("#E6F1FB", "#185FA5"),
            "Trà & Macchiato": ("#E1F5EE", "#0F6E56"),
            "Bánh ngọt":       ("#FAEEDA", "#854F0B"),
            "Khác":            ("#F1EFE8", "#5F5E5A"),
        }

        for i, item in enumerate(items):
            bg  = "white" if i % 2 == 0 else "#fafafa"
            row = ctk.CTkFrame(self.table_scroll,
                               fg_color=bg, height=48,
                               corner_radius=0)
            row.pack(fill="x")
            row.pack_propagate(False)

            # Tên món
            ctk.CTkLabel(row, text=item['name'],
                         font=("Segoe UI", 12, "bold"),
                         text_color=TEXT_PRIMARY,
                         anchor="w").place(relx=0.02, rely=0.5,
                                           anchor="w", relwidth=0.26)

            # Badge danh mục
            cat_name = item.get('category_name', '')
            bg_c, fg_c = cat_colors.get(cat_name, ("#F1EFE8", "#5F5E5A"))
            ctk.CTkLabel(row, text=cat_name,
                         font=("Segoe UI", 10, "bold"),
                         fg_color=bg_c, text_color=fg_c,
                         corner_radius=6,
                         padx=8, pady=3).place(
                             relx=0.30, rely=0.5, anchor="w")

            # Giá bán
            ctk.CTkLabel(row,
                         text=f"{int(item['base_price']):,}đ",
                         font=("Segoe UI", 12, "bold"),
                         text_color=TEXT_PRIMARY).place(
                             relx=0.46, rely=0.5, anchor="w")

            # Trạng thái
            avail = item.get('is_available', 1)
            st_text, st_color = status_cfg.get(avail, ("—", TEXT_SECONDARY))
            ctk.CTkLabel(row, text=f"● {st_text}",
                         font=FONT_SMALL,
                         text_color=st_color).place(
                             relx=0.59, rely=0.5, anchor="w")

            # Nổi bật
            featured = "⭐ Có" if item.get('is_featured') else "—"
            ctk.CTkLabel(row, text=featured,
                         font=FONT_SMALL,
                         text_color=ACCENT_COLOR if item.get('is_featured')
                         else TEXT_SECONDARY).place(
                             relx=0.74, rely=0.5, anchor="w")

            # Nút hành động
            act = ctk.CTkFrame(row, fg_color="transparent")
            act.place(relx=0.87, rely=0.5, anchor="w")

            ctk.CTkButton(act, text="✏",
                          width=32, height=32, corner_radius=6,
                          fg_color=BG_SECONDARY, text_color=TEXT_PRIMARY,
                          hover_color="#e5e7eb", font=("Segoe UI", 14),
                          command=lambda it=item: self._open_form(it)
                          ).pack(side="left", padx=2)

            ctk.CTkButton(act, text="🗑",
                          width=32, height=32, corner_radius=6,
                          fg_color="#FCEBEB", text_color=DANGER_COLOR,
                          hover_color="#fecaca", font=("Segoe UI", 14),
                          command=lambda it=item: self._delete_item(it)
                          ).pack(side="left", padx=2)

            ctk.CTkFrame(self.table_scroll,
                         fg_color="#f3f4f6", height=1).pack(fill="x")

        self.page_label.configure(
            text=f"Hiển thị {len(items)} trong tổng số "
                 f"{len(self.all_items)} món")

    # ══════════════════════════════════════════
    #  FORM THÊM / SỬA DANH MỤC
    # ══════════════════════════════════════════
    def _open_category_form(self, category: dict = None):
        """
        Mở dialog thêm hoặc sửa danh mục.
        Hiển thị danh sách danh mục hiện có,
        cho phép thêm mới hoặc xóa danh mục.
        """
        dialog = ctk.CTkToplevel(self)
        dialog.title("Quản lý danh mục")
        dialog.geometry("420x500")
        dialog.resizable(False, False)
        dialog.grab_set()

        dialog.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width()  - 420) // 2
        y = self.winfo_rooty() + (self.winfo_height() - 500) // 2
        dialog.geometry(f"420x500+{x}+{y}")

        scroll = ctk.CTkScrollableFrame(dialog, fg_color="white")
        scroll.pack(fill="both", expand=True, padx=8, pady=8)

        ctk.CTkLabel(scroll, text="Quản lý danh mục",
                     font=("Segoe UI", 15, "bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", pady=(0, 4))
        ctk.CTkLabel(scroll,
                     text="Thêm hoặc xóa danh mục món trong thực đơn",
                     font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).pack(anchor="w", pady=(0, 16))

        # ── Danh sách danh mục hiện có
        ctk.CTkLabel(scroll, text="Danh mục hiện có",
                     font=("Segoe UI", 12, "bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", pady=(0, 6))

        self.cat_list_frame = ctk.CTkFrame(scroll, fg_color=BG_SECONDARY,
                                            corner_radius=10)
        self.cat_list_frame.pack(fill="x", pady=(0, 16))

        def refresh_cat_list():
            """Vẽ lại danh sách danh mục trong dialog."""
            for w in self.cat_list_frame.winfo_children():
                w.destroy()
            cats = MenuDAO.get_categories()
            if not cats:
                ctk.CTkLabel(self.cat_list_frame,
                             text="Chưa có danh mục nào",
                             font=FONT_SMALL,
                             text_color=TEXT_SECONDARY).pack(pady=12)
                return
            for cat in cats:
                r = ctk.CTkFrame(self.cat_list_frame,
                                  fg_color="transparent")
                r.pack(fill="x", padx=12, pady=4)

                # Tên danh mục
                ctk.CTkLabel(r, text=cat['name'],
                             font=("Segoe UI", 12, "bold"),
                             text_color=TEXT_PRIMARY).pack(side="left")

                # Nút xóa danh mục
                ctk.CTkButton(r, text="🗑",
                              width=30, height=30, corner_radius=6,
                              fg_color="#FCEBEB", text_color=DANGER_COLOR,
                              hover_color="#fecaca",
                              font=("Segoe UI", 13),
                              command=lambda c=cat: _delete_cat(c)
                              ).pack(side="right")

        def _delete_cat(cat: dict):
            """Xóa danh mục — chỉ cho phép nếu không có món nào thuộc danh mục đó."""
            confirm = msgbox.askyesno(
                "Xác nhận xóa",
                f"Xóa danh mục '{cat['name']}'?\n"
                "Danh mục phải không có món nào thì mới xóa được.",
                icon="warning")
            if confirm:
                try:
                    Database.execute_query(
                        "DELETE FROM categories WHERE id=%s", (cat['id'],))
                    refresh_cat_list()
                    self._load_data()
                except Exception:
                    msgbox.showerror(
                        "Không thể xóa",
                        f"Danh mục '{cat['name']}' đang có món.\n"
                        "Vui lòng xóa hoặc chuyển hết món trước!")

        refresh_cat_list()

        # ── Form thêm danh mục mới
        ctk.CTkFrame(scroll, fg_color="#e5e7eb",
                     height=1).pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(scroll, text="Thêm danh mục mới",
                     font=("Segoe UI", 12, "bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", pady=(0, 8))

        # Tên danh mục
        ctk.CTkLabel(scroll, text="Tên danh mục",
                     font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).pack(anchor="w")
        name_var = ctk.StringVar()
        ctk.CTkEntry(scroll, textvariable=name_var,
                     placeholder_text="VD: Cà phê, Trà, Bánh...",
                     height=38, corner_radius=8
                     ).pack(fill="x", pady=(4, 10))

        # Mô tả
        ctk.CTkLabel(scroll, text="Mô tả (tuỳ chọn)",
                     font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).pack(anchor="w")
        desc_var = ctk.StringVar()
        ctk.CTkEntry(scroll, textvariable=desc_var,
                     placeholder_text="Mô tả ngắn về danh mục...",
                     height=38, corner_radius=8
                     ).pack(fill="x", pady=(4, 10))

        # Thứ tự hiển thị
        ctk.CTkLabel(scroll, text="Thứ tự hiển thị",
                     font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).pack(anchor="w")
        order_var = ctk.StringVar(value="1")
        ctk.CTkEntry(scroll, textvariable=order_var,
                     placeholder_text="1",
                     height=38, corner_radius=8
                     ).pack(fill="x", pady=(4, 10))

        # Thông báo lỗi
        error_var = ctk.StringVar()
        ctk.CTkLabel(scroll, textvariable=error_var,
                     font=FONT_SMALL,
                     text_color=DANGER_COLOR).pack(pady=(0, 6))

        def _save_category():
            """Lưu danh mục mới vào DB."""
            name = name_var.get().strip()
            desc = desc_var.get().strip()

            if not name:
                error_var.set("Vui lòng nhập tên danh mục!")
                return

            try:
                sort_order = int(order_var.get().strip())
            except ValueError:
                error_var.set("Thứ tự hiển thị phải là số!")
                return

            try:
                Database.execute_query(
                    """INSERT INTO categories (name, description, sort_order)
                       VALUES (%s, %s, %s)""",
                    (name, desc or None, sort_order))
                name_var.set("")
                desc_var.set("")
                order_var.set("1")
                error_var.set("")
                refresh_cat_list()
                self._load_data()
            except Exception as e:
                error_var.set(f"Lỗi: {e}")

        # Nút lưu
        ctk.CTkButton(scroll, text="+ Thêm danh mục",
                      font=("Segoe UI", 12, "bold"),
                      fg_color=PRIMARY_COLOR, hover_color=PRIMARY_HOVER,
                      height=40, corner_radius=8,
                      command=_save_category
                      ).pack(fill="x", pady=(0, 8))

        # Nút đóng
        ctk.CTkButton(scroll, text="Đóng",
                      font=FONT_NORMAL,
                      fg_color=BG_SECONDARY, text_color=TEXT_PRIMARY,
                      hover_color="#e5e7eb",
                      height=40, corner_radius=8,
                      command=dialog.destroy
                      ).pack(fill="x")

    # ══════════════════════════════════════════
    #  FORM THÊM / SỬA MÓN
    # ══════════════════════════════════════════
    def _open_form(self, item: dict = None):
        """Mở dialog thêm món mới hoặc chỉnh sửa món đã có."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Thêm món mới" if not item else "Chỉnh sửa món")
        dialog.geometry("500x600")
        dialog.resizable(False, False)
        dialog.grab_set()

        dialog.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width()  - 500) // 2
        y = self.winfo_rooty() + (self.winfo_height() - 600) // 2
        dialog.geometry(f"500x600+{x}+{y}")

        inner = ctk.CTkScrollableFrame(dialog, fg_color="white")
        inner.pack(fill="both", expand=True, padx=8, pady=8)

        ctk.CTkLabel(inner,
                     text="Thêm món mới" if not item else "Chỉnh sửa món",
                     font=("Segoe UI", 16, "bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", pady=(0, 16))

        # Tên món
        ctk.CTkLabel(inner, text="Tên món",
                     font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).pack(anchor="w")
        name_var = ctk.StringVar(value=item['name'] if item else "")
        ctk.CTkEntry(inner, textvariable=name_var,
                     height=38, corner_radius=8
                     ).pack(fill="x", pady=(4, 12))

        # Danh mục + Giá
        row2 = ctk.CTkFrame(inner, fg_color="white")
        row2.pack(fill="x", pady=(0, 12))
        row2.grid_columnconfigure((0, 1), weight=1)

        cats      = MenuDAO.get_categories()
        cat_names = [c['name'] for c in cats]
        cat_ids   = [c['id']   for c in cats]

        current_cat = cat_names[0] if cat_names else ""
        if item:
            for c in cats:
                if c['id'] == item['category_id']:
                    current_cat = c['name']
                    break

        ctk.CTkLabel(row2, text="Danh mục",
                     font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).grid(row=0, column=0,
                                                      sticky="w")
        cat_var = ctk.StringVar(value=current_cat)
        ctk.CTkOptionMenu(row2, values=cat_names,
                          variable=cat_var,
                          fg_color=BG_SECONDARY,
                          button_color=PRIMARY_COLOR,
                          button_hover_color=PRIMARY_HOVER,
                          text_color=TEXT_PRIMARY,
                          height=38).grid(row=1, column=0,
                                          sticky="ew", padx=(0, 8))

        ctk.CTkLabel(row2, text="Giá bán (VNĐ)",
                     font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).grid(row=0, column=1,
                                                      sticky="w")
        price_var = ctk.StringVar(
            value=str(int(item['base_price'])) if item else "")
        ctk.CTkEntry(row2, textvariable=price_var,
                     placeholder_text="35000",
                     height=38, corner_radius=8).grid(row=1, column=1,
                                                       sticky="ew")

        # Mô tả
        ctk.CTkLabel(inner, text="Mô tả",
                     font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).pack(anchor="w")
        desc_box = ctk.CTkTextbox(inner, height=80, corner_radius=8)
        desc_box.pack(fill="x", pady=(4, 12))
        if item and item.get('description'):
            desc_box.insert("1.0", item['description'])

        # Hình ảnh
        ctk.CTkLabel(inner, text="Hình ảnh món",
                     font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).pack(anchor="w")

        img_frame = ctk.CTkFrame(inner, fg_color=BG_SECONDARY,
                                  corner_radius=8, height=110)
        img_frame.pack(fill="x", pady=(4, 4))
        img_frame.pack_propagate(False)

        self.image_path_var = ctk.StringVar(
            value=item.get('image_path', '') if item else '')
        self.img_preview = ctk.CTkLabel(img_frame, text="Chưa có ảnh",
                                         font=FONT_SMALL,
                                         text_color=TEXT_SECONDARY)
        self.img_preview.pack(expand=True)

        if item and item.get('image_path'):
            self._show_preview(item['image_path'], self.img_preview)

        ctk.CTkButton(inner, text="📁  Chọn ảnh từ máy tính",
                      font=FONT_SMALL,
                      fg_color=BG_SECONDARY, text_color=TEXT_PRIMARY,
                      hover_color="#e5e7eb",
                      height=34, corner_radius=8,
                      command=lambda: self._pick_image(
                          self.img_preview, self.image_path_var)
                      ).pack(fill="x", pady=(4, 10))

        # Tùy chọn nâng cao
        ctk.CTkLabel(inner, text="Tùy chọn nâng cao",
                     font=("Segoe UI", 11, "bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", pady=(0, 8))

        opt_row = ctk.CTkFrame(inner, fg_color="white")
        opt_row.pack(fill="x", pady=(0, 16))

        avail_var = ctk.BooleanVar(
            value=bool(item['is_available']) if item else True)
        featured_var = ctk.BooleanVar(
            value=bool(item['is_featured']) if item else False)

        ctk.CTkCheckBox(opt_row, text="Đang kinh doanh",
                        variable=avail_var, font=FONT_SMALL,
                        fg_color=PRIMARY_COLOR,
                        hover_color=PRIMARY_HOVER).pack(
                            side="left", padx=(0, 20))
        ctk.CTkCheckBox(opt_row, text="Món nổi bật ⭐",
                        variable=featured_var, font=FONT_SMALL,
                        fg_color=PRIMARY_COLOR,
                        hover_color=PRIMARY_HOVER).pack(side="left")

        # Lỗi
        error_var = ctk.StringVar()
        ctk.CTkLabel(inner, textvariable=error_var,
                     font=FONT_SMALL,
                     text_color=DANGER_COLOR).pack(pady=(0, 6))

        # Nút Hủy + Lưu
        btn_row = ctk.CTkFrame(inner, fg_color="white")
        btn_row.pack(fill="x")
        def _save():
            name     = name_var.get().strip()
            price    = price_var.get().strip()
            desc     = desc_box.get("1.0", "end").strip()
            cat_name = cat_var.get()
            img_path = self.image_path_var.get() or None

            if not name:
                error_var.set("Vui lòng nhập tên món!")
                return
            if not cat_names:
                error_var.set("Chưa có danh mục nào!")
                return
            try:
                price_val = float(price)
            except ValueError:
                error_var.set("Giá không hợp lệ!")
                return

            # Tìm cat_id từ tên danh mục
            cat_id = None
            for c in cats:
                if c['name'] == cat_name:
                    cat_id = c['id']
                    break

            if cat_id is None:
                error_var.set(f"Không tìm thấy danh mục '{cat_name}'!")
                return

            try:
                if item:
                    MenuDAO.update(item['id'], cat_id, name, desc,
                                   price_val,
                                   int(avail_var.get()),
                                   int(featured_var.get()))
                    if img_path:
                        Database.execute_query(
                            "UPDATE menu_items SET image_path=%s WHERE id=%s",
                            (img_path, item['id']))
                else:
                    MenuDAO.create(cat_id, name, desc, price_val, img_path)

                dialog.destroy()
                self._load_data()

            except Exception as e:
                error_var.set(f"Lỗi lưu: {e}")

        ctk.CTkButton(btn_row, text="Hủy",
                      font=FONT_NORMAL,
                      fg_color=BG_SECONDARY, text_color=TEXT_PRIMARY,
                      hover_color="#e5e7eb",
                      height=40, corner_radius=8,
                      command=dialog.destroy).pack(
                          side="left", fill="x",
                          expand=True, padx=(0, 6))

        ctk.CTkButton(btn_row, text="💾  Lưu thay đổi",
                      font=("Segoe UI", 12, "bold"),
                      fg_color=PRIMARY_COLOR, hover_color=PRIMARY_HOVER,
                      height=40, corner_radius=8,
                      command=_save).pack(
                          side="left", fill="x", expand=True)

    # ══════════════════════════════════════════
    #  CHỌN & PREVIEW ẢNH
    # ══════════════════════════════════════════
    def _pick_image(self, preview_label, path_var):
        """Mở hộp thoại chọn ảnh từ máy tính, copy vào thư mục assets."""
        from tkinter import filedialog
        import shutil, os

        file_path = filedialog.askopenfilename(
            title="Chọn ảnh món ăn",
            filetypes=[("Ảnh", "*.jpg *.jpeg *.png *.webp")])
        if not file_path:
            return

        os.makedirs("assets/images", exist_ok=True)
        ten_file = os.path.basename(file_path)
        dich     = os.path.join("assets/images", ten_file)
        shutil.copy2(file_path, dich)
        path_var.set(dich)
        self._show_preview(dich, preview_label)

    def _show_preview(self, image_path: str, label):
        """Hiển thị ảnh preview trong form."""
        from PIL import Image
        import os

        if not image_path or not os.path.exists(image_path):
            return
        try:
            img     = Image.open(image_path).resize((100, 90))
            ctk_img = ctk.CTkImage(light_image=img, size=(100, 90))
            label.configure(image=ctk_img, text="")
            label.image = ctk_img
        except Exception:
            label.configure(text="Không thể đọc ảnh")

    # ══════════════════════════════════════════
    #  XÓA MÓN
    # ══════════════════════════════════════════
    def _delete_item(self, item: dict):
        """Xóa món khỏi DB sau khi xác nhận."""
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