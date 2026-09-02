from mlx import Mlx
import sys

class MLXApp:
    """Simple wrapper for the 42 school's MLX library."""
    def __init__(self, width: int, height: int, title: str) -> None:
        self.mlx = Mlx()
        self.mlx_ptr = self.mlx.mlx_init()
        self.win_ptr = self.mlx.mlx_new_window(self.mlx_ptr, width, height, title)

        self.width = width
        self.height = height

        self._key_handlers = {}
        self._tick = 0

        self._init_hooks()

    def _init_hooks(self) -> None:
        self.mlx.mlx_hook(self.win_ptr, 33, 0, self._on_close, None)
        self.mlx.mlx_hook(self.win_ptr, 2, 1, self._internal_key_hook, None)
        self.mlx.mlx_loop_hook(self.win_ptr, self._internal_loop_hook, None)

    def start(self) -> None:
        self.mlx.mlx_loop(self.mlx_ptr)

    def _on_close(self) -> None:
        print("destroy win")
        self.mlx.mlx_destroy_window(self.mlx_ptr, self.win_ptr)
        print("destroy mlx")
        self.mlx.mlx_release(self.mlx_ptr)
        sys.exit(0)

    def bind_key(self, key: int, callback) -> None:
        self._key_handlers[key] = callback

    def _internal_key_hook(self, key: int, param) -> None:
        if key == 65307:
            self._on_close()
        if key in self._key_handlers:
            self._key_handlers[key]()

    def _internal_loop_hook(self, param) -> None:
        self._tick += 1
        self.update(self._tick)

    def update(self, current_tick: int) -> None:
        pass
