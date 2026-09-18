import string
from collections import UserDict

import numpy as np
from mlx import Mlx
from PIL import ImageFont

from mlx_wrapper.exceptions import FontLoadError, RenderingError

from .base import Asset
from .sprite import Sprite

CHARACTERS = string.ascii_letters + string.digits + string.punctuation + "▯"


class Font(Asset, UserDict):
    """Representation of a font as a bitmap atlas for rendering text on the
    MLX canvas.

    Attributes:
        size (int): The font size.
        spacing (int): The spacing between characters.
        atlas (Sprite): The sprite bitmapatlas containing the font characters.

    """

    def __init__(
        self,
        mlx: Mlx, mlx_ptr: int,
        font_path: str, font_size: int,
        spacing: int = 1
    ) -> None:
        """Initialize a Font instance with the specified parameters.

        The font is loaded from the specified path using `PIL.ImageFont
        .truetype` and rendered as a bitmap atlas. The implementation takes
        into account the font's bounding box and character offsets to ensure
        accurate rendering and prevent texture bleeding.
        At render time, the atlas is used to sample the correct pixel values
        for each character.

        Note: The atlas contains only printable characters and is rendered
            on a single row with dimensions:
                width = max width of all glyphs * number of glyphs
                height = max height of all glyphs

        Args:
            mlx (Mlx): MLX instance.
            mlx_ptr (int): MLX pointer.
            font_path (str): Path to the font file.
            font_size (int): Font size.
            spacing (int): Spacing between characters. Defaults to 1.

        """
        UserDict.__init__(self)
        self.mlx: Mlx = mlx
        self.mlx_ptr: int = mlx_ptr
        self.size: int = font_size
        self.spacing: int = spacing
        self.rasterized_strings: dict[str, Sprite] = {}

        try:
            font = ImageFont.truetype(font_path, font_size)
        except OSError as e:
            raise FontLoadError(f"Could not load font ({e})")
        glyph_data = {}
        max_w, max_h = 0, 0

        for c in CHARACTERS:
            bbox = font.getbbox(c)
            w = int(bbox[2] - bbox[0])
            h = int(bbox[3] - bbox[1])
            offset_y = bbox[1]

            max_w, max_h = int(max(max_w, w)), int(max(max_h, h + offset_y))
            glyph_data[c] = (w, h, offset_y)

        self.atlas: Sprite = Sprite.blank(
            mlx, mlx_ptr, int(max_w * len(CHARACTERS)) +
            font_size // 3, int(max_h)
        )

        try:
            for i, c in enumerate(CHARACTERS):
                w, h, offset_y = glyph_data[c]
                mask = font.getmask(c)
                c_bitmap = np.array(mask).reshape(mask.size[::-1])

                # Character position and width in the bitmap atlas
                cx, cw = max_w * i, w
                # Pad the character bitmap to fit in the atlas
                pad_top = int(max(0, offset_y))
                pad_bottom = int(max(0, max_h - offset_y - h))
                self.atlas.pixels[:, cx: cx + max_w] = np.pad(
                    c_bitmap,
                    ((pad_top, pad_bottom), (0, max_w - w)),
                    constant_values=0
                )
                # Store the character's position and width in the atlas
                self[c] = cx, cw

            # Space character
            self[" "] = max_w * len(CHARACTERS), font_size // 3

            self.atlas.pixels = self.atlas.pixels << 24
        except (ValueError, IndexError) as e:
            raise FontLoadError("Couldn't create font atlas: ", e) from e

    def __getitem__(self, key: str) -> tuple[int, int]:
        """Return the position and width of the character in the atlas.

        Args:
            key (str): Character to look up.

        Returns:
            tuple[int, int]: Position and width of the character in the atlas.
        """
        if key not in self:
            return self.data["▯"]
        return self.data[key]

    def measure_text(self, text: str) -> int:
        """Measure the width of the given text in pixels.

        Args:
            text (str): Text to measure.

        Returns:
            int: Width of the text in pixels.

        """
        return int(
            np.sum([self[c][1] for c in text]) + (len(text) - 1) * self.spacing
        )

    def rasterize_text(self, text: str, color: int = 0xFF000000) -> None:
        """Rasterize text into a sprite, and store it in the rasterized_strings
        cache.

        Args:
            text (str): Text to rasterize.

        """
        if not text:
            raise RenderingError("Cannot render empty string")
        text_width = self.measure_text(text)
        text_sprite = Sprite.blank(
            self.mlx, self.mlx_ptr, text_width, self.atlas.pixels.shape[0]
        )

        try:
            tx = 0
            for c in text:
                cx, cw = self[c]
                glyph = self.atlas.pixels[:, cx: cx + cw]

                text_sprite.pixels[:, tx: tx + cw] = glyph |\
                    (color & 0x00FFFFFF)
                tx = tx + self.spacing + cw
        except (ValueError, IndexError) as e:
            raise FontLoadError(f"Couldn't rasterize text {text}: ", e) from e

        self.rasterized_strings[text] = text_sprite

    def _custom_destroy(self) -> None:
        """Destroy the font, freeing its resources."""

        self.atlas.destroy()
