from mlx_wrapper import MLXApp, Sprite
from mlx_wrapper.exceptions import MLXError
from mlx_wrapper.manager import AssetManager

KEY_LEFT = 0xFF51
KEY_UP = 0xFF52
KEY_RIGHT = 0xFF53
KEY_DOWN = 0xFF54


class TestApp(MLXApp):
    def __init__(
        self, width: int, height: int, title: str, target_fps: int = 60
    ) -> None:
        super().__init__(width, height, title, target_fps=target_fps)
        self.main = Sprite.blank(width, height)
        self.am = AssetManager("./assets.xml")

        self.iori1 = self.am.get_animated_sprite('iori')
        self.iori2 = self.am.get_animated_sprite('iori')
        self.player = Sprite.blank(32, 32)
        self.player.fill(0xFFF0F0F0)

        self.player_x = (self.width - self.player.width) // 2
        self.player_y = (self.height - self.player.height) // 2
        self.player_speed = 300.0

        self.iori1.play()
        self.iori2.play()
        self.iori2.current_index = 9

        self.bind_key(KEY_LEFT, self.move_left, held=True)
        self.bind_key(KEY_RIGHT, self.move_right, held=True)
        self.bind_key(KEY_UP, self.move_up, held=True)
        self.bind_key(KEY_DOWN, self.move_down, held=True)

    def update(self) -> None:
        self.iori1.update(self.dt)
        self.iori2.update(self.dt)

        self.main.fill(0xFFB0B0B0)

        self.iori1.blit(self.main, 25, 100)
        self.iori2.blit(self.main, 200, 100)
        self.player.blit(
            self.main, int(self.player_x), int(self.player_y)
        )
        self.draw_text(self.main, "ap", 10, 10, self.am.get_font("minecraft"))

        self.main.draw_to_window(self.win_ptr, 0, 0)

    def move_left(self) -> None:
        self.player_x = max(0.0, self.player_x - self.player_speed * self.dt)

    def move_up(self) -> None:
        self.player_y = max(0.0, self.player_y - self.player_speed * self.dt)

    def move_right(self) -> None:
        self.player_x = min(
            float(self.width - self.player.width),
            self.player_x + self.player_speed * self.dt,
        )

    def move_down(self) -> None:
        self.player_y = min(
            float(self.height - self.player.height),
            self.player_y + self.player_speed * self.dt,
        )

    def on_cleanup(self) -> None:
        self.am.clear()
        self.main.destroy()


if __name__ == "__main__":
    try:
        app = TestApp(1200, 800, "test window")
        app.start()
    except MLXError as e:
        print(f"Error: {e}")
