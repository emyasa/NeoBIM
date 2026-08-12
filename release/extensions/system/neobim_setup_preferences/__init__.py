import os
import json

import bpy
from bpy.props import EnumProperty
from bpy.types import AddonPreferences

_UNIT_SYSTEM_ITEMS = (
    ("NONE", "None", "No units, adaptive display only"),
    ("METRIC", "Metric", "Metric units (millimeters, meters, etc.)"),
    ("IMPERIAL", "Imperial", "Imperial units (inches, feet, etc.)"),
)

class NeoBIMSetupPreferences(AddonPreferences):
    bl_idname = __package__

    unit_system: EnumProperty(
        name="Unit System",
        description="Default unit system for the project on startup",
        items=_UNIT_SYSTEM_ITEMS,
    )

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        col = layout.column()
        col.prop(self, "unit_system")
        col.label(text="Applied on Application Start Up IFC Project", icon="INFO")

cls = NeoBIMSetupPreferences

def register():
    bpy.utils.register_class(cls)

def unregister():
    bpy.utils.unregister_class(cls)

def on_startup():
    json_path = os.path.join(bpy.utils.user_resource("CONFIG"), "neobim_setup.json")
    if os.path.isfile(json_path):
        with open(json_path) as f:
            saved_pref = json.load(f)
            bpy.context.scene.unit_settings.system = saved_pref.get("unit_system")
            bpy.context.scene.unit_settings.length_unit = saved_pref.get("length_unit")
            # bpy.context.scene.BIMProperties.area_unit = 'KILO/SQUARE_METRE'
            # bpy.context.scene.BIMProperties.volume_unit = 'CUBIC_METRE'
            # bpy.context.scene.BIMProjectProperties.template_file = 'IFC4 Demo Template.ifc'
            # bpy.ops.bim.create_project()
