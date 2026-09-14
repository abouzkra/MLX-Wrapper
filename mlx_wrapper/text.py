import string
from collections import UserDict
from mlx import Mlx
from .sprite import Sprite
import numpy as np
from PIL import ImageFont


CHARACTERS = string.ascii_letters + string.digits + string.punctuation


class Font(UserDict):
	def __init__(self, mlx: Mlx, mlx_ptr: int, font_path: str, font_size: int, spacing: int = 1) -> None:
		super().__init__()
		self.size = font_size
		self.spacing = spacing

		font = ImageFont.truetype(font_path, font_size)
		glyph_data = {}
		max_w, max_h = 0, 0

		for c in CHARACTERS:
			bbox = font.getbbox(c)
			w = bbox[2] - bbox[0]
			h = bbox[3] - bbox[1]
			offset_x = bbox[0]

			max_w, max_h = max(max_w, w), max(max_h, h)
			glyph_data[c] = (w, h, offset_x)

		self.atlas = Sprite.blank(
			mlx, mlx_ptr,
			int(max_w * len(CHARACTERS)) + font_size // 3,
			int(max_h)
		)

		for i, c in enumerate(CHARACTERS):
			w, h, offset_x = glyph_data[c]
			mask = font.getmask(c)
			c_bitmap = np.array(mask).reshape(mask.size[::-1])

			cx, cw = max_w * i, w
			self.atlas.pixels[:, cx: cx + max_w] = np.pad(
				c_bitmap,
				((max_h - h, 0), (0, max_w - w)),
				constant_values=0
			)
			self[c] = cx, cw

		self[' '] = max_w * len(CHARACTERS), font_size // 3

		self.atlas.pixels[self.atlas.pixels > 0] = 0xFF000000

	def measure_text(self, text: str) -> int:
		return int(np.sum([self[c][1] for c in text]) + (len(text) - 1) * self.spacing)
