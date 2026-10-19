from mlx_wrapper import (
    KEY_DOWN,
    KEY_LEFT,
    KEY_RIGHT,
    KEY_UP,
    AssetManager,
    MLXApp,
    MLXError,
    Sprite,
)


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

        self.timer = 200

        self.iori1.play()
        self.iori2.play()
        self.iori2.current_index = 9

        self.bind_key(KEY_LEFT, self.move_left, held=True)
        self.bind_key(KEY_RIGHT, self.move_right, held=True)
        self.bind_key(KEY_UP, self.move_up, held=True)
        self.bind_key(KEY_DOWN, self.move_down, held=True)

    def update_timer(self) -> None:
        self.timer -= self.dt

    def draw_timer(self) -> None:
        font = self.am.get_font("minecraft")
        min, sec = divmod(self.timer, 60)
        timer_text = f"{int(min):02}:{int(sec):02}"
        font.draw_text(
            self.main, timer_text, 10, 10, id="timer", color=0xFF000000
        )

    def update(self) -> None:
        self.update_timer()
        self.iori1.update(self.dt)
        self.iori2.update(self.dt)

        self.main.fill(0xFFB0B0B0)

        self.iori1.blit(self.main, 25, 100)
        self.iori2.blit(self.main, 200, 100)
        self.player.blit(
            self.main, int(self.player_x), int(self.player_y)
        )
        self.draw_timer()

        self.main.draw_to_window(0, 0)

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
        app = TestApp(1200, 800, "test window", target_fps=30)
        app.start()
    except MLXError as e:
        print(f"Error: {e}")
