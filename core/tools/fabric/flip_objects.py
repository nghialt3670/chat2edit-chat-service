from copy import deepcopy
from typing import List, Literal

from core.schemas.fabric.fabric_canvas import FabricCanvas
from core.schemas.fabric.fabric_image import FabricImage
from core.schemas.fabric.fabric_object import FabricObject
from core.tools.fabric.helpers import get_object_idxs
from core.tools.fabric.inpaint_objects import inpaint_objects


async def flip_objects(
    canvas: FabricCanvas, objects: List[FabricObject], axis: Literal["x", "y"]
) -> FabricCanvas:
    object_idxs = get_object_idxs(canvas, objects)
    canvas = deepcopy(canvas)

    await inpaint_objects(canvas, object_idxs)

    for i in object_idxs:
        obj = canvas.objects[i]
        if axis == "x":
            obj.flipX = not obj.flipX
        else:
            obj.flipY = not obj.flipY

    return canvas
