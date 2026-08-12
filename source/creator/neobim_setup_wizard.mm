#import <AppKit/AppKit.h>

#include "WM_api.hh"

@interface NeoBIMSetupWizardController : NSObject
@property(strong) NSPopUpButton *systemDropdown;
@end

@implementation NeoBIMSetupWizardController
- (void)updateSystemDropdown {
    [self.systemDropdown selectItemAtIndex:1];
}
@end

namespace blender {
namespace neobim {

SetupWizardResult setup_wizard_run(SetupWizardSelection &r_selection) {
    @autoreleasepool {
        NeoBIMSetupWizardController *controller = [[NeoBIMSetupWizardController alloc] init];

        NSAlert *alert = [[NSAlert alloc] init];
        alert.messageText = @"Welcome to NeoBIM";
        alert.informativeText = @"Choose the default unit system for your workspace.\n"
            @"You can change this later in the NeoBIM preferences "
            @"or Scene Properties.\nIt will be applied to every new project.";

        NSButton *continue_button = [alert addButtonWithTitle:@"Continue"];
        continue_button.keyEquivalent = @"\r";

        NSButton *quit_button = [alert addButtonWithTitle:@"Quit NeoBIM"];
        quit_button.keyEquivalent = @"\e";

        NSView *accessory = [[NSView alloc] initWithFrame:NSMakeRect(0, 0, 380, 96)];

        NSTextField *system_label = [NSTextField labelWithString:@"Unit System"];
        system_label.frame = NSMakeRect(0, 62, 110, 16);
        system_label.alignment = NSTextAlignmentRight;

        NSPopUpButton *system_dropdown = [[NSPopUpButton alloc] initWithFrame:NSMakeRect(120, 56, 260, 26)
            pullsDown:NO];
        [system_dropdown addItemsWithTitles:@[@"None", @"Metric", @"Imperial"]];
        system_dropdown.target = controller;
        controller.systemDropdown = system_dropdown;
        [controller updateSystemDropdown];

        [accessory addSubview:system_label];
        [accessory addSubview:system_dropdown];
        alert.accessoryView = accessory;

        const NSModalResponse response = [alert runModal];
        if (response == NSAlertSecondButtonReturn) {
            return SetupWizardResult::kSetupExit;
        }

        static const char *systemDropdownKeys[3] = {"NONE", "METRIC", "IMPERIAL"};
        NSInteger index = [system_dropdown indexOfSelectedItem];
        r_selection.unit_system = systemDropdownKeys[index];

        return SetupWizardResult::kSetupComplete;
    }
}

} // namespace neobim
} // namespace blender
