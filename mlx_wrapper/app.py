import time
from mlx import Mlx


class MLXApp:
	"""Simple wrapper for the 42 school's MLX library."""
	def __init__(self, width: int, height: int, title: str, target_fps: int = 60) -> None:
		self.mlx = Mlx()
		self.mlx_ptr = self.mlx.mlx_init()
		self.win_ptr = self.mlx.mlx_new_window(self.mlx_ptr, width, height, title)

		self.width = width
		self.height = height

		self.target_fps = target_fps
		self._target_frame_time = 1.0 / target_fps if target_fps > 0 else 0.0

		self._key_handlers = {}
		self._tick = 0
		self._last_time = time.perf_counter()

		self.active_keys = set()
		self._init_hooks()

	def _init_hooks(self) -> None:
		self.mlx.mlx_hook(self.win_ptr, 33, 0, self._on_close, None)
		self.mlx.mlx_hook(self.win_ptr, 2, 1, self._internal_key_press, None)
		self.mlx.mlx_hook(self.win_ptr, 3, 2, self._internal_key_release, None)
		self.mlx.mlx_loop_hook(self.mlx_ptr, self._internal_loop_hook, None)

	def start(self) -> None:
		self.mlx.mlx_do_key_autorepeatoff(self.mlx_ptr)
		self.mlx.mlx_loop(self.mlx_ptr)

		print("destroy win")
		self.mlx.mlx_destroy_window(self.mlx_ptr, self.win_ptr)
		self.win_ptr = None
		print("destroy mlx")
		self.mlx.mlx_release(self.mlx_ptr)
		self.mlx_ptr = None

	def _on_close(self, *args) -> None:
		self.mlx.mlx_do_key_autorepeaton(self.mlx_ptr)
		self.mlx.mlx_loop_exit(self.mlx_ptr)

	def bind_key(self, key: int, callback) -> None:
		self._key_handlers[key] = callback

	def _internal_key_press(self, key: int, *args) -> None:
		self.active_keys.add(key)
		if key == 65307:
			self._on_close()
		if key in self._key_handlers:
			self._key_handlers[key]()

	def _internal_key_release(self, key: int, *args) -> None:
		self.active_keys.discard(key)

	def _internal_loop_hook(self, *args) -> None:
		current_time = time.perf_counter()
		elapsed = current_time - self._last_time

		if self._target_frame_time > 0 and elapsed < self._target_frame_time:
			sleep = self._target_frame_time - elapsed
			time.sleep(sleep)
			current_time = time.perf_counter()

		dt = current_time - self._last_time
		self._last_time = current_time

		if dt > 0.1:
			dt = 0.1

		self._tick += 1
		self.update(dt)

	def update(self, dt: float) -> None:
		pass
