import os
from enum import Enum, auto
from mlx import Mlx
import numpy as np


class Sprite:
	def __init__(self, mlx: Mlx, mlx_ptr: int, img_ptr: int, width: int, height: int) -> None:
		self.mlx = mlx
		self.mlx_ptr = mlx_ptr
		self.img_ptr = img_ptr
		self.width = width
		self.height = height

		(
			self.data,
			self.bpp,
			self.sl,
			self.fmt
		) = self.mlx.mlx_get_data_addr(img_ptr)
		self.bytes_pp = self.bpp // 8

		self.pixels = np.ndarray(
			shape=(self.height, self.width),
			dtype=np.uint32,
			buffer=self.data,
			strides=(self.sl, self.bytes_pp)
		)

	@classmethod
	def blank(cls, mlx: Mlx, mlx_ptr: int, width: int, height: int) -> "Sprite":
		img_ptr = mlx.mlx_new_image(mlx_ptr, width, height)
		if not img_ptr:
			raise RuntimeError(
				f"Failed to allocate MLX image {width}x{height}"
			)
		return cls(mlx, mlx_ptr, img_ptr, width, height)

	@classmethod
	def from_file(cls, mlx: Mlx, mlx_ptr: int, file_path: str) -> "Sprite":
		ext = os.path.splitext(file_path)[1]

		match ext:
			case ".png":
				res = mlx.mlx_png_file_to_image(mlx_ptr, file_path)
			case ".xpm" | ".xpm3":
				res = mlx.mlx_xpm_file_to_image(mlx_ptr, file_path)
			case _:
				raise ValueError(f"Unsupported image file extension: {ext}")

		if not res or not res[0]:
			raise RuntimeError(f"Could not load sprite file: '{file_path}'")

		return cls(mlx, mlx_ptr, res[0], res[1], res[2])

	def set_pixel(self, x: int, y: int, color: int) -> None:
		if 0 <= x < self.width and 0 <= y < self.height:
			self.pixels[y, x] = color

	def get_pixel(self, x: int, y: int) -> int:
		if 0 <= x < self.width and 0 <= y < self.height:
			return int(self.pixels[y, x] | 0xFF000000)
		return 0

	def fill(self, color: int) -> None:
		self.pixels[:] = color

	def blit(self, target: "Sprite", dest_x: int, dest_y: int) -> None:
		sx1, sy1 = 0, 0
		sx2, sy2 = self.width, self.height
		tx1, ty1 = dest_x, dest_y

		if tx1 < 0:
			sx1 -= tx1
			tx1 = 0
		if ty1 < 0:
			sy1 -= ty1
			ty1 = 0

		tx2, ty2 = tx1 + sx2 - sx1, ty1 + sy2 - sy1
		if tx2 > target.width:
			sx2 -= tx2 - target.width
			tx2 = target.width
		if ty2 > target.height:
			sy2 -= ty2 - target.height
			ty2 = target.height

		if sx1 >= sx2 or sy1 >= sy2:
			return

		s_view = self.pixels[sy1: sy2, sx1: sx2]
		t_view = target.pixels[ty1: ty2, tx1: tx2]

		fg_bytes = s_view.view(np.uint8).reshape(s_view.shape + (4,))
		bg_bytes = t_view.view(np.uint8).reshape(t_view.shape + (4,))

		f_a = fg_bytes[..., 3:4]
		fg_rgb = fg_bytes[..., 0:3].astype(np.uint16)
		bg_rgb = bg_bytes[..., 0:3].astype(np.uint16)

		out_rgb = (fg_rgb * f_a + bg_rgb * (255 - f_a)) // 255

		bg_bytes[..., 0:3] = out_rgb.astype(np.uint8)
		bg_bytes[..., 3] = 255

	def draw_to_window(self, win_ptr: int, x: int, y: int) -> None:
		self.mlx.mlx_put_image_to_window(
			self.mlx_ptr, win_ptr, self.img_ptr, x, y
		)

	def destroy(self) -> None:
		if self.img_ptr:
			self.mlx.mlx_destroy_image(self.mlx_ptr, self.img_ptr)
			self.img_ptr = None


class LoopMode(Enum):
    LOOP = auto()
    PINGPONG = auto()
    ONCE = auto()


class AnimatedSprite:
	def __init__(self, frames: list[Sprite], fps: float = 12.0, loop_mode: LoopMode = LoopMode.LOOP) -> None:
		if not frames:
			raise ValueError("AnimatedSprite needs at least one frame.")

		self.frames = frames
		self.loop_mode = loop_mode

		self.current_index = 0
		self.ping_pong_dir = 1 # 1 = forward, -1 = backward

		self.elapsed_time = 0.0
		self.frame_time = 1.0 / fps if fps > 0 else 0.0
		self.is_playing = False
		self.is_finished = False

	def reset(self) -> None:
		self.current_index = 0
		self.is_finished = False

	def play(self) -> None:
		self.is_playing = True

	def pause(self) -> None:
		self.is_playing = False

	def stop(self) -> None:
		self.is_playing = False
		self.reset()

	def update(self, dt: float) -> None:
		if not self.is_playing or len(self.frames) <= 1:
			return

		self.elapsed_time += dt
		if self.elapsed_time >= self.frame_time:
			self.elapsed_time %= self.frame_time
			self._next_frame()

	def _next_frame(self) -> None:
		n_frames = len(self.frames)

		match self.loop_mode:
			case LoopMode.LOOP:
				self.current_index = (self.current_index + 1) % n_frames
			case LoopMode.PINGPONG:
				self.current_index += self.ping_pong_dir
				if self.current_index >= n_frames - 1:
					self.current_index = n_frames - 1
					self.ping_pong_dir = -1
				elif self.current_index <= 0:
					self.current_index = 0
					self.ping_pong_dir = 1
			case LoopMode.ONCE:
				if self.current_index < n_frames - 1:
					self.current_index += 1
				else:
					self.is_playing = False
					self.is_finished = True

	def blit(self, target: Sprite, x: int, y: int) -> None:
		current_sprite = self.frames[self.current_index]
		current_sprite.blit(target, x, y)
