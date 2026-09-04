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
						Sprite.from_file(self.mlx, self.mlx_ptr, f'./assets/kratos/sprite-1-{i}.png')
						for i in range(1, 36)
					]
				),
			'iori': AnimatedSprite(
					[
						Sprite.from_file(self.mlx, self.mlx_ptr, f'./assets/iori/frame_{i:02}_delay-0.1s.png')
						for i in range(32)
					], fps=10
				),
			'player': Sprite.blank(self.mlx, self.mlx_ptr, 32, 32)
		}
		self.assets['player'].fill(0xFFFF0000)

		self.player_x = (self.width - self.assets['player'].width) // 2
		self.player_y = (self.height - self.assets['player'].height) // 2
		self.player_speed = 300.0

		self.assets['kratos'].play()
		self.assets['iori'].play()

	def update(self, dt) -> None:
		self.player_move(dt)
		self.assets['kratos'].update(dt)
		self.assets['iori'].update(dt)

		self.main.fill(0xFFB0B0B0)

		self.assets['kratos'].blit(self.main, 25, 25)
		self.assets['iori'].blit(self.main, 25, 100)
		self.assets['player'].blit(self.main, int(self.player_x), int(self.player_y))

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

	# fg_img = Sprite.from_file(app.mlx, app.mlx_ptr, f'./sprites/sprite-1-1.png')
	# bg_img = Sprite.blank(app.mlx, app.mlx_ptr, fg_img.width, fg_img.height)
	# bg_img.fill(0xFF301010)

	# fg_bytes = fg_img.pixels.view(np.uint8).reshape(fg_img.pixels.shape + (4,)).astype(np.float32)
	# bg_bytes = bg_img.pixels.view(np.uint8).reshape(bg_img.pixels.shape + (4,)).astype(np.float32)

	# f_a = fg_bytes[..., 0:1] / 255.0
	# fg_rgb = fg_bytes[..., 1:4]
	# bg_rgb = bg_bytes[..., 1:4]

	# out_rgb = fg_rgb * f_a + bg_rgb * (1.0 - f_a)

	# fg_bytes[..., 0] = 255
	# fg_bytes[..., 1:4] = out_rgb.astype(np.uint8)
