#import <AppKit/AppKit.h>
#include <cstdio>

#include "WM_api.hh"

namespace {

struct DropdownOption {
    const char *title;
    const char *value;
};

static constexpr DropdownOption kAreaOptions[] = {
    {"None", "NONE"},
    {"Square Nanometre", "NANO/SQUARE_METRE"},
    {"Square Micrometre", "MICRO/SQUARE_METRE"},
    {"Square Millimetre", "MILLI/SQUARE_METRE"},
    {"Square Decimetre", "DECI/SQUARE_METRE"},
    {"Square Centimetre", "CENTI/SQUARE_METRE"},
    {"Square Metre", "SQUARE_METRE"},
    {"Square Kilometre", "KILO/SQUARE_METRE"},
    {"Square Inch", "square inch"},
    {"Square Foot", "square foot"},
    {"Square Yard", "square yard"},
    {"Square Mile", "square mile"},
};

static constexpr DropdownOption kVolumeOptions[] = {
    {"None", "NONE"},
    {"Cubic Nanometre", "NANO/CUBIC_METRE"},
    {"Cubic Micrometre", "MICRO/CUBIC_METRE"},
    {"Cubic Millimetre", "MILLI/CUBIC_METRE"},
    {"Cubic Decimetre", "DECI/CUBIC_METRE"},
    {"Cubic Centimetre", "CENTI/CUBIC_METRE"},
    {"Cubic Metre", "CUBIC_METRE"},
    {"Cubic Kilometre", "KILO/CUBIC_METRE"},
    {"Cubic Inch", "cubic inch"},
    {"Cubic Foot", "cubic foot"},
    {"Cubic Yard", "cubic yard"},
};

} // namespace

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
            @"or Scene Properties.\n\nIt will be applied to the default project on application start.";

        NSButton *continue_button = [alert addButtonWithTitle:@"Continue"];
        continue_button.keyEquivalent = @"\r";

        NSButton *quit_button = [alert addButtonWithTitle:@"Quit NeoBIM"];
        quit_button.keyEquivalent = @"\e";

        NSView *accessory = [[NSView alloc] initWithFrame:NSMakeRect(0, 0, 380, 200)];

        NSTextField *system_label = [NSTextField labelWithString:@"Unit System"];
        system_label.frame = NSMakeRect(0, 144, 110, 16);
        system_label.alignment = NSTextAlignmentRight;

        NSPopUpButton *system_dropdown = [[NSPopUpButton alloc] initWithFrame:NSMakeRect(120, 136, 260, 26)
            pullsDown:NO];
        [system_dropdown addItemsWithTitles:@[@"None", @"Metric", @"Imperial"]];
        [system_dropdown selectItemAtIndex:1];
        system_dropdown.target = controller;
        system_dropdown.action = @selector(systemChanged:);
        controller.systemDropdown = system_dropdown;

        NSTextField *length_label = [NSTextField labelWithString:@"Length Unit"];
        length_label.frame = NSMakeRect(0, 108, 110, 16);
        length_label.alignment = NSTextAlignmentRight;

        NSPopUpButton *length_dropdown = [[NSPopUpButton alloc] initWithFrame:NSMakeRect(120, 100, 260, 26)
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

        NSTextField *area_label = [NSTextField labelWithString:@"Area Unit"];
        area_label.frame = NSMakeRect(0, 70, 110, 16);
        area_label.alignment = NSTextAlignmentRight;

        NSPopUpButton *area_dropdown = [[NSPopUpButton alloc] initWithFrame:NSMakeRect(120, 64, 260, 26)
            pullsDown:NO];
        for (const DropdownOption &option: kAreaOptions) {
            [area_dropdown addItemWithTitle: [NSString stringWithUTF8String:option.title]];
            area_dropdown.lastItem.representedObject = [NSString stringWithUTF8String:option.value];
        }
        [area_dropdown selectItemAtIndex:6];

        NSTextField *volume_label = [NSTextField labelWithString:@"Volume Unit"];
        volume_label.frame = NSMakeRect(0, 34, 110, 16);
        volume_label.alignment = NSTextAlignmentRight;

        NSPopUpButton *volume_dropdown = [[NSPopUpButton alloc] initWithFrame:NSMakeRect(120, 28, 260, 26)
            pullsDown:NO];
        for (const DropdownOption &option: kVolumeOptions) {
            [volume_dropdown addItemWithTitle: [NSString stringWithUTF8String:option.title]];
            volume_dropdown.lastItem.representedObject = [NSString stringWithUTF8String:option.value];
        }
        [volume_dropdown selectItemAtIndex:6];

        [accessory addSubview:system_label];
        [accessory addSubview:system_dropdown];
        [accessory addSubview:length_label];
        [accessory addSubview:length_dropdown];
        [accessory addSubview:area_label];
        [accessory addSubview:area_dropdown];
        [accessory addSubview:volume_label];
        [accessory addSubview:volume_dropdown];
        alert.accessoryView = accessory;

        const NSModalResponse response = [alert runModal];
        if (response == NSAlertSecondButtonReturn) {
            return SetupWizardResult::kSetupExit;
        }

        r_selection.unit_system = system_dropdown.titleOfSelectedItem.uppercaseString.UTF8String;
        r_selection.length_unit = length_dropdown.titleOfSelectedItem.uppercaseString.UTF8String;
        r_selection.area_unit = ((NSString *) area_dropdown.selectedItem.representedObject).UTF8String;
        r_selection.volume_unit = ((NSString *) volume_dropdown.selectedItem.representedObject).UTF8String;

        return SetupWizardResult::kSetupComplete;
    }
}

} // namespace neobim
} // namespace blender
