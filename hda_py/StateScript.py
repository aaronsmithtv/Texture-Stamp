import hou
import viewerstate.utils as vsu

from typing import Any

HDA_VERSION = 1.0
HDA_AUTHOR = "aaronsmith.tv"


class StampCursor(object):
    SIZE = 0.05
    COLOR = hou.Color(1.0, 0.0, 0.0)
    PROMPT = 'Left-click to place a projection primitive.'
    POSITION_GEOMETRY = 0
    POSITION_SCREEN = 1

    def __init__(self, scene_viewer, state_name):
        self.scene_viewer = scene_viewer
        self.state_name = state_name

        self.drawable = self.init_drawable()

        # xform is our location in geometry space
        self.xform = hou.Matrix4(self.SIZE)
        self.model_xform = hou.Matrix4(1)
        self.mouse_xform = hou.Matrix4(1)

        # last_pos and resizing are used to handle resizing events
        self.last_cursor_pos = hou.Vector3()
        self.last_normal = hou.Vector3()
        self.last_uvw = hou.Vector3()

        self.prompt = self.PROMPT

    def init_drawable(self):
        """Create the advanced drawable and return it to self.drawable"""
        sops = hou.sopNodeTypeCategory()
        verb = sops.nodeVerb("tube")

        verb.setParms(
            {"type": 1, "surftype": 4, "orient": 1, "cap": 1, "rad": hou.Vector2(0.5, 0.05), "radscale": 1.0, "height": 1.0, "rows": 2, "cols": 13},
        )
        cursor_geo = hou.Geometry()
        verb.execute(cursor_geo, [])

        cursor_draw = hou.GeometryDrawableGroup("cursor")

        # adds the drawables
        cursor_draw.addDrawable(
            hou.GeometryDrawable(
                self.scene_viewer,
                hou.drawableGeometryType.Face,
                "face",
                params={
                    "color1": (0.0, 1.0, 0.0, 1.0),
                    "color2": (0.0, 0.0, 0.0, 0.33),
                    "highlight_mode": hou.drawableHighlightMode.MatteOverGlow,
                    "glow_width": 2,
                },
            )
        )
        cursor_draw.setGeometry(cursor_geo)

        return cursor_draw

    def set_color(self, color: hou.Vector4):
        """Change the colour of the drawable whilst editing parameters in the viewer state"""
        self.drawable.setParams({"color1": color})

    def show(self):
        """Enable the drawable"""
        self.drawable.show(True)

    def hide(self):
        """Disable the drawable"""
        self.drawable.show(False)

    def update_position(
        self,
        node: hou.Node,
        mouse_point: hou.Vector3,
        mouse_dir: hou.Vector3,
        intersect_geometry: hou.Geometry,
        rad: float = 0.05,
    ) -> bool:
        """Overwrites the model transform with an intersection of cursor to geo.
        also records if the intersection is hitting geo, and which prim is recorded in the hit
        """

        # Make objects for the intersect() method to modify
        cursor_pos = hou.Vector3()
        normal = hou.Vector3()
        uvw = hou.Vector3()
        prim_num = intersect_geometry.intersect(mouse_point, mouse_dir, cursor_pos, normal, uvw)
        hit = prim_num != -1

        self.last_cursor_pos = cursor_pos
        self.last_normal = normal
        self.last_uvw = uvw

        # Position is at the intersection point oriented to go along the normal
        srt = {
            "translate": (
                self.last_cursor_pos[0],
                self.last_cursor_pos[1],
                self.last_cursor_pos[2],
            ),
            "scale": (rad, rad, rad),
            "rotate": (0, 0, 0),
        }

        rotate_quaternion = hou.Quaternion()

        if hit and normal is not None:
            rotate_quaternion.setToVectors(hou.Vector3(0, 1, 0), normal)
        else:
            rotate_quaternion.setToVectors(
                hou.Vector3(0, 0, 1), hou.Vector3(mouse_dir).normalized()
            )

        rotate = rotate_quaternion.extractEulerRotates()
        srt["rotate"] = rotate

        self.update_xform(srt)

        return hit

    def update_xform(self, srt: dict) -> None:
        """Overrides the current transform with the given dictionary.
        The entries should match the keys of hou.Matrix4.explode.
        """
        try:
            current_srt = self.xform.explode()
            current_srt.update(srt)
            self.xform = hou.hmath.buildTransform(current_srt)
            self.drawable.setTransform(self.xform * self.model_xform)
        except hou.OperationFailed:
            return

    def update_model_xform(self, viewport: hou.GeometryViewport) -> None:
        """Update attribute model_xform by the selected viewport.
        This will vary depending on our position type.
        """

        self.model_xform = viewport.modelToGeometryTransform().inverted()
        self.mouse_xform = hou.Matrix4(1.0)

    def render(self, handle: int) -> None:
        """Renders the cursor in the viewport with the onDraw python state

        optimise the onDraw method by reducing the amount of operations
        calculated at draw time as possible

        Parameters:
            handle: int
                The current integer handle number
        """

        self.drawable.draw(handle)

    def show_prompt(self) -> None:
        """Write the tool prompt used in the viewer state"""
        self.scene_viewer.setPromptMessage(self.prompt)


class State(object):
    def __init__(self, state_name, scene_viewer):
        self.state_name = state_name
        self.scene_viewer = scene_viewer

        self.cursor = StampCursor(self.scene_viewer, self.state_name)

    def onMouseEvent(self, kwargs):
        """ Process mouse events
        """
        ui_event = kwargs["ui_event"]
        dev = ui_event.device()
        node = kwargs["node"]

        geometry = node.geometry()
        mouse_point, mouse_dir = ui_event.ray()

        self.cursor.update_model_xform(ui_event.curViewport())
        hit = self.cursor.update_position(
            node=node,
            mouse_point=mouse_point,
            mouse_dir=mouse_dir,
            intersect_geometry=geometry,
        )
        if hit:
            self.cursor.show()
        else:
            self.cursor.hide()

        # Must return True to consume the event
        return

    def onDraw(self, kwargs):
        """ This callback is used for rendering the drawables
        """
        handle = kwargs["draw_handle"]
        self.cursor.render(handle)

    def onEnter(self, kwargs: dict) -> None:
        node = kwargs["node"]

        self.cursor.update_xform({"scale": (1.0, 1.0, 1.0)})
        # hide the cursor before it has inherited a screen transform
        self.cursor.hide()

        # display the viewer state prompt
        self.cursor.show_prompt()

        self.scene_viewer.hudInfo(values={})

    def onExit(self, kwargs: dict) -> None:
        vsu.Menu.clear()


def createViewerStateTemplate():
    """ Mandatory entry point to create and return the viewer state
        template to register. """

    state_typename = kwargs["type"].definition().sections()["DefaultState"].contents()
    state_label = "aaron_smith::image_stamp::{0}".format(HDA_VERSION)
    state_cat = hou.sopNodeTypeCategory()

    template = hou.ViewerStateTemplate(state_typename, state_label, state_cat)
    template.bindFactory(State)
    template.bindIcon(kwargs["type"].icon())

    return template
