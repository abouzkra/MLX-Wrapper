import os
from random import sample

from lxml import etree as et

from .asset.animated_sprite import AnimatedSprite
from .asset.font import Font
from .asset.sprite import Sprite
from .exceptions import AssetManagerError

ASSET_SCHEMA = """<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">

    <xs:element name="assets">
        <xs:complexType>
            <xs:all>
            <xs:element name="fonts" minOccurs="0" maxOccurs="1">
                <xs:complexType>
                    <xs:sequence>
                        <xs:element name="font" minOccurs="0" maxOccurs="unbounded">
                            <xs:complexType>
                                <xs:attribute name="id" type="xs:string" use="required"/>
                                <xs:attribute name="path" type="xs:string" use="required"/>
                                <xs:attribute name="size" type="xs:positiveInteger" use="required"/>
                                <xs:attribute name="spacing" type="xs:positiveInteger" use="optional"/>
                            </xs:complexType>
                        </xs:element>
                    </xs:sequence>
                </xs:complexType>
            </xs:element>

            <xs:element name="sprites" minOccurs="0" maxOccurs="1">
                <xs:complexType>
                    <xs:sequence>
                        <xs:element name="sprite" minOccurs="0" maxOccurs="unbounded">
                            <xs:complexType>
                                <xs:attribute name="id" type="xs:string" use="required"/>
                                <xs:attribute name="path" type="xs:string" use="required"/>
                            </xs:complexType>
                        </xs:element>
                    </xs:sequence>
                </xs:complexType>
            </xs:element>

            <xs:element name="animated_sprites" minOccurs="0" maxOccurs="1">
                <xs:complexType>
                    <xs:sequence>
                        <xs:element name="animated_sprite" minOccurs="0" maxOccurs="unbounded">
                            <xs:complexType>
                                <xs:sequence>
                                    <xs:element name="frame" minOccurs="1" maxOccurs="unbounded">
                                        <xs:complexType>
                                            <xs:attribute name="path" type="xs:string" use="required"/>
                                        </xs:complexType>
                                    </xs:element>
                                </xs:sequence>
                                <xs:attribute name="id" type="xs:string" use="required"/>
                                <xs:attribute name="fps" type="xs:integer" use="required"/>
                            </xs:complexType>
                        </xs:element>
                    </xs:sequence>
                </xs:complexType>
            </xs:element>
            </xs:all>
            <xs:attribute name="base_dir" type="xs:string" use="required"/>
        </xs:complexType>
    </xs:element>
</xs:schema>
"""


class AssetManager:
    def __init__(self, xml_file: str) -> None:
        self.fonts: dict[str, Font] = {}
        self.sprites: dict[str, Sprite] = {}
        self.animated_sprites: dict[str, AnimatedSprite] = {}
        self._seen_ids: set[str] = set()

        try:
            xml_tree = et.parse(xml_file)
        except OSError as e:
            raise AssetManagerError(
                f"Couldn't load XML asset file '{xml_file}': {e}"
            )
        except et.XMLSyntaxError as e:
            raise AssetManagerError(
                f"Syntax error in XML asset file '{xml_file}': {e}"
            )

        self._validate_xml(xml_tree)
        base_dir = xml_tree.getroot().attrib['base_dir']

        for sprite_el in xml_tree.iterfind(".//sprite"):
            sprite_id = sprite_el.attrib['id']
            self._check_id(sprite_id)
            sprite_path = os.path.join(base_dir, sprite_el.attrib['path'])
            self.sprites[sprite_id] = Sprite.from_file(sprite_path)

        for font_el in xml_tree.iterfind(".//font"):
            font_id = font_el.attrib['id']
            self._check_id(font_id)
            font_path = os.path.join(base_dir, font_el.attrib['path'])
            font_size = int(font_el.get('size', 16))
            font_spacing = int(font_el.get('spacing', 1))
            self.fonts[font_id] = Font(font_path, font_size, font_spacing)

        for anim_sprite_el in xml_tree.iterfind(".//animated_sprite"):
            anim_sprite_id = anim_sprite_el.attrib['id']
            self._check_id(anim_sprite_id)
            anim_sprite_fps = int(anim_sprite_el.attrib['fps'])
            frames = [
                Sprite.from_file(os.path.join(base_dir, frame.get("path")))
                for frame in anim_sprite_el.iterfind(".//frame")
            ]
            self.animated_sprites[anim_sprite_id] = AnimatedSprite(
                frames, anim_sprite_fps
            )

    def _check_id(self, asset_id: str) -> None:
        if asset_id in self._seen_ids:
            raise AssetManagerError(
                f"Duplicate asset id '{asset_id}', "
                "asset id must be unique globally."
            )
        self._seen_ids.add(asset_id)

    def _validate_xml(self, xml_tree: et.ElementTree[et.Element[str]]) -> None:
        try:
            schema = et.XMLSchema(et.fromstring(ASSET_SCHEMA.encode("utf-8")))
        except (AttributeError, et.XMLSyntaxError, ValueError) as e:
            raise AssetManagerError(f"Failed to load XML Schema: {e}") from e

        root = xml_tree.getroot()

        if not schema.validate(root):
            raise AssetManagerError(
                f"Invalid XML Assets file: {schema.error_log[0]}"
            )

    def get_sprite(self, id: str) -> Sprite:
        if id not in self.sprites:
            raise AssetManagerError(f"No sprite with id '{id}' was found.")
        return self.sprites[id]

    def get_font(self, id: str) -> Font:
        if id not in self.fonts:
            raise AssetManagerError(f"No font with id '{id}' was found.")
        return self.fonts[id]

    def get_animated_sprite(self, id: str) -> AnimatedSprite:
        if id not in self.animated_sprites:
            raise AssetManagerError(f"No animated sprite with id '{id}' was found.")
        return self.animated_sprites[id]
