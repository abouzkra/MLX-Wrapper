import string
from collections import UserDict
from mlx import Mlx
from .sprite import Sprite
import numpy as np
from PIL import ImageFont


CHARACTERS = string.ascii_letters + string.digits + string.punctuation


class Font(UserDict):
	def __init__(self, mlx: Mlx, mlx_ptr: int, font_path: str, font_size: int) -> None:
		super().__init__()
		self.size = font_size

		font = ImageFont.truetype(font_path, font_size)

		self.atlas = Sprite.blank(mlx, mlx_ptr, font_size * len(CHARACTERS), font_size)

		for i, c in enumerate(CHARACTERS):
			mask = font.getmask(c)
			c_bitmap = np.array(mask).reshape(mask.size[::-1])
			self.atlas.pixels[:, i * font_size: (i + 1) * font_size] = np.pad(
				c_bitmap,
				((font_size - c_bitmap.shape[0], 0), (0, font_size - c_bitmap.shape[1])),
				constant_values=0
			)

			self.atlas.pixels[self.atlas.pixels > 0] = 0xFF000000

	def measure_text(self, text: str, spacing: int = 1) -> int:
		return np.sum([self[c].shape[1] for c in text]) + len(text) * spacing
