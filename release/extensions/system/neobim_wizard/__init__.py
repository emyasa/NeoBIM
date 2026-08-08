# SPDX-FileCopyrightText: 2026 NeoBIM Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""First-run unit system setup wizard for NeoBIM.

Shown once, before the user is exposed to the full application, so the
unit system is in place from the very start. The chosen values are saved
to user preferences and applied to the startup scene, which means every
new project created afterwards inherits them.
"""

import bpy
from bpy.props import BoolProperty, EnumProperty
from bpy.types import AddonPreferences, Operator

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


class NEOBIM_OT_first_run_wizard(Operator):
    bl_idname = "neobim.first_run_wizard"
    bl_label = "NeoBIM Setup"
    bl_description = "Set up the default unit system for NeoBIM"

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

    # Set only by the deferred re-invocation from the startup timer. When the
    # wizard is invoked directly by the C startup hook the dialog is scheduled
    # a short moment later instead, so the popup is created after the initial
    # window-manager notifiers have been processed (those remove all popups).
    from_timer: BoolProperty(default=False, options={"HIDDEN"})

    def invoke(self, context, event):
        import sys
        print("WZ invoke from_timer=%s" % self.from_timer, file=sys.stderr, flush=True)
        if not self.from_timer:
            bpy.app.timers.register(
                lambda: bpy.ops.neobim.first_run_wizard(
                    "INVOKE_DEFAULT", from_timer=True
                ),
                first_interval=0.5,
            )
            import sys
            print("WZ deferred timer registered", file=sys.stderr, flush=True)
            return {"CANCELLED"}

        scene = context.scene
        import sys
        print("WZ showing dialog", file=sys.stderr, flush=True)
        if scene is not None:
            # Seed from the current startup scene. `unit_system` is set first so
            # the update callback resets `length_unit` to a valid value for the
            # chosen system, then the scene's actual length unit is applied (it
            # is guaranteed valid for the scene's own unit system).
            self.unit_system = scene.unit_settings.system
            self.length_unit = scene.unit_settings.length_unit
        else:
            self.unit_system = "METRIC"
            self.length_unit = _default_length_unit(self.unit_system)
        return context.window_manager.invoke_props_dialog(self, width=380)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        col = layout.column()
        col.label(text="Welcome to NeoBIM", icon="WORKSPACE")
        col.separator()
        col.label(text="Choose the default unit system for your workspace.")
        col.label(text="You can change this at any time in Scene Properties.")
        col.separator()
        col.prop(self, "unit_system")
        if self.unit_system != "NONE":
            col.prop(self, "length_unit")
        col.separator()
        col.label(
            text="Saved to your preferences and applied to all new projects.",
            icon="INFO",
        )

    def execute(self, context):
        import sys
        print("WZ execute", file=sys.stderr, flush=True)
        prefs = self._preferences(context)
        # Set `length_unit` before `unit_system` so the update callback keeps it.
        prefs.length_unit = self.length_unit
        prefs.unit_system = self.unit_system
        prefs.setup_complete = True

        scene = context.scene
        if scene is not None:
            scene.unit_settings.system = self.unit_system
            scene.unit_settings.length_unit = self.length_unit

        self._save_preferences()
        self._save_startup_file()

        return {"FINISHED"}

    def cancel(self, context):
        import sys
        print("WZ cancel", file=sys.stderr, flush=True)
        # Skipping uses Blender's defaults, but still marks setup as done so
        # the wizard does not nag on every launch.
        self._preferences(context).setup_complete = True
        self._save_preferences()

    def _preferences(self, context):
        return context.preferences.addons[__package__].preferences

    def _save_preferences(self):
        try:
            bpy.ops.wm.save_userpref()
        except Exception:
            pass

    def _save_startup_file(self):
        try:
            bpy.ops.wm.save_homefile()
        except Exception:
            pass


classes = (NeoBIMWizardPreferences, NEOBIM_OT_first_run_wizard)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
