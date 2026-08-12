#import <AppKit/AppKit.h>
#include <cstdio>

#include "WM_api.hh"

@interface NeoBIMSetupWizardController : NSObject
@property(strong) NSPopUpButton *systemDropdown;
@property(strong) NSPopUpButton *lengthDropdown;
- (void)systemChanged:(id)sender;
@end

@implementation NeoBIMSetupWizardController
- (void)updateSystemDropdown {
    [self.lengthDropdown removeAllItems];
    switch (self.systemDropdown.indexOfSelectedItem) {
        case 0:
            [self.lengthDropdown addItemWithTitle:@"Adaptive"];
            break;
        case 1:
            [self.lengthDropdown addItemsWithTitles:@[
                @"Adaptive",
                @"Kilometers",
                @"Meters",
                @"Centimeters",
                @"Millimeters",
                @"Micrometers",
            ]];
            [self.lengthDropdown selectItemAtIndex:4];
            break;
        case 2:
            [self.lengthDropdown addItemsWithTitles:@[
                @"Adaptive",
                @"Miles",
                @"Feet",
                @"Inches",
                @"Thou",
            ]];
            [self.lengthDropdown selectItemAtIndex:2];
            break;
    }
}
- (void)systemChanged:(id)sender {
    (void)sender;
    [self updateSystemDropdown];
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
        [system_dropdown selectItemAtIndex:1];
        system_dropdown.target = controller;
        system_dropdown.action = @selector(systemChanged:);
        controller.systemDropdown = system_dropdown;

        NSTextField *length_label = [NSTextField labelWithString:@"Length Unit"];
        length_label.frame = NSMakeRect(0, 26, 110, 16);
        length_label.alignment = NSTextAlignmentRight;

        NSPopUpButton *length_dropdown = [[NSPopUpButton alloc] initWithFrame:NSMakeRect(120, 20, 260, 26)
            pullsDown:NO];
        [length_dropdown addItemsWithTitles:@[
            @"Adaptive",
            @"Kilometers",
            @"Meters",
            @"Centimeters",
            @"Millimeters",
            @"Micrometers",
        ]];
        [length_dropdown selectItemAtIndex:4];

        controller.lengthDropdown = length_dropdown;

        [accessory addSubview:system_label];
        [accessory addSubview:system_dropdown];
        [accessory addSubview:length_label];
        [accessory addSubview:length_dropdown];
        alert.accessoryView = accessory;

        const NSModalResponse response = [alert runModal];
        if (response == NSAlertSecondButtonReturn) {
            return SetupWizardResult::kSetupExit;
        }

        r_selection.unit_system = system_dropdown.titleOfSelectedItem.uppercaseString.UTF8String;
        r_selection.length_unit = length_dropdown.titleOfSelectedItem.uppercaseString.UTF8String;

        return SetupWizardResult::kSetupComplete;
    }
}

} // namespace neobim
} // namespace blender
