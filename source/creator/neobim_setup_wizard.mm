/* SPDX-FileCopyrightText: 2026 NeoBIM Authors
 *
 * SPDX-License-Identifier: GPL-2.0-or-later */

/** \file
 * \ingroup creator
 *
 * Native (AppKit) first-run setup wizard for NeoBIM.
 *
 * Shown on macOS before the main event loop starts and blocking: the user
 * cannot reach the application without either completing setup or quitting
 * (which exits the process, so the wizard is shown again on the next launch).
 * The chosen values are handed to the addon through a JSON file written by
 * the caller once setup has been completed.
 */

#include <cstddef>
#include <iterator>
#include <string>

#import <AppKit/AppKit.h>

#include "WM_api.hh"

namespace {
struct UnitOption {
  const char *title;
  const char *identifier;
};

static constexpr UnitOption kMetricOptions[] = {
    {"Adaptive", "ADAPTIVE"},
    {"Micrometers", "MICROMETERS"},
    {"Millimeters", "MILLIMETERS"},
    {"Centimeters", "CENTIMETERS"},
    {"Meters", "METERS"},
    {"Kilometers", "KILOMETERS"},
};

static constexpr UnitOption kImperialOptions[] = {
    {"Adaptive", "ADAPTIVE"},
    {"Thousandths of an Inch", "THOU"},
    {"Inches", "INCHES"},
    {"Feet", "FEET"},
    {"Yards", "YARDS"},
    {"Miles", "MILES"},
};
}  // namespace

/* NOTE: Objective-C declarations may only appear in global scope, so the
 * controller is defined here rather than in a namespace. */

@interface NeoBIMSetupWizardController : NSObject
@property(strong) NSPopUpButton *systemPopup;
@property(strong) NSPopUpButton *lengthPopup;
- (void)systemChanged:(id)sender;
@end

@implementation NeoBIMSetupWizardController

- (void)updateLengthUnits
{
  const UnitOption *options = kMetricOptions;
  size_t option_count = std::size(kMetricOptions);

  switch (self.systemPopup.indexOfSelectedItem) {
    case 1:
      options = kImperialOptions;
      option_count = std::size(kImperialOptions);
      break;
    case 2:
      options = nullptr;
      option_count = 0;
      break;
  }

  [self.lengthPopup removeAllItems];
  if (options == nullptr) {
    [self.lengthPopup addItemWithTitle:@"Adaptive"];
  }
  else {
    for (size_t i = 0; i < option_count; i++) {
      [self.lengthPopup addItemWithTitle:[NSString stringWithUTF8String:options[i].title]];
    }
  }

  /* Default to "Millimeters" / "Inches" when the full list is shown. */
  if (self.lengthPopup.numberOfItems > 2) {
    [self.lengthPopup selectItemAtIndex:2];
  }
  else {
    [self.lengthPopup selectItemAtIndex:0];
  }
}

- (void)systemChanged:(id)sender
{
  (void)sender;
  [self updateLengthUnits];
}

@end

namespace blender::neobim {

SetupWizardResult setup_wizard_run(SetupWizardSelection &r_selection)
{
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

    NSPopUpButton *system_popup = [[NSPopUpButton alloc] initWithFrame:NSMakeRect(120, 56, 260, 26)
                                                              pullsDown:NO];
    [system_popup addItemsWithTitles:@[@"Metric", @"Imperial", @"None"]];
    system_popup.target = controller;
    system_popup.action = @selector(systemChanged:);
    controller.systemPopup = system_popup;

    NSTextField *length_label = [NSTextField labelWithString:@"Length Unit"];
    length_label.frame = NSMakeRect(0, 26, 110, 16);
    length_label.alignment = NSTextAlignmentRight;

    NSPopUpButton *length_popup = [[NSPopUpButton alloc] initWithFrame:NSMakeRect(120, 20, 260, 26)
                                                              pullsDown:NO];
    controller.lengthPopup = length_popup;
    [controller updateLengthUnits];

    [accessory addSubview:system_label];
    [accessory addSubview:length_label];
    [accessory addSubview:system_popup];
    [accessory addSubview:length_popup];
    alert.accessoryView = accessory;

    const NSModalResponse response = [alert runModal];
    if (response == NSAlertSecondButtonReturn) {
      /* Quit without completing: no JSON handoff is written, so the wizard is
       * shown again on the next launch. */
      return SetupWizardResult::kSetupExit;
    }

    switch (system_popup.indexOfSelectedItem) {
      case 1:
        r_selection.unit_system = "IMPERIAL";
        break;
      case 2:
        r_selection.unit_system = "NONE";
        break;
      default:
        r_selection.unit_system = "METRIC";
        break;
    }

    if (r_selection.unit_system == "NONE") {
      r_selection.length_unit = "ADAPTIVE";
    }
    else {
      const UnitOption *options = (r_selection.unit_system == "IMPERIAL") ? kImperialOptions :
                                                                           kMetricOptions;
      const size_t option_count = (r_selection.unit_system == "IMPERIAL") ?
                                      std::size(kImperialOptions) :
                                      std::size(kMetricOptions);
      const NSInteger index = length_popup.indexOfSelectedItem;
      if (index >= 0 && size_t(index) < option_count) {
        r_selection.length_unit = options[index].identifier;
      }
      else {
        r_selection.length_unit = options[2].identifier;
      }
    }

    return SetupWizardResult::kSetupComplete;
  }
}

}  // namespace blender::neobim
