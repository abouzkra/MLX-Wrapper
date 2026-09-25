from .asset.animated_sprite import AnimatedSprite
from .asset.font import Font
from .asset.sprite import Sprite
from .exceptions import AssetError
from lxml import etree


class AssetManager:
    def __init__(self) -> None:
        try:
            with open("./mlx_wrapper/assets.xsd", 'rb') as f:
               self.xml_schema = etree.XMLSchema(etree.XML(f.read()))
        except (
            AttributeError, OSError, etree.XMLSyntaxError, ValueError
        ) as e:
            raise AssetError(f"Failed to load XML Schema: {e}") from e

        self.fonts: dict[str, Font] = {}
        self.sprites: dict[str, Sprite] = {}
        self.animated_sprites: dict[str, AnimatedSprite] = {}

    def validate_xml(self, xml_file: str) -> bool:
        pass

    def from_xml(self, xml_file: str) -> None:
        pass

    def load_sprite(self, path: str) -> None:
        pass

    def load_font(self, path: str) -> None:
        pass

    def load_animated_sprite(self, path: str) -> None:
        pass

    def get_sprite(self, id: str) -> None:
        pass

    def get_font(self, id: str) -> None:
        pass

    def get_animated_sprite(self, id: str) -> None:
        pass
