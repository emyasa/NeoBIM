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

_LENGTH_METRIC_ITEMS = (
    ("ADAPTIVE", "Adaptive", "Adaptive"),
    ("KILOMETERS", "Kilometers", "Kilometers"),
    ("METERS", "Meters", "Meters"),
    ("CENTIMETERS", "Centimeters", "Centimeters"),
    ("MILLIMETERS", "Millimeters", "Millimeters"),
    ("MICROMETERS", "Micrometers", "Micrometers"),
)

_LENGTH_IMPERIAL_ITEMS = (
    ("ADAPTIVE", "Adaptive", "Adaptive"),
    ("MILES", "Miles", "Miles"),
    ("FEET", "Feet", "Feet"),
    ("INCHES", "Inches", "Inches"),
    ("THOU", "Thou", "Thou"),
)

_AREA_UNIT_ITEMS = (
    ("NONE", "None", "None"),
    ("NANO/SQUARE_METRE", "Square Nanometre", "Square Nanometre"),
    ("MICRO/SQUARE_METRE", "Square Micrometre", "Square Micrometre"),
    ("MILLI/SQUARE_METRE", "Square Millimetre", "Square Millimetre"),
    ("DECI/SQUARE_METRE", "Square Decimetre", "Square Decimetre"),
    ("CENTI/SQUARE_METRE", "Square Centimetre", "Square Centimetre"),
    ("SQUARE_METRE", "Square Metre", "Square Metre"),
    ("KILO/SQUARE_METRE", "Square Kilometre", "Squre Kilometre"),
    ("square inch", "Square Inch", "Square Inch"),
    ("square foot", "Square Foot", "Squre Foot"),
    ("square yard", "Square Yard", "Square Yard"),
    ("square mile", "Square Mile", "Square Mile"),
)

_VOLUME_UNIT_ITEMS = (
    ("NONE", "None", "None"),
    ("NANO/CUBIC_METRE", "Cubic Nanometre", "Cubic Nanometre"),
    ("MICRO/CUBIC_METRE", "Cubic Micrometre", "Cubic Micrometre"),
    ("MILLI/CUBIC_METRE", "Cubic Millimetre", "Cubic Millimetre"),
    ("DECI/CUBIC_METRE", "Cubic Decimetre", "Cubic Decimetre"),
    ("CENTI/CUBIC_METRE", "Cubic Centimetre", "Cubic Centimetre"),
    ("CUBIC_METRE", "Cubic Metre", "Cubic Metre"),
    ("KILO/CUBIC_METRE", "Cubic Kilometre", "Cubic Kilometre"),
    ("cubic inch", "Cubic Inch", "Cubic Inch"),
    ("cubic foot", "Cubic Foot", "Cubic Foot"),
    ("cubic yard", "Cubic Yard", "Cubic Yard"),
)

def get_length_unit_items(self, context):
    if self.unit_system == "METRIC":
        return _LENGTH_METRIC_ITEMS

    elif self.unit_system == "IMPERIAL":
        return _LENGTH_IMPERIAL_ITEMS

    return (("ADAPTIVE", "Adaptive", "Adaptive"),)

class NeoBIMSetupPreferences(AddonPreferences):
    bl_idname = __package__

    unit_system: EnumProperty(
        name="Unit System",
        items=_UNIT_SYSTEM_ITEMS,
    )

    length_unit: EnumProperty(
        name="Length Unit",
        items=get_length_unit_items,
    )

    area_unit: EnumProperty(
        name="Area Unit",
        items=_AREA_UNIT_ITEMS,
    )

    volume_unit: EnumProperty(
        name="Volume Unit",
        items=_VOLUME_UNIT_ITEMS,
    )

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        col = layout.column()
        col.prop(self, "unit_system")
        col.prop(self, "length_unit")
        col.prop(self, "area_unit")
        col.prop(self, "volume_unit")
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

            prefs = bpy.context.preferences.addons[__package__].preferences
            prefs.unit_system = saved_pref.get("unit_system")
            prefs.length_unit = saved_pref.get("length_unit")
            prefs.area_unit = saved_pref.get("area_unit")
            prefs.volume_unit = saved_pref.get("volume_unit")

            bpy.context.scene.unit_settings.system = saved_pref.get("unit_system")
            bpy.context.scene.unit_settings.length_unit = saved_pref.get("length_unit")
            bpy.context.scene.BIMProperties.area_unit = saved_pref.get("area_unit")
            bpy.context.scene.BIMProperties.volume_unit = saved_pref.get("volume_unit")
            bpy.context.scene.BIMProjectProperties.template_file = 'IFC4 Demo Template.ifc'
            bpy.ops.bim.create_project()
