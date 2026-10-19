"""Wrapper for the 42 school MiniLibX graphics library.

Designed to simplify:
    - Window management
    - Event handling
    - Rendering
    - Asset management

Components:
    - MLXApp: Main application controller, simplifies the creation and
        management of a window, event loop and event handling.
    - AssetManager: Manages the loading and unloading of assets through an xml
        manifest file (the structure is defined in the project's README.md
        file).
    - Assets:
        - Sprite: Abstraction for the MLX images, can be drawn to the screen,
            blitted on another one through alpha blending, loaded from a
            png/xpm file.
        - AnimatedSprite: Just a list of sprites that are played in various
            modes (loop, once, ping-pong).
        - Font: Creates a bitmap font atlas from a TrueType font file,
            allowing text rendering with custom font sizes and colors.
    - Exceptions: Comprehensive exception classes for handling errors related
        to window errors, asset loading/rendering, and resource management...
    - Keys: X11 keycode constants for use in event handling.
"""


from .app import MLXApp
from .asset.animated_sprite import AnimatedSprite, LoopMode
from .asset.font import Font
from .asset.sprite import Sprite
from .exceptions import (
    AssetError,
    AssetManagerError,
    DestroyedResourceError,
    FontLoadError,
    ImageAllocationError,
    ImageLoadError,
    MLXError,
    NativeCallError,
    RenderingError,
)

from .keys import (
    # Arrow keys
    KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_UP,
    # Special keys
    KEY_BACKSPACE, KEY_ENTER, KEY_ESC, KEY_SPACE, KEY_TAB,
    KEY_ALT_L, KEY_ALT_R, KEY_CTRL_L, KEY_CTRL_R, KEY_SHIFT_L, KEY_SHIFT_R,
    # Alphabet keys
    KEY_A, KEY_B, KEY_C, KEY_D, KEY_E, KEY_F, KEY_G, KEY_H, KEY_I, KEY_J,
    KEY_K, KEY_L, KEY_M, KEY_N, KEY_O, KEY_P, KEY_Q, KEY_R, KEY_S, KEY_T,
    KEY_U, KEY_V, KEY_W, KEY_X, KEY_Y, KEY_Z,
    # Digit keys
    KEY_0, KEY_1, KEY_2, KEY_3, KEY_4,
    KEY_5, KEY_6, KEY_7, KEY_8, KEY_9
)

from .manager import AssetManager

__all__ = [
    "AnimatedSprite",
    "AssetManager",
    "Font",
    "LoopMode",
    "MLXApp",
    "Sprite",
    "AssetError",
    "AssetManagerError",
    "DestroyedResourceError",
    "FontLoadError",
    "ImageAllocationError",
    "ImageLoadError",
    "MLXError",
    "NativeCallError",
    "RenderingError",
    "KEY_DOWN", "KEY_LEFT", "KEY_RIGHT", "KEY_UP",
    "KEY_BACKSPACE", "KEY_ENTER", "KEY_ESC", "KEY_SPACE", "KEY_TAB",
    "KEY_ALT_L", "KEY_ALT_R", "KEY_CTRL_L", "KEY_CTRL_R", "KEY_SHIFT_L",
    "KEY_SHIFT_R",
    "KEY_A", "KEY_B", "KEY_C", "KEY_D", "KEY_E", "KEY_F", "KEY_G", "KEY_H",
    "KEY_I", "KEY_J", "KEY_K", "KEY_L", "KEY_M", "KEY_N", "KEY_O", "KEY_P",
    "KEY_Q", "KEY_R", "KEY_S", "KEY_T", "KEY_U", "KEY_V", "KEY_W", "KEY_X",
    "KEY_Y", "KEY_Z",
    "KEY_0", "KEY_1", "KEY_2", "KEY_3", "KEY_4",
    "KEY_5", "KEY_6", "KEY_7", "KEY_8", "KEY_9"
]
