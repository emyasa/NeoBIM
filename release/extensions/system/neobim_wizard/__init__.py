# SPDX-FileCopyrightText: 2026 NeoBIM Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""First-run unit system setup for NeoBIM.

The required setup step is enforced by a native dialog shown before the main
event loop starts (macOS). Its choices are handed to this addon through a
`neobim_setup.json` file in the user config directory, which is read once,
applied to user preferences and the startup scene, then deleted. Skipping is
impossible: the dialog only exits the process without completing setup, so it
re-appears on the next launch.
"""

import json
import os

import bpy
from bpy.app.handlers import persistent
from bpy.props import BoolProperty, EnumProperty
from bpy.types import AddonPreferences

# Blender's stable `UnitSettings.length_unit` identifiers per unit system.
_LENGTH_UNITS_METRIC = [
    ("ADAPTIVE", "Adaptive", "Adapt to the view zoom level"),
    ("MICROMETERS", "Micrometers", "Use micrometers"),
    ("MILLIMETERS", "Millimeters", "Use millimeters"),
    ("CENTIMETERS", "Centimeters", "Use centimeters"),
    ("METERS", "Meters", "Use meters"),
    ("KILOMETERS", "Kilometers", "Use kilometers"),
]

_LENGTH_UNITS_IMPERIAL = [
    ("ADAPTIVE", "Adaptive", "Adapt to the view zoom level"),
    ("THOU", "Thousandths of an Inch", "Use thousandths of an inch"),
    ("INCHES", "Inches", "Use inches"),
    ("FEET", "Feet", "Use feet"),
    ("YARDS", "Yards", "Use yards"),
    ("MILES", "Miles", "Use miles"),
]

_UNIT_SYSTEM_ITEMS = (
    ("METRIC", "Metric", "Metric units (millimeters, meters, etc.)"),
    ("IMPERIAL", "Imperial", "Imperial units (inches, feet, etc.)"),
    ("NONE", "None", "No units, adaptive display only"),
)


def _length_unit_items(system):
    if system == "IMPERIAL":
        return _LENGTH_UNITS_IMPERIAL
    if system == "METRIC":
        return _LENGTH_UNITS_METRIC
    return [("ADAPTIVE", "Adaptive", "Adapt to the view zoom level")]


def _default_length_unit(system):
    if system == "IMPERIAL":
        return "INCHES"
    if system == "METRIC":
        return "MILLIMETERS"
    return "ADAPTIVE"


def _unit_system_update(self, context):
    valid = {item[0] for item in _length_unit_items(self.unit_system)}
    if self.length_unit not in valid:
        self.length_unit = _default_length_unit(self.unit_system)


class NeoBIMWizardPreferences(AddonPreferences):
    bl_idname = __package__

    unit_system: EnumProperty(
        name="Unit System",
        description="Default unit system for new projects",
        items=_UNIT_SYSTEM_ITEMS,
        default="METRIC",
        update=_unit_system_update,
    )
    length_unit: EnumProperty(
        name="Length Unit",
        description="Default length unit for new projects",
        items=lambda self, context: _length_unit_items(self.unit_system),
        default=0,
    )
    setup_complete: BoolProperty(
        name="Setup Complete",
        description="Whether the first-run setup wizard has been completed",
        default=False,
    )

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        col = layout.column()
        col.prop(self, "unit_system")
        if self.unit_system != "NONE":
            col.prop(self, "length_unit")
        col.separator()
        col.label(text="Applied to every new project (File → New).", icon="INFO")


def _setup_json_path():
    return os.path.join(bpy.utils.user_resource("CONFIG"), "neobim_setup.json")


def _apply_setup_json_if_present():
    """Apply the wizard's JSON handoff once. Returns True when the file existed.

    The file is written by the native startup dialog. Reading it marks setup
    as complete and saves the preferences, so the wizard never re-appears.
    """
    path = _setup_json_path()
    if not os.path.exists(path):
        return False
    addon = bpy.context.preferences.addons.get(__package__)
    if addon is None:
        return False

    data = {}
    try:
        with open(path, "r") as f:
            data = json.load(f)
    except (OSError, ValueError):
        pass
    # The handoff is consumed regardless: a leftover or malformed file must
    # not block startup or nag again on the next launch.
    try:
        os.remove(path)
    except OSError:
        pass

    system = data.get("unit_system", "METRIC")
    valid_systems = {item[0] for item in _UNIT_SYSTEM_ITEMS}
    if system not in valid_systems:
        system = "METRIC"
    length = data.get("length_unit", _default_length_unit(system))
    valid_units = {item[0] for item in _length_unit_items(system)}
    if length not in valid_units:
        length = _default_length_unit(system)

    prefs = addon.preferences
    # `unit_system` first: `length_unit` is validated against the current
    # system, so it must be set before the unit-specific value.
    prefs.unit_system = system
    prefs.length_unit = length
    prefs.setup_complete = True

    # Startup and new-file loads read with an empty `bpy.data.filepath`, so a
    # project file opened on first run is left untouched.
    if not bpy.data.filepath:
        for scene in bpy.data.scenes:
            scene.unit_settings.system = system
            scene.unit_settings.length_unit = length
        try:
            bpy.ops.wm.save_homefile()
        except Exception:
            pass

    try:
        bpy.ops.wm.save_userpref()
    except Exception:
        pass

    return True


@persistent
def _apply_unit_preferences_to_new_scene(*_args):
    """Apply the stored unit defaults to startup and `File → New` scenes.

    Startup and new-file loads read with an empty `bpy.data.filepath`, so this
    leaves already-saved project files untouched.
    """
    if bpy.data.filepath or bpy.context.preferences is None:
        return
    _apply_setup_json_if_present()
    addon = bpy.context.preferences.addons.get(__package__)
    if addon is None or not addon.preferences.setup_complete:
        return
    prefs = addon.preferences
    # At startup `load_post` fires before the window context is established
    # (the startup scene would otherwise keep the stale units from the
    # startup file), so apply to every freshly loaded scene instead of
    # `bpy.context.scene`. Startup and new-file loads have exactly one scene.
    for scene in bpy.data.scenes:
        scene.unit_settings.system = prefs.unit_system
        scene.unit_settings.length_unit = prefs.length_unit


def _first_run_timer():
    """One-shot check for the wizard's JSON handoff, right after startup."""
    _apply_setup_json_if_present()
    return None


classes = (NeoBIMWizardPreferences,)

_first_run_timer_handle = None


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.app.handlers.load_post.append(_apply_unit_preferences_to_new_scene)
    global _first_run_timer_handle
    _first_run_timer_handle = bpy.app.timers.register(
        _first_run_timer, first_interval=0.5
    )


def unregister():
    global _first_run_timer_handle
    if _first_run_timer_handle is not None:
        bpy.app.timers.unregister(_first_run_timer_handle)
        _first_run_timer_handle = None
    bpy.app.handlers.load_post.remove(_apply_unit_preferences_to_new_scene)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
