from mlx_wrapper import MLXApp, Sprite, AnimatedSprite, LoopMode


KEY_LEFT = 0xFF51
KEY_UP = 0xFF52
KEY_RIGHT = 0xFF53
KEY_DOWN = 0xFF54


class TestApp(MLXApp):
	def __init__(self, width: int, height: int, title: str) -> None:
		super().__init__(width, height, title)
		self.main = Sprite.blank(self.mlx, self.mlx_ptr, width, height)
		self.assets = {
			'kratos': AnimatedSprite(
					[
						Sprite.from_file(self.mlx, self.mlx_ptr, f'./sprites/sprite-1-{i}.png')
						for i in range(1, 36)
					]
				),
			'player': Sprite.blank(self.mlx, self.mlx_ptr, 32, 32)
		}
		self.assets['player'].fill(0xFF0F0000)

		self.player_x = (self.width - self.assets['player'].width) // 2
		self.player_y = (self.height - self.assets['player'].height) // 2
		self.player_speed = 300.0

		self.assets['kratos'].play()

	def update(self, dt) -> None:
		self.main.fill(0xFF301010)

		self.assets['kratos'].blit(self.main, 10, 10)
		self.assets['player'].blit(self.main, int(self.player_x), int(self.player_y))

		self.player_move(dt)
		self.assets['kratos'].update(dt)

		self.main.draw_to_window(self.win_ptr, 0, 0)

	def player_move(self, dt) -> None:
		if KEY_LEFT in self.active_keys:
			self.player_x = max(0.0, self.player_x - self.player_speed * dt)
		if KEY_UP in self.active_keys:
			self.player_y = max(0.0, self.player_y - self.player_speed * dt)
		if KEY_RIGHT in self.active_keys:
			self.player_x = min(
				float(self.width - self.assets['player'].width),
				self.player_x + self.player_speed * dt
			)
		if KEY_DOWN in self.active_keys:
			self.player_y = min(
				float(self.height - self.assets['player'].height),
				self.player_y + self.player_speed * dt
			)


if __name__ == "__main__":
	app = TestApp(800, 600, "test window")
	app.start()
