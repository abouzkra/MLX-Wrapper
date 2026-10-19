# mlx_wrapper

Python wrapper for the 42 school MiniLibX graphics library, designed to bridge the procedural C API with Object-Oriented programming and highly efficient vectorized operations using `Numpy`.

# Motivation

Working with the original MiniLibX graphics library for python 42 School projects can be difficult and inefficient when building structured/scalable applications.

Because MiniLibX is written in pure C, it enforces a functional programming style. Managing window states, hooking events, tracking active inputs, handling image allocations, and preventing segfaults/resource leaks/use-after-free problems quickly turns into boilerplate-heavy smelly code.

The `mlx_wrapper` was built to solve this problem. It encapsulates the raw C pointers and procerural functions into a clean, intuitive and safe object-oriented library allowing the developer to focus on game design, architecture, optimizations and logic rather than memory management and raw X11 communication.

# Features

### 1. High-performance Zero-Copy `Numpy` pixel buffers

Rather than using python `for` loops for pixel manipulation or copying the Mlx image data back and fourt, `Sprite` wraps the memory address provided by Mlx (`mlx_get_data_addr`) in a zero-copy `Numpy` memory view.

```python
# mlx_wrapper/asset/sprite.py

self.pixels = np.ndarray(
  shape=(self.height, self.width), # height and width of the allocated image
  dtype=np.uint32, # each pixel is represented as a 32 bit unsigned integer
                   # each 8 bits represent a color channel
                   # on little endian systems: `0xAARRGGBB` (e.g. (fully opaque red): 0xFFFF0000)
  buffer=data, # the buffer allocated by the mlx function
  strides=(sl, bpp // 8) # specifies to numpy how to navigate the buffer:
                         #   sl (size_line): width of a single image row, which is: image width * bytes_per_pixel
                         #   bpp // 8 (bytes_per_pixel) = 32 // 8 = 4: a single pixel from the image
)
```
- **Vectorized pixel manipulation**: custom per-pixel operations execute at native C-speed through vectorized Numpy array broadcasting.
- **Alpha blending `Sprite.blit`**: blitting an image on top of another one performs two fundamental operations:
  - **Bounded region calculation**: before doing any math, it calculates clipping bounds (`sx1`, `sx2`, `tx1`, `tx2`, `sy1`, `sy2`, `ty1`, `ty2`) to prevent index out-of-bounds errors when drawing sprites partially off-target.
  - **Vectorized alpha blending**: applying the alpha blending formula `out_rgb = fg_rgb * fg_a + bg_rgb * (1 - fg_a)` (Source Over (SrcOver) Porter-Duff blending mode)
    - `fg_rgb * fg_a`: determines how much of the foreground color goes through based on its opacity
    - `bg_rgb * (1 - fg_a)`: determines how much of the background color goes through based the inverse of the foreground's opacity
    - `out_a = fg_a + (bg_a * (1 - fg_a)) // 255`: composes the foreground and background's alpha channels

### 2. **Resource Safety (Use-After-Free Prevention)**:
In wrapped C libararies accessing a freed block of memory causes segfaults/undefined behaviours. `mlx_wrapper` solves this with a lifecycle guard:
- Child assets (`Sprite`, `Font`, `AnimatedSprite`) inherit a centralized `Asset.destroy()` method that clears writable attributes and sets a persistent `_destroyed` flag.
- `__getattr__` dunder method intercepts access attempts to a `DestroyedAsset`immediately raising a catchable `DestroyedResourceError` rather than crashing the python interpreter.

### 3. **XML-Driven Asset Managment with XML Schema (XSD) validation**
Managing multiple assets can clutter code. The `AssetManager` simplifies loading by pulling assets from a single XML manifest and avoids hardcoding asset paths.
- **XML Schema Validation**: validates the XML manifest against an embedded XML Schema before loading, catching typos and mistakes.
- **Global ID Uniqueness**: Enforces unique asset identifiers across all asset types.

### 4. Font Atlas & Caching
Text rendering is a massive performance bottleneck generally. The `Font` class builds a bitmap atlas from a `TrueType` font file using `Pillow` and `Numpy`:
- Supports text measurement, custom character spacing, font scaling and text coloring.
- Built-int text caching for static (e.g.: title, current level...) and dynamic strings (e.g.: timer, score...) with automated cache cleanup to prevent rasterized text leaks and frame-rate drops during rendering.

### 5. Unified Application Lifecycle & Event Management
`MLXApp` class abstracts away window creation, X11 event hooks and main loop orchestration:
- **Delta time & Frame limiting**: combines `perf_counter` with `sleep` to enforce target frame rates, maintain consistent delta time `dt` and prevent CPU halting.
- **Flexible Input Binding**: Supports both one-time trigger hooks and continuous input polling (`active_keys`/`_key_handlers`/`_held_key_handlers`) for smooth event handling, provides also easy key binding/unbinding through `bind_key`/`unbind_key`.

# Wrapper structure

```
mlx_wrapper/
├── app.py                 # Core application controller
├── asset/                 # Namespace package for asset implementations
│   ├── animated_sprite.py # Multi-sprite animations with 3 modes (Loop, Once, Ping-Pong)
│   ├── base.py            # Abstract base class for assets with the previously mentioned lifecycle guard
│   ├── font.py            # Bitmap atlas text rendering and caching
│   ├── __init__.py
│   └── sprite.py          # Mlx image wrapper with zero-copy numpy array
├── exceptions.py          # Custom hierarchical error handling
├── __init__.py
├── keys.py                # X11 keyboard key codes
└── manager.py             # XML-validated asset loader and manager
```

# Quick Start Guide

### Requirements
- Python 3.14 or later
- Python dependency manager `pip` or `uv`

### Installation instructions

- `pip`:
```bash
pip install git+https://github.com/abouzkra/MLX-Wrapper
```

- `uv`:
```bash
uv init --no-package
uv add git+https://github.com/abouzkra/MLX-Wrapper
```

### Usage Example

```python
# main.py
from mlx_wrapper import MLXApp, Sprite, KEY_LEFT, KEY_RIGHT, KEY_UP, KEY_DOWN


class TestApp(MLXApp):
    def __init__(
        self, width: int, height: int, title: str, target_fps: int = 60
    ) -> None:
        super().__init__(width, height, title, target_fps=target_fps)
        self.main = Sprite.blank(width, height)
        self.player = Sprite.blank(32, 32)
        self.player.fill(0xFFF0F0F0)

        self.player_x = (self.width - self.player.width) // 2
        self.player_y = (self.height - self.player.height) // 2
        self.player_speed = 300.0

        self.bind_key(KEY_LEFT, self.move_left, held=True)
        self.bind_key(KEY_RIGHT, self.move_right, held=True)
        self.bind_key(KEY_UP, self.move_up, held=True)
        self.bind_key(KEY_DOWN, self.move_down, held=True)

    def update(self) -> None:
        self.main.fill(0xFFB0B0B0)
        self.player.blit(
            self.main, int(self.player_x), int(self.player_y)
        )

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
        self.main.destroy()


if __name__ == "__main__":
    TestApp(1200, 800, "Test").start()
```

### Run the program
```bash
python3 main.py
# using uv
uv run python3 main.py
```

# Resources

- [Compositing and blend modes](https://ssp.impulsetrain.com/porterduff.html)
- [Game Loop](https://gameprogrammingpatterns.com/game-loop.html)
- [mlx_CLXV](https://github.com/42school/mlx_CLXV/tree/main/src)
- [MiniLibx documentation](https://harm-smits.github.io/42docs/libs/minilibx/getting_started.html)
