from typing import Dict, List, Literal, Optional
from uuid import uuid4

import PIL
import PIL.Image
from pydantic import Field

from core.providers.fabric.models.fabric_object import FabricObject
from utils.convert import data_url_to_image, image_to_base64


class FabricImage(FabricObject):
    type: Literal["Image"] = "Image"
    cropX: int = 0
    cropY: int = 0
    src: str = Field(repr=False)
    crossOrigin: Optional[str] = None
    filters: List = []

    # Additional attributes
    filename: str = Field(default_factory=lambda: f"{uuid4()}.png")
    label_to_score: Dict[str, float] = {}
    inpainted: bool = False

    def init_size(self) -> None:
        image = self.to_image()
        self.width = image.size[0]
        self.height = image.size[1]

    def set_image(self, image: PIL.Image.Image) -> None:
        image_format = image.format.lower() or "png"
        base64 = image_to_base64(image)
        mime_type = f"image/{image_format}"
        self.src = f"data:{mime_type};base64,{base64}"

    def to_image(self) -> PIL.Image.Image:
        return data_url_to_image(self.src)