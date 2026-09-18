import os
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any

import numpy as np
from mlx import Mlx

from mlx_wrapper.exceptions import AssetError, DestroyedResourceError, ImageAllocationError, ImageLoadError, NativeCallError, RenderingError


class Asset(ABC):
    def destroy(self) -> None:
        if self.__dict__.get("_destroyed"):
            return
        self._custom_destroy()
        self.__dict__.clear()
        self.__dict__["_destroyed"] = True

    @abstractmethod
    def _custom_destroy(self) -> None:
        pass

    def __getattr__(self, name: str) -> Any:
        if self._destroyed:
            raise DestroyedResourceError(
                f"Tried to access '{name}' on destroyed "
                f"{self.__class__.__name__}"
            )


class Sprite(Asset):
    """Encapsulates an MLX image for simplified sprite handling.

    Internally, an image is stored as a Zero-copy numpy array using the MLX
    data address. It exposes essential methods for sprite manipulation such as
    loading from a file, blitting, and drawing to the window.

    Attributes:
        mlx (Mlx): MLX instance.
        mlx_ptr (int): MLX pointer.
        img_ptr (int): MLX image pointer.
        width (int): Width of the sprite.
        height (int): Height of the sprite.
        fmt (int): Endianness of the data.
        pixels (np.ndarray): 2d array representing the sprite pixels.

    """

    def __init__(
        self, mlx: Mlx, mlx_ptr: int, img_ptr: int, width: int, height: int
    ) -> None:
        """Initialize a Sprite instance with the given MLX image
        pointer and dimensions.

        Args:
            mlx (Mlx): MLX instance.
            mlx_ptr (int): MLX pointer.
            img_ptr (int): MLX image pointer.
            width (int): Width of the sprite.
            height (int): Height of the sprite.

        """
        self.mlx: Mlx = mlx
        self.mlx_ptr: int = mlx_ptr
        self.img_ptr: int = img_ptr
        self.width: int = width
        self.height: int = height

        (
            data,
            bpp,
            sl,
            _,
        ) = self.mlx.mlx_get_data_addr(img_ptr)

        self.pixels: np.ndarray = np.ndarray(
            shape=(self.height, self.width),
            dtype=np.uint32,
            buffer=data,
            strides=(sl, bpp // 8),
        )

    @classmethod
    def blank(cls, mlx: Mlx, mlx_ptr: int, width: int, height: int) -> "Sprite":
        """Create a blank sprite with the given dimensions.

        Args:
            mlx (Mlx): MLX instance.
            mlx_ptr (int): MLX pointer.
            width (int): Width of the sprite.
            height (int): Height of the sprite.

        Returns:
            Sprite: The created blank sprite.

        """
        if width <= 0 or height <= 0:
            raise ImageAllocationError(
                f"Cannot allocate image with dimensions {width}x{height}"
            )
        img_ptr = mlx.mlx_new_image(mlx_ptr, width, height)
        if not img_ptr:
            raise ImageAllocationError(
                f"Failed to allocate a new image {width}x{height}"
            )
        blank = cls(mlx, mlx_ptr, img_ptr, width, height)
        blank.fill(0)
        return blank

    @classmethod
    def from_file(cls, mlx: Mlx, mlx_ptr: int, file_path: str) -> "Sprite":
        """Load a sprite from a PNG or XPM file.

        Args:
            mlx (Mlx): MLX instance.
            mlx_ptr (int): MLX pointer.
            file_path (str): Path to the image file.

        Returns:
            Sprite: The loaded sprite.

        """
        ext = os.path.splitext(file_path)[1]

        match ext:
            case ".png":
                res = mlx.mlx_png_file_to_image(mlx_ptr, file_path)
            case ".xpm" | ".xpm3":
                res = mlx.mlx_xpm_file_to_image(mlx_ptr, file_path)
            case _:
                raise ImageLoadError(
                    f"Unsupported image file extension: {ext}"
                )

        if not res or not res[0]:
            raise ImageLoadError(
                f"Could not load sprite file: '{file_path}'"
            )

        return cls(mlx, mlx_ptr, res[0], res[1], res[2])

    def set_pixel(self, x: int, y: int, color: int) -> None:
        """Set pixel at (x, y) to the given color.

        Args:
            x (int): X-coordinate of the pixel.
            y (int): Y-coordinate of the pixel.
            color (int): Color value to set.

        """
        if 0 <= x < self.width and 0 <= y < self.height:
            self.pixels[y, x] = color & 0xFFFFFFFF

    def get_pixel(self, x: int, y: int) -> int:
        """Get the color of the pixel at (x, y).

        Args:
            x (int): X-coordinate of the pixel.
            y (int): Y-coordinate of the pixel.

        Returns:
            int: Color value of the pixel.

        """
        if 0 <= x < self.width and 0 <= y < self.height:
            return int(self.pixels[y, x])
        return 0

    def fill(self, color: int) -> None:
        """Fill the sprite with the given color.

        Args:
            color (int): Color value to fill.

        """
        color &= 0xFFFFFFFF
        self.pixels[:] = color

    def blit(self, target: "Sprite", dest_x: int, dest_y: int) -> None:
        """Blit onto a target sprite at (dest_x, dest_y).

        Uses a simple implementation of alpha blending to blend pixels from
        the source onto the target.

        Args:
            target (Sprite): Target sprite to blit onto.
            dest_x (int): Destination x-coordinate.
            dest_y (int): Destination y-coordinate.

        """
        try:
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

            s_view = self.pixels[sy1:sy2, sx1:sx2]
            t_view = target.pixels[ty1:ty2, tx1:tx2]

            fg_bytes = s_view.view(np.uint8).reshape(s_view.shape + (4,))
            bg_bytes = t_view.view(np.uint8).reshape(t_view.shape + (4,))

            f_a = fg_bytes[..., 3:4]
            fg_rgb = fg_bytes[..., 0:3].astype(np.uint16)
            bg_rgb = bg_bytes[..., 0:3].astype(np.uint16)

            out_rgb = (fg_rgb * f_a + bg_rgb * (255 - f_a)) // 255

            bg_bytes[..., 0:3] = out_rgb.astype(np.uint8)
            bg_bytes[..., 3] = 255
        except (ValueError, IndexError) as e:
            raise RenderingError(
                f"blit failed: src={self.width}x{self.height} "
                f"on target={target} at dest={(dest_x, dest_y)}"
            ) from e

    def draw_to_window(self, win_ptr: int, x: int, y: int) -> None:
        """Draw to the window at (x, y).

        Args:
            win_ptr (int): Window pointer.
            x (int): X-coordinate.
            y (int): Y-coordinate.

        """
        self.mlx.mlx_put_image_to_window(self.mlx_ptr, win_ptr, self.img_ptr, x, y)

    def _custom_destroy(self) -> None:
        """Destroy the sprite, freeing its resources."""
        if self.img_ptr:
            self.mlx.mlx_destroy_image(self.mlx_ptr, self.img_ptr)


class LoopMode(Enum):
    """Loop mode for the animated sprite.

    Attributes:
        LOOP (int): Loop the animation.
        PINGPONG (int): Ping-pong the animation.
        ONCE (int): Play the animation once.

    """

    LOOP = auto()
    PINGPONG = auto()
    ONCE = auto()


class AnimatedSprite(Asset):
    """A simple implementation of animated sprites.

    Attributes:
        frames (list[Sprite]): List of frames for the animation.
        loop_mode (LoopMode): Loop mode for the animation.
        current_index (int): Current frame index.
        ping_pong_dir (int): Ping-pong direction.
        elapsed_time (float): Elapsed time since the animation started.
        frame_time (float): Time between frames.
        is_playing (bool): Whether the animation is playing.
        is_finished (bool): Whether the animation is finished (used for
            ONCE loop mode).

    """

    def __init__(
        self,
        frames: list[Sprite],
        fps: int = 12,
        loop_mode: LoopMode = LoopMode.LOOP,
    ) -> None:
        """Initialize an animated sprite with the given frames, frames per
        second, and loop mode.

        Args:
            frames (list[Sprite]): List of frames for the animation.
            fps (int): Frames per second.
            loop_mode (LoopMode): Loop mode for the animation. Defaults to
                LoopMode.LOOP.
        """
        if not frames:
            raise AssetError("AnimatedSprite needs at least one frame.")

        self.frames: list[Sprite] = frames
        self.loop_mode: LoopMode = loop_mode

        self.current_index: int = 0
        self.ping_pong_dir: int = 1  # 1 = forward, -1 = backward

        self.elapsed_time: float = 0.0
        self.frame_time: float = 1.0 / fps if fps > 0 else 0.0
        self.is_playing: bool = False
        self.is_finished: bool = False

    def reset(self) -> None:
        """Reset the animation to the beginning."""
        self.current_index = 0
        self.is_finished = False

    def play(self) -> None:
        """Play the animation."""
        self.is_playing = True

    def pause(self) -> None:
        """Pause the animation."""
        self.is_playing = False

    def stop(self) -> None:
        """Stop the animation."""
        self.is_playing = False
        self.reset()

    def update(self, dt: float) -> None:
        """Update the animation state based on the elapsed time.

        Args:
            dt (float): The elapsed time since the last update.

        """
        if not self.is_playing or len(self.frames) <= 1:
            return

        self.elapsed_time += dt
        if self.elapsed_time >= self.frame_time:
            self.elapsed_time %= self.frame_time
            self._next_frame()

    def _next_frame(self) -> None:
        """Advance to the next frame based on the loop mode."""
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
        """Blit the current frame onto the target sprite at (x, y).

        Args:
            target (Sprite): The target sprite to blit onto.
            x (int): The x-coordinate of the target position.
            y (int): The y-coordinate of the target position.

        """
        self.frames[self.current_index].blit(target, x, y)

    def _custom_destroy(self) -> None:
        """Destroy the animated sprite, freeing its resources."""

        for f in self.frames:
            f.destroy()
