import os
from enum import Enum, auto
from typing import Optional
from mlx import Mlx


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
            offset = y * self.sl + x * self.bytes_pp
            self.data[offset: offset + self.bytes_pp] = color.to_bytes(self.bytes_pp, 'little')

    def get_pixel(self, x: int, y: int) -> int:
        if 0 <= x < self.width and 0 <= y < self.height:
            offset = y * self.sl + x * self.bytes_pp
            return int.from_bytes(self.data[offset: offset + self.bytes_pp + 1]) | 0xFF000000
        return 0

    def fill(self, color: int) -> None:
        color_bytes = color.to_bytes(self.bytes_pp, 'little')
        for y in range(self.height):
            row = y * self.sl
            for x in range(self.width):
                offset = row + x * self.bytes_pp
                self.data[offset: offset + self.bytes_pp] = color_bytes

    def blit(self, target: "Sprite", dest_x: int, dest_y: int, colorkey: Optional[int] = None) -> None:
        for sy in range(self.height):
            ty = dest_y + sy
            if 0 <= ty < target.height:
                for sx in range(self.width):
                    tx = dest_x + sx
                    if 0 <= tx < target.width:
                        pixel_color = self.get_pixel(sx, sy)
                        if colorkey is None or pixel_color != colorkey:
	                        target.set_pixel(tx, ty, pixel_color)

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
    def __init__(self, frames: list[Sprite], tpf: int = 4, loop_mode: LoopMode = LoopMode.LOOP) -> None:
        if not frames:
            raise ValueError("AnimatedSprite needs at least one frame.")

        self.frames = frames
        self.tpf = tpf # tick per frame
        self.loop_mode = loop_mode

        self.current_index = 0
        self.tick_counter = 0
        self.ping_pong_dir = 1 # 1 = forward, -1 = backward
        self.is_playing = False
        self.is_finished = False

    def reset(self) -> None:
        self.current_index = 0
        self.tick_counter = 0
        self.is_finished = False

    def play(self) -> None:
        self.is_playing = True

    def pause(self) -> None:
        self.is_playing = False

    def stop(self) -> None:
        self.is_playing = False
        self.reset()

    def update(self) -> None:
        if not self.is_playing or len(self.frames) <= 1:
            return

        self.tick_counter += 1
        if self.tick_counter >= self.tpf:
            self.tick_counter = 0
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

    def draw(self, target: Sprite, x: int, y: int, colorkey: Optional[int] = None) -> None:
        current_sprite = self.frames[self.current_index]
        current_sprite.blit(target, x, y, colorkey=colorkey)
