import customtkinter as ctk
from config.settings import *
from dao.menu_dao import MenuDAO
from dao.order_dao import OrderDAO
from PIL import Image, ImageTk
import os

class POSView(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=BG_PRIMARY)
        self.app      = app
        self.user     = app.current_user
        self.cart     = []          # [{item, quantity, variant, subtotal}]
        self.all_items = []
        self.selected_category = None
        self.pack(fill="both", expand=True)
        self._build()
        self._load_menu()

    # ════════════════════════════════════════
    #  BUILD UI
    # ════════════════════════════════════════
    def _build(self):
        # ── Header
        header = ctk.CTkFrame(self, fg_color="white", height=52, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)

        h = ctk.CTkFrame(header, fg_color="white")
        h.pack(fill="both", expand=True, padx=20)

        ctk.CTkLabel(h, text="POS - Bán hàng nhanh",
                     font=("Segoe UI", 14, "bold"),
                     text_color=TEXT_PRIMARY).pack(side="left", pady=12)

        self.order_id_label = ctk.CTkLabel(
            h, text="Order ID: #TLU-mới",
            font=FONT_SMALL, text_color=TEXT_SECONDARY)
        self.order_id_label.pack(side="left", padx=20)

        # Thanh tìm kiếm
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", lambda *a: self._filter_items())
        ctk.CTkEntry(h, textvariable=self.search_var,
                     placeholder_text="Tìm kiếm món...",
                     width=220, height=34,
                     corner_radius=8).pack(side="right", pady=9)

        # ── Body: Menu trái + Cart phải
        body = ctk.CTkFrame(self, fg_color=BG_PRIMARY)
        body.pack(fill="both", expand=True)

        # Cột trái — Menu
        left = ctk.CTkFrame(body, fg_color=BG_PRIMARY)
        left.pack(side="left", fill="both", expand=True, padx=(12,6), pady=12)

        # Tab danh mục
        self.cat_frame = ctk.CTkFrame(left, fg_color="transparent")
        self.cat_frame.pack(fill="x", pady=(0,10))

        # Grid món ăn
        self.menu_scroll = ctk.CTkScrollableFrame(
            left, fg_color="transparent")
        self.menu_scroll.pack(fill="both", expand=True)

        # Cột phải — Giỏ hàng
        right = ctk.CTkFrame(body, fg_color="white",
                              width=300, corner_radius=12,
                              border_width=1, border_color="#e5e7eb")
        right.pack(side="right", fill="y", padx=(6,12), pady=12)
        right.pack_propagate(False)
        self._build_cart(right)

    def _build_cart(self, parent):
        """Khu vực giỏ hàng bên phải."""
        # Header cart
        h = ctk.CTkFrame(parent, fg_color="white")
        h.pack(fill="x", padx=16, pady=(16,8))
        ctk.CTkLabel(h, text="🛒  Giỏ hàng",
                     font=("Segoe UI", 14, "bold"),
                     text_color=TEXT_PRIMARY).pack(side="left")
        ctk.CTkButton(h, text="Xóa tất cả",
                      font=("Segoe UI", 10),
                      text_color=DANGER_COLOR,
                      fg_color="transparent", hover=False,
                      command=self._clear_cart).pack(side="right")

        ctk.CTkFrame(parent, fg_color="#e5e7eb", height=1).pack(fill="x")

        # Danh sách món trong cart
        self.cart_scroll = ctk.CTkScrollableFrame(
            parent, fg_color="white", height=320)
        self.cart_scroll.pack(fill="x", padx=8)

        self.empty_label = ctk.CTkLabel(
            self.cart_scroll,
            text="Chưa có món nào\nClick món để thêm vào giỏ",
            font=FONT_SMALL, text_color=TEXT_SECONDARY,
            justify="center")
        self.empty_label.pack(pady=40)

        ctk.CTkFrame(parent, fg_color="#e5e7eb", height=1).pack(fill="x")

        # Tổng tiền
        total_frame = ctk.CTkFrame(parent, fg_color="white")
        total_frame.pack(fill="x", padx=16, pady=12)

        rows = [
            ("Tạm tính",    "subtotal_label",  TEXT_SECONDARY, FONT_SMALL),
            ("Giảm giá",    "discount_label",  DANGER_COLOR,   FONT_SMALL),
            ("Thuế (8%)",   "tax_label",       TEXT_SECONDARY, FONT_SMALL),
        ]
        for label, attr, color, font in rows:
            r = ctk.CTkFrame(total_frame, fg_color="white")
            r.pack(fill="x", pady=2)
            ctk.CTkLabel(r, text=label, font=font,
                         text_color=TEXT_SECONDARY).pack(side="left")
            lbl = ctk.CTkLabel(r, text="0đ", font=font, text_color=color)
            lbl.pack(side="right")
            setattr(self, attr, lbl)

        ctk.CTkFrame(total_frame, fg_color="#e5e7eb",
                     height=1).pack(fill="x", pady=6)

        total_row = ctk.CTkFrame(total_frame, fg_color="white")
        total_row.pack(fill="x")
        ctk.CTkLabel(total_row, text="TỔNG CỘNG",
                     font=("Segoe UI", 13, "bold"),
                     text_color=TEXT_PRIMARY).pack(side="left")
        self.total_label = ctk.CTkLabel(
            total_row, text="0đ",
            font=("Segoe UI", 16, "bold"),
            text_color=PRIMARY_COLOR)
        self.total_label.pack(side="right")

        # Phương thức thanh toán
        ctk.CTkLabel(parent, text="Phương thức thanh toán",
                     font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).pack(anchor="w", padx=16)

        self.payment_var = ctk.StringVar(value="cash")
        pay_frame = ctk.CTkFrame(parent, fg_color="white")
        pay_frame.pack(fill="x", padx=16, pady=(4,8))

        pay_methods = [
            ("Tiền mặt",  "cash"),
            ("CK",        "transfer"),
        ]
        pay_frame.grid_columnconfigure((0,1,2), weight=1)
        self.pay_btns = {}
        for i, (label, value) in enumerate(pay_methods):
            btn = ctk.CTkButton(
                pay_frame, text=label,
                font=("Segoe UI", 11),
                height=36, corner_radius=8,
                fg_color=PRIMARY_COLOR if value=="cash" else BG_SECONDARY,
                text_color="white" if value=="cash" else TEXT_PRIMARY,
                hover_color=PRIMARY_HOVER,
                command=lambda v=value: self._select_payment(v))
            btn.grid(row=0, column=i, padx=3, sticky="ew")
            self.pay_btns[value] = btn

        # Ghi chú
        ctk.CTkLabel(parent, text="Ghi chú",
                     font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).pack(anchor="w", padx=16)
        self.note_entry = ctk.CTkEntry(
            parent, placeholder_text="Ghi chú đơn hàng...",
            height=34, corner_radius=8)
        self.note_entry.pack(fill="x", padx=16, pady=(4,8))

        # Nút thanh toán
        self.pay_btn = ctk.CTkButton(
            parent, text="THANH TOÁN",
            font=("Segoe UI", 14, "bold"),
            fg_color=PRIMARY_COLOR,
            hover_color=PRIMARY_HOVER,
            height=50, corner_radius=8,
            command=self._checkout)
        self.pay_btn.pack(fill="x", padx=16, pady=(0,16))

    # ════════════════════════════════════════
    #  LOAD & FILTER MENU
    # ════════════════════════════════════════
    def _load_menu(self):
        """Load danh mục và món từ DB."""
        cats = MenuDAO.get_categories()
        self.all_items = MenuDAO.get_available()

        # Nút "Tất cả"
        all_cats = [{"id": None, "name": "Tất cả"}] + cats
        for cat in all_cats:
            is_all = cat['id'] is None
            btn = ctk.CTkButton(
                self.cat_frame,
                text=cat['name'],
                font=FONT_SMALL,
                height=32, corner_radius=16,
                fg_color=PRIMARY_COLOR if is_all else BG_SECONDARY,
                text_color="white" if is_all else TEXT_PRIMARY,
                hover_color=PRIMARY_HOVER,
                command=lambda c=cat: self._select_category(c))
            btn.pack(side="left", padx=4)
            cat['_btn'] = btn

        self.categories    = all_cats
        self.selected_category = None
        self._render_menu(self.all_items)

    def _select_category(self, cat: dict):
        self.selected_category = cat['id']
        for c in self.categories:
            active = c['id'] == cat['id']
            c['_btn'].configure(
                fg_color=PRIMARY_COLOR if active else BG_SECONDARY,
                text_color="white" if active else TEXT_PRIMARY)
        self._filter_items()

    def _filter_items(self):
        kw    = self.search_var.get().lower()
        items = self.all_items
        if self.selected_category:
            items = [i for i in items
                     if i['category_id'] == self.selected_category]
        if kw:
            items = [i for i in items if kw in i['name'].lower()]
        self._render_menu(items)

    def _render_menu(self, items: list):
        """Vẽ lại grid món ăn."""
        for w in self.menu_scroll.winfo_children():
            w.destroy()

        COLS = 4
        for idx, item in enumerate(items):
            row = idx // COLS
            col = idx % COLS
            self._item_card(self.menu_scroll, item, row, col)

        # Đảm bảo cột giãn đều
        for c in range(COLS):
            self.menu_scroll.grid_columnconfigure(c, weight=1)

    def _item_card(self, parent, item: dict, row: int, col: int):
        """Card cho 1 món ăn."""
        card = ctk.CTkFrame(parent, fg_color="white",
                             corner_radius=10,
                             border_width=1, border_color="#e5e7eb",
                             cursor="hand2")
        card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

        # Ảnh món (hoặc placeholder)
        img_frame = ctk.CTkFrame(card, fg_color=BG_SECONDARY,
                                  height=100, corner_radius=8)
        img_frame.pack(fill="x", padx=8, pady=(8,0))
        img_frame.pack_propagate(False)

        # Badge giá
        price_badge = ctk.CTkLabel(
            img_frame,
            text=f"{int(item['base_price']):,}đ",
            font=("Segoe UI", 10, "bold"),
            fg_color=PRIMARY_COLOR,
            text_color="white",
            corner_radius=6, padx=5, pady=2)
        price_badge.place(relx=1, x=-6, y=6, anchor="ne")

        # Load ảnh nếu có
        if item.get('image_path') and os.path.exists(item['image_path']):
            try:
                img = Image.open(item['image_path']).resize((140, 100))
                photo = ImageTk.PhotoImage(img)
                img_lbl = ctk.CTkLabel(img_frame, image=photo, text="")
                img_lbl.image = photo
                img_lbl.pack(fill="both", expand=True)
            except:
                self._placeholder_img(img_frame, item)
        else:
            self._placeholder_img(img_frame, item)

        # Tên món
        ctk.CTkLabel(card, text=item['name'],
                     font=("Segoe UI", 11, "bold"),
                     text_color=TEXT_PRIMARY,
                     wraplength=130).pack(padx=8, pady=(6,0))

        # Mô tả
        desc = (item.get('description') or "")[:30]
        ctk.CTkLabel(card, text=desc,
                     font=("Segoe UI", 9),
                     text_color=TEXT_SECONDARY,
                     wraplength=130).pack(padx=8, pady=(2,8))

        # Click để thêm vào cart
        for w in [card, img_frame]:
            w.bind("<Button-1>", lambda e, i=item: self._add_to_cart(i))

    def _placeholder_img(self, parent, item):
        """Ảnh placeholder khi không có ảnh."""
        icons = {"Cà phê": "☕", "Trà & Macchiato": "🍵",
                 "Bánh ngọt": "🥐", "Khác": "🥤"}
        icon = icons.get(item.get('category_name', ''), "☕")
        ctk.CTkLabel(parent, text=icon,
                     font=("Segoe UI", 36),
                     text_color=TEXT_SECONDARY).pack(expand=True)

    # ════════════════════════════════════════
    #  CART LOGIC
    # ════════════════════════════════════════
    def _add_to_cart(self, item: dict):
        """Thêm món vào giỏ hoặc tăng số lượng."""
        for entry in self.cart:
            if entry['item']['id'] == item['id']:
                entry['quantity'] += 1
                entry['subtotal']  = entry['quantity'] * item['base_price']
                self._refresh_cart()
                return

        self.cart.append({
            'item':     item,
            'quantity': 1,
            'subtotal': float(item['base_price'])
        })
        self._refresh_cart()

    def _remove_from_cart(self, item_id: int):
        self.cart = [e for e in self.cart if e['item']['id'] != item_id]
        self._refresh_cart()

    def _change_qty(self, item_id: int, delta: int):
        for entry in self.cart:
            if entry['item']['id'] == item_id:
                entry['quantity'] += delta
                if entry['quantity'] <= 0:
                    self.cart.remove(entry)
                else:
                    entry['subtotal'] = (entry['quantity']
                                         * entry['item']['base_price'])
                break
        self._refresh_cart()

    def _clear_cart(self):
        self.cart = []
        self._refresh_cart()

    def _refresh_cart(self):
        """Vẽ lại toàn bộ giỏ hàng."""
        for w in self.cart_scroll.winfo_children():
            w.destroy()

        if not self.cart:
            self.empty_label = ctk.CTkLabel(
                self.cart_scroll,
                text="Chưa có món nào\nClick món để thêm vào giỏ",
                font=FONT_SMALL, text_color=TEXT_SECONDARY,
                justify="center")
            self.empty_label.pack(pady=40)
            self._update_totals(0)
            return

        for entry in self.cart:
            item = entry['item']
            row  = ctk.CTkFrame(self.cart_scroll, fg_color="white")
            row.pack(fill="x", pady=4, padx=4)

            # Tên món
            ctk.CTkLabel(row, text=item['name'],
                         font=("Segoe UI", 11, "bold"),
                         text_color=TEXT_PRIMARY,
                         anchor="w", wraplength=120).pack(
                             side="left", fill="x", expand=True)

            # Điều chỉnh số lượng
            qty_frame = ctk.CTkFrame(row, fg_color="white")
            qty_frame.pack(side="right")

            ctk.CTkButton(qty_frame, text="−", width=26, height=26,
                          font=("Segoe UI", 13),
                          fg_color=BG_SECONDARY,
                          text_color=TEXT_PRIMARY,
                          hover_color="#e5e7eb",
                          corner_radius=6,
                          command=lambda i=item['id']: self._change_qty(i,-1)
                          ).pack(side="left")

            ctk.CTkLabel(qty_frame,
                         text=str(entry['quantity']),
                         font=("Segoe UI", 12, "bold"),
                         text_color=TEXT_PRIMARY,
                         width=28).pack(side="left")

            ctk.CTkButton(qty_frame, text="+", width=26, height=26,
                          font=("Segoe UI", 13),
                          fg_color=PRIMARY_COLOR,
                          text_color="white",
                          hover_color=PRIMARY_HOVER,
                          corner_radius=6,
                          command=lambda i=item['id']: self._change_qty(i,1)
                          ).pack(side="left")

            # Subtotal + nút xóa
            right_col = ctk.CTkFrame(row, fg_color="white")
            right_col.pack(side="right", padx=(8,0))

            ctk.CTkLabel(right_col,
                         text=f"{int(entry['subtotal']):,}đ",
                         font=("Segoe UI", 11, "bold"),
                         text_color=PRIMARY_COLOR).pack()

            ctk.CTkButton(right_col, text="✕", width=20, height=20,
                          fg_color="transparent",
                          text_color=DANGER_COLOR,
                          hover=False, font=("Segoe UI", 11),
                          command=lambda i=item['id']: self._remove_from_cart(i)
                          ).pack()

            # Divider
            ctk.CTkFrame(self.cart_scroll,
                         fg_color="#f3f4f6", height=1).pack(
                             fill="x", padx=4)

        subtotal = sum(e['subtotal'] for e in self.cart)
        self._update_totals(subtotal)

    def _update_totals(self, subtotal: float):
        tax      = subtotal * 0.00   # Bỏ thuế nếu không cần
        total    = subtotal + tax
        self.subtotal_label.configure(text=f"{int(subtotal):,}đ")
        self.tax_label.configure(text=f"{int(tax):,}đ")
        self.discount_label.configure(text="0đ")
        self.total_label.configure(text=f"{int(total):,}đ")

    def _select_payment(self, method: str):
        self.payment_var.set(method)
        for k, btn in self.pay_btns.items():
            if k == method:
                btn.configure(fg_color=PRIMARY_COLOR, text_color="white")
            else:
                btn.configure(fg_color=BG_SECONDARY, text_color=TEXT_PRIMARY)

    # ════════════════════════════════════════
    #  CHECKOUT
    # ════════════════════════════════════════
    def _checkout(self):
        if not self.cart:
            self._show_toast("Giỏ hàng trống!", error=True)
            return

        subtotal = sum(e['subtotal'] for e in self.cart)
        total    = subtotal
        method   = self.payment_var.get()
        note     = self.note_entry.get()

        # Lưu đơn hàng
        order_id = OrderDAO.create(
            user_id        = self.user['id'],
            subtotal       = subtotal,
            total_amount   = total,
            payment_method = method,
            note           = note if note else None
        )

        # Lưu chi tiết món
        items_data = [{
            'item_id':    e['item']['id'],
            'item_name':  e['item']['name'],
            'unit_price': e['item']['base_price'],
            'quantity':   e['quantity'],
            'subtotal':   e['subtotal']
        } for e in self.cart]

        OrderDAO.add_items(order_id, items_data)

        # Xóa giỏ hàng
        self.cart = []
        self._refresh_cart()
        self.note_entry.delete(0, "end")

        self._show_toast(f"✓ Đơn hàng #{order_id} đã thanh toán thành công!")

    def _show_toast(self, msg: str, error: bool = False):
        """Thông báo nổi tạm thời."""
        toast = ctk.CTkLabel(
            self, text=msg,
            font=("Segoe UI", 12, "bold"),
            fg_color=DANGER_COLOR if error else SUCCESS_COLOR,
            text_color="white",
            corner_radius=8, padx=16, pady=10)
        toast.place(relx=0.5, rely=0.95, anchor="center")
        self.after(2500, toast.destroy)