import customtkinter as ctk
from config.settings import *

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Cấu hình cửa sổ
        self.title(APP_NAME)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(WINDOW_MIN_W, WINDOW_MIN_H)
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")

        # Căn giữa màn hình
        self._center_window()

        # Lưu thông tin user đang đăng nhập
        self.current_user = None

        # Container chứa tất cả màn hình
        self.container = ctk.CTkFrame(self, fg_color=BG_PRIMARY)
        self.container.pack(fill="both", expand=True)

        # Dictionary lưu các frame màn hình
        self.frames = {}

        # Khởi động — hiển thị màn hình Login trước
        self.show_login()

    def _center_window(self):
        """Căn cửa sổ ra giữa màn hình."""
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x  = (sw - WINDOW_WIDTH)  // 2
        y  = (sh - WINDOW_HEIGHT) // 2
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")

    def clear_container(self):
        """Xóa toàn bộ nội dung container."""
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_login(self):
        """Chuyển sang màn hình Login."""
        self.clear_container()
        # Import ở đây để tránh circular import
        from views.login_view import LoginView
        LoginView(self.container, self)

    def show_register(self):
        """Chuyển sang màn hình Register."""
        self.clear_container()
        from views.register_view import RegisterView
        RegisterView(self.container, self)

    def show_main(self, user: dict):
        """Chuyển sang màn hình chính sau khi đăng nhập."""
        self.current_user = user
        self.clear_container()
        from views.main_window import MainWindow
        MainWindow(self.container, self)

    def logout(self):
        """Đăng xuất — quay về Login."""
        self.current_user = None
        self.show_login()


if __name__ == "__main__":
    app = App()
    app.mainloop()