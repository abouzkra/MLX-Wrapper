import time
from typing import Any, Callable

from mlx import Mlx

from .asset.font import Font
from .asset.sprite import Sprite
from .exceptions import NativeCallError


class MLXApp:
    """Simple wrapper for the 42 school's MLX library.

    Attributes:
        mlx: MLX instance.
        mlx_ptr: MLX pointer.
        win_ptr: Window pointer.
        width: Width of the window.
        height: Height of the window.
        target_fps: Target frames per second.
        fonts: Dictionary of loaded fonts.
        active_keys: Set of active keys.

    """

    def __init__(
        self, width: int, height: int, title: str, target_fps: int = 60
    ) -> None:
        """MLXApp constructor.

        Args:
            width (int): Width of the window.
            height (int): Height of the window.
            title (str): Title of the window.
            target_fps (int, optional): Target frames per second.
                Defaults to 60.

        """
        self.mlx: Mlx = Mlx()
        self.mlx_ptr: int = self.mlx.mlx_init()
        if self.mlx_ptr == 0:
            raise NativeCallError("mlx_init failed to initialize MLX")
        self.win_ptr: int = self.mlx.mlx_new_window(
            self.mlx_ptr, width, height, title
        )
        if self.win_ptr == 0:
            raise NativeCallError("mlx_new_window failed to create window")

        self.width: int = width
        self.height: int = height

        self.fonts: dict[str, Font] = {}

        # NOTE: although the user can specify a value higher than 60,
        # the actual frame rate is capped at the screen's refresh rate because
        # the mlx backend enforces V-sync
        self.target_fps: int = target_fps
        # Target frame time in seconds.
        self._target_frame_time: float = 0.0
        if target_fps > 0:
            self._target_frame_time = 1.0 / target_fps

        # Dictionary of key handlers mapping key codes to callback functions
        self._key_handlers: dict[int, Callable[[], None]] = {}
        # Current tick count.
        self._tick: int = 0
        # Last time the loop hook was called, used for frame rate limiting.
        # Prevents CPU halting.
        self._last_time: float = time.perf_counter()

        self.active_keys: set[int] = set()
        self._init_hooks()

    def _init_hooks(self) -> None:
        """Initialize the window hooks for key events and the loop hook."""
        self.mlx.mlx_hook(self.win_ptr, 33, 0, self._on_close, None)
        self.mlx.mlx_hook(self.win_ptr, 2, 1, self._internal_key_press, None)
        self.mlx.mlx_hook(self.win_ptr, 3, 2, self._internal_key_release, None)
        self.mlx.mlx_loop_hook(self.mlx_ptr, self._internal_loop_hook, None)

    def start(self) -> None:
        """Start the MLX application loop.

        It disables X11 key autorepeat and starts the MLX loop.
        """
        try:
            self.mlx.mlx_do_key_autorepeatoff(self.mlx_ptr)
            self.mlx.mlx_loop(self.mlx_ptr)
        finally:
            self._shutdown()

    def _on_close(self, *args: Any) -> None:
        """Close event handler.

        Re-enables X11 key autorepeat and ends the MLX loop.

        Args:
            *args: Variable length argument list.

        """
        self.mlx.mlx_loop_exit(self.mlx_ptr)
        print("Mlx loop exit")

    def bind_key(self, key: int, callback: Callable[[], None]) -> None:
        """Bind a key to a callback function.

        Args:
            key (int): Key code to bind.
            callback: Function to call when the key is pressed.

        """
        if key in self._key_handlers:
            print(f"Warning: key {key} already has a handler")
        self._key_handlers[key] = callback

    def _internal_key_press(self, key: int, *args: Any) -> None:
        """Key press event handler.

        It adds the pressed key to the active keys set and calls the
        corresponding callback function.

        Args:
            key (int): Key code of the pressed key.
            *args: Variable length argument list.

        """
        self.active_keys.add(key)
        if key == 65307:
            self._on_close()
        if key in self._key_handlers:
            self._key_handlers[key]()

    def _internal_key_release(self, key: int, *args: Any) -> None:
        """Key release event handler.

        It discards the released key from the active keysset.

        Args:
            key (int): Key code of the released key.
            *args: Variable length argument list.

        """
        self.active_keys.discard(key)

    def _internal_loop_hook(self, *args: Any) -> None:
        """Window loop hook.

        Acts as the main loop of the MLX app, calls the update function and
        enforces consistent frame rate by putting the thread to sleep
        if a cycle completes faster than _target_frame_time.

        Args:
            *args: Variable length argument list.

        """
        current_time = time.perf_counter()
        elapsed = current_time - self._last_time

        if self._target_frame_time > 0 and elapsed < self._target_frame_time:
            time.sleep(self._target_frame_time - elapsed)
            current_time = time.perf_counter()
            elapsed = current_time - self._last_time

        self._last_time = current_time

        dt = min(elapsed, 0.0333)

        self._tick += 1
        self.update(dt)

    def update(self, dt: float) -> None:
        """Update function.

        Called every frame to update the application state according to
        the elapsed time.

        Args:
            dt (float): Time elapsed since the last update.

        """
        pass

    def _shutdown(self) -> None:
        """Shutdown The MLX app.

        Cleans up resources (fonts, additional cleanup, window) and releses the
        MLX pointer.
        """
        self.mlx.mlx_do_key_autorepeaton(self.mlx_ptr)
        self._cleanup()
        print("destroy win")
        self.mlx.mlx_destroy_window(self.mlx_ptr, self.win_ptr)
        self.win_ptr = 0

        print("destroy mlx")
        self.mlx.mlx_release(self.mlx_ptr)
        self.mlx_ptr = 0

    def _cleanup(self) -> None:
        """Cleanup function.

        Destroys all font atlases and clears the fonts dictionary.
        Should be overridden by subclasses to perform additional cleanup.
        """

        self.on_cleanup()

        for f in self.fonts.values():
            f.destroy()

    def on_cleanup(self) -> None:
        """Hook for additional cleanup.

        Should be overridden by sublcasses to perform additional cleanup.
        """
        pass

    def load_ttf_font(self, font_path: str, font_size: int, key: str) -> None:
        """Load a TrueType font from font_path and store it under the given
        key.

        Args:
            font_path (str): Path to the font file.
            font_size (int): Size of the font.
            key (str): Font key.

        """
        self.fonts[key] = Font(self.mlx, self.mlx_ptr, font_path, font_size)

    def draw_text(
        self,
        target: Sprite,
        text: str,
        x: int, y: int,
        font_key: str,
        color: int = 0xFF000000,
        cache: bool = True
    ) -> None:
        """Draw text on the target sprite using the specified font and color.

        Args:
            target (Sprite): Target sprite to draw on.
            text (str): Text to draw.
            x (int): X position of the text.
            y (int): Y position of the text.
            font_key (str): Key of the font to use.
            color (int): Color of the text. Defaults to 0xFF000000.
            cache (bool): Whether to cache the rasterized text.
                Defaults to True.

        """
        if not text:
            return

        if font_key not in self.fonts:
            return

        font = self.fonts[font_key]
        if text not in font.rasterized_strings:
            font.rasterize_text(text, color, cache)
        text_sprite = font.rasterized_strings[(text, color)]

        text_sprite.blit(target, x, y)
