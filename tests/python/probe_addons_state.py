# Script to inspect the add-ons state on application start

# Run with a completed build
# build_darwin/bin/Blender.app/Contents/MacOS/Blender \
# --background \     ## headless (no GUI)
# --factory-startup \  ## ignores existing preferences
# --python tests/python/probe_addons_state.py

import addon_utils

def print_state(mod_name):
    is_enabled, is_loaded = addon_utils.check(mod_name)
    print(f"{mod_name}: enabled={is_enabled}, loaded={is_loaded}")

def list_all_addons():
    print("\nAll add-ons discovered by addon_utils.modules():")
    for mod in addon_utils.modules():
        print_state(mod.__name__)

def main():
    list_all_addons()

if __name__ == "__main__":
    main()

