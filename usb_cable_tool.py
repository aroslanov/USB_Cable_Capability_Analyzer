import tkinter as tk
from tkinter import ttk

"""
USB Cable Checker GUI — Extended Analysis Edition

Mirrors the physical USB-C cable checker board.
User checks LEDs that are ON; software infers wiring, capabilities,
and assigns an auto-classification label.

This is a *diagnostic* tool, not a USB-IF compliance certifier.
"""

LEFT_PINS = [
    "GND", "TX2+", "TX2-", "VBUS", "CC2", "D+", "D-", "SBU2", "VBUS", "RX1-", "RX1+", "GND"
]

RIGHT_PINS = [
    "GND", "RX2+", "RX2-", "VBUS", "SBU1", "D-", "D+", "CC1", "VBUS", "TX1-", "TX1+", "GND"
]

SS_PINS = {
    "TX1+", "TX1-", "RX1+", "RX1-",
    "TX2+", "TX2-", "RX2+", "RX2-",
}

# Define SuperSpeed lanes
LANE_1 = {"TX1+", "TX1-", "RX1+", "RX1-"}
LANE_2 = {"TX2+", "TX2-", "RX2+", "RX2-"}

PIN_TOOLTIPS = {
    "GND": "Ground pin for power and signal return",
    "TX2+": "Transmit positive for USB 3.x SuperSpeed lane 2",
    "TX2-": "Transmit negative for USB 3.x SuperSpeed lane 2",
    "VBUS": "Power supply pin (5V, 9V, 15V, 20V)",
    "CC2": "Configuration Channel 2 for cable detection and power negotiation",
    "D+": "USB 2.0 data positive",
    "D-": "USB 2.0 data negative",
    "SBU2": "Sideband Use 2 for alternate modes (e.g., DisplayPort)",
    "RX1-": "Receive negative for USB 3.x SuperSpeed lane 1",
    "RX1+": "Receive positive for USB 3.x SuperSpeed lane 1",
    "RX2+": "Receive positive for USB 3.x SuperSpeed lane 2",
    "RX2-": "Receive negative for USB 3.x SuperSpeed lane 2",
    "SBU1": "Sideband Use 1 for alternate modes (e.g., DisplayPort)",
    "CC1": "Configuration Channel 1 for cable detection and power negotiation",
    "TX1-": "Transmit negative for USB 3.x SuperSpeed lane 1",
    "TX1+": "Transmit positive for USB 3.x SuperSpeed lane 1",
}


def analyze_cable(
    active_pins: set[str],
    pin_counts: dict[str, int] | None = None,
    left_connector: str | None = None,
    right_connector: str | None = None,
    left_pins_checked: set[str] | None = None,
    right_pins_checked: set[str] | None = None,
) -> str:
    """
    Standalone cable analysis function.
    
    Analyzes active pins and generates a detailed diagnostic report including:
    - User-friendly cable classification
    - Capability detection (USB 2.0, SuperSpeed, Power, etc.)
    - Lane-level status reporting
    - Broken pair detection
    - Technical details for advanced users
    
    Args:
        active_pins: Set of pin names that are active/connected
        pin_counts: Optional pin occurrence counts for multi-pin signals
        left_connector: Selected connector type for left side
        right_connector: Selected connector type for right side
        left_pins_checked: Physical pins checked on left side (board labels)
        right_pins_checked: Physical pins checked on right side (board labels)
        
    Returns:
        A formatted string with the detailed analysis report
    """
    report = []
    
    # --- Feature Detection ---
    usb2 = {"D+", "D-"}.issubset(active_pins)
    usb2_partial = len({"D+", "D-"} & active_pins) == 1

    pin_counts = pin_counts or {}
    vbus_count = pin_counts.get("VBUS", 0)
    gnd_count = pin_counts.get("GND", 0)
    
    # SuperSpeed Lane Analysis
    lane1_pins = LANE_1 & active_pins
    lane2_pins = LANE_2 & active_pins
    
    lane1_complete = len(lane1_pins) == 4
    lane2_complete = len(lane2_pins) == 4
    ss_count = len(SS_PINS & active_pins)
    full_ss = ss_count == 8
    partial_ss = 0 < ss_count < 8
    
    # CC and SBU detection
    cc_count = len({"CC1", "CC2"} & active_pins)
    cc_present = cc_count > 0
    sbu_count = len({"SBU1", "SBU2"} & active_pins)

    # Cable profile based on connector selection
    left_connector = left_connector or ""
    right_connector = right_connector or ""

    left_is_usb_c = "Type C" in left_connector
    right_is_usb_c = "Type C" in right_connector
    usb_c_any = left_is_usb_c or right_is_usb_c
    usb_c_both = left_is_usb_c and right_is_usb_c

    left_is_usb3 = "3.0" in left_connector
    right_is_usb3 = "3.0" in right_connector
    usb3_any = left_is_usb3 or right_is_usb3
    usb2_only = not usb3_any

    legacy_usb2_candidate = usb2 and usb2_only and not usb_c_any
    legacy_usb3_candidate = usb2 and usb3_any and not usb_c_any
    full_usb_c_candidate = usb_c_both and left_is_usb3 and right_is_usb3

    expected_ss_pins = 8 if full_usb_c_candidate else (4 if usb3_any else 0)
    mismatch_ss = (expected_ss_pins == 0 and ss_count > 0) or (expected_ss_pins > 0 and ss_count > expected_ss_pins)
    # Legacy USB 3.0 connectors (non-USB-C) should only use Lane 1 (TX1/RX1)
    if usb3_any and not usb_c_any:
        lane2_present = len(LANE_2 & active_pins) > 0
        if lane2_present:
            mismatch_ss = True

    # Power expectations vary by connector selection
    if full_usb_c_candidate:
        power_full = vbus_count >= 2 and gnd_count >= 4
    else:
        power_full = vbus_count >= 1 and gnd_count >= 1

    power_partial = (vbus_count > 0 or gnd_count > 0) and not power_full
    power = power_full
    
    # Detect broken pairs / critical wiring issues vs non-critical warnings
    broken_pairs = []
    wiring_warnings = []
    if expected_ss_pins > 0:
        for lane_name, lane_pins in [("Lane 1", LANE_1), ("Lane 2", LANE_2)]:
            tx_pins = {p for p in lane_pins if p.startswith("TX")}
            rx_pins = {p for p in lane_pins if p.startswith("RX")}
            
            tx_active = tx_pins & active_pins
            rx_active = rx_pins & active_pins
            
            if len(tx_active) == 1:
                broken_pairs.append(f"{lane_name} TX pair broken")
            if len(rx_active) == 1:
                broken_pairs.append(f"{lane_name} RX pair broken")

    if usb2_partial:
        broken_pairs.append("USB 2.0 D+/D- pair broken")

    if power_partial:
        broken_pairs.append("Power wiring incomplete (VBUS/GND)")

    if usb_c_any and cc_count == 0:
        broken_pairs.append("CC wiring missing (USB-C selected)")
    elif full_usb_c_candidate and cc_count == 1:
        wiring_warnings.append("CC wiring incomplete (USB-C)")
    
    # === USER-FRIENDLY CLASSIFICATION ===
    # Classification is based strictly on AVAILABLE PINS, not assumptions
    orientation_note = ""
    
    single_lane_ss = (lane1_complete ^ lane2_complete) and ss_count == 4

    # Determine cable type based on actual pin presence
    if broken_pairs:
        cable_type = "DAMAGED CABLE - Broken wiring detected"
        cable_note = "This cable has broken or missing connections. Do not use for data transfer."
    elif mismatch_ss:
        cable_type = "Mismatch: Connector selection vs detected wiring"
        cable_note = "Selected connectors do not match detected SuperSpeed wiring."
    elif full_ss and sbu_count == 2 and usb2 and cc_present:
        # All features present: full SuperSpeed + Alt-Mode + USB 2.0 + Config channel
        cable_type = "Premium USB-C Cable (Full Featured)"
        cable_note = "Supports high-speed data, Alt-Mode (video/display output), and advanced features."
        if (lane1_complete and not lane2_complete) or (lane2_complete and not lane1_complete):
            orientation_note = "Works in one orientation only"
    elif full_ss and usb2 and cc_present:
        # Full SuperSpeed with USB 2.0 (regardless of Alt-Mode)
        cable_type = "USB 3.x Fast Data Cable"
        cable_note = "Supports high-speed data transfer. Good for modern devices."
        if (lane1_complete and not lane2_complete) or (lane2_complete and not lane1_complete):
            orientation_note = "Works in one orientation only"
    elif usb2 and single_lane_ss:
        cable_type = "USB 3.x Data Cable (Single-Lane)"
        if legacy_usb3_candidate:
            cable_note = "Single SuperSpeed lane detected (legacy USB 3.0 connectors)."
        else:
            cable_note = "Single SuperSpeed lane detected (common in USB-A/B to USB-C cables)."
            orientation_note = "Works in one orientation only"
    elif usb2 and not full_ss and not partial_ss:
        # USB 2.0 data only, no SuperSpeed pins
        cable_type = "USB 2.0 Data Cable"
        if legacy_usb2_candidate:
            cable_note = "Legacy USB 2.0 wiring detected (USB-A/B/Micro/Mini/Lightning)."
        else:
            cable_note = "Good for basic data transfer, charging, and older devices."
    elif power and not usb2 and ss_count == 0:
        # Power and ground only, no data or SuperSpeed
        cable_type = "Charging Cable"
        cable_note = "Supports power delivery only. Not suitable for data transfer."
    elif power_partial and not usb2 and ss_count == 0:
        cable_type = "Charging Cable (Incomplete Power Wiring)"
        cable_note = "Power wiring is incomplete. Charging may be unstable or unsafe."
    elif usb2 and partial_ss:
        # USB 2.0 with incomplete SuperSpeed (damaged pins)
        cable_type = "NON-STANDARD Cable"
        cable_note = "Has incomplete or damaged SuperSpeed connections. May work but not recommended."
        if (lane1_complete and not lane2_complete) or (lane2_complete and not lane1_complete):
            orientation_note = "Works in one orientation only"
    else:
        cable_type = "Unknown Cable"
        cable_note = "Unable to determine cable type. May be defective."
    
    # Build the report with user-friendly format
    report.append(f"{cable_type}")
    report.append(f"{cable_note}")
    if left_connector or right_connector:
        report.append(f"Selected connectors: {left_connector or 'Unknown'} ↔ {right_connector or 'Unknown'}")
    
    if orientation_note:
        report.append(f"Note: {orientation_note}")
    
    # === TECHNICAL DETAILS ===
    report.append(f"\nCapabilities:")
    report.append(f"  • USB 2.0 data: {'Yes' if usb2 else ('Partial' if usb2_partial else 'No')}")
    report.append(f"  • Power delivery: {'Yes' if power else ('Partial' if power_partial else 'No')}")
    report.append(f"  • SuperSpeed (USB 3.x): {'Yes' if full_ss else ('Partial' if partial_ss else 'No')} (expected {expected_ss_pins}/8 pins)")
    report.append(f"  • Alt-Mode wiring (SBU): {'Yes' if sbu_count == 2 else ('Partial' if sbu_count == 1 else 'No')} (not a guarantee of Alt-Mode)"
    )
    
    report.append(f"\nSuperSpeed Lanes ({ss_count}/8 pins detected):")
    if lane1_complete:
        report.append("  • Lane 1 (TX1/RX1): OK")
    elif len(lane1_pins) > 0:
        report.append(f"  • Lane 1 (TX1/RX1): INCOMPLETE ({len(lane1_pins)}/4 pins)")
    else:
        report.append("  • Lane 1 (TX1/RX1): MISSING")
    
    if lane2_complete:
        report.append("  • Lane 2 (TX2/RX2): OK")
    elif len(lane2_pins) > 0:
        report.append(f"  • Lane 2 (TX2/RX2): INCOMPLETE ({len(lane2_pins)}/4 pins)")
    else:
        report.append("  • Lane 2 (TX2/RX2): MISSING")
    
    # Report broken pairs
    if broken_pairs:
        report.append(f"\nBroken Differential Pairs:")
        for bp in broken_pairs:
            report.append(f"  • {bp}")

    if wiring_warnings:
        report.append(f"\nWiring Warnings:")
        for warning in wiring_warnings:
            report.append(f"  • {warning}")
    
    report.append(f"\nConfiguration:")
    report.append(f"  • CC (Config Channel): {'Yes' if cc_count == 2 else ('Partial' if cc_count == 1 else 'No')}")
    report.append(f"  • SBU (Sideband): {sbu_count}/2 lines")
    
    if left_pins_checked or right_pins_checked:
        report.append(f"\nChecked Pins:")
        if left_pins_checked:
            left_str = ", ".join(sorted(left_pins_checked, key=lambda p: int(p.split()[0]) if p.split()[0].isdigit() else 999))
            report.append(f"  Left (Row B): {left_str}")
        if right_pins_checked:
            right_str = ", ".join(sorted(right_pins_checked, key=lambda p: int(p.split()[0]) if p.split()[0].isdigit() else 999))
            report.append(f"  Right (Row A): {right_str}")
    
    return "\n".join(report)


class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, event):
        if self.tooltip:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tooltip, text=self.text, background="yellow", relief="solid", borderwidth=1)
        label.pack()

    def hide(self, event):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class USBCableChecker(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("USB Cable Capability Analyzer")
        self.geometry("450x700")
        self.vars = {}
        self.left_connector_var = tk.StringVar(value="Type C 3.0")
        self.right_connector_var = tk.StringVar(value="Type C 3.0")
        self._suppress_update = False
        self.report_text: tk.Text | None = None
        self._build_ui()

    def _build_ui(self):
        main = ttk.Frame(self, padding=10)
        main.pack(fill="both", expand=True)

        left_selector = ttk.LabelFrame(main, text="Left Connector")
        left = ttk.LabelFrame(main, text="Pin Row B (Left)")
        right = ttk.LabelFrame(main, text="Pin Row A (Right)")
        right_selector = ttk.LabelFrame(main, text="Right Connector")

        left_selector.grid(row=0, column=0, padx=(0, 6), sticky="n")
        left.grid(row=0, column=1, padx=(0, 10), sticky="n")
        right.grid(row=0, column=2, padx=(10, 0), sticky="n")
        right_selector.grid(row=0, column=3, padx=(6, 0), sticky="n")

        main.grid_columnconfigure(0, weight=0)
        main.grid_columnconfigure(1, weight=1)
        main.grid_columnconfigure(2, weight=1)
        main.grid_columnconfigure(3, weight=0)

        self.left_connector_var.trace_add("write", lambda *_: self._update_report())
        self.right_connector_var.trace_add("write", lambda *_: self._update_report())

        for label in ["Type A 3.0", "Type A 2.0", "Type C 3.0"]:
            ttk.Radiobutton(
                left_selector,
                text=label,
                value=label,
                variable=self.left_connector_var,
            ).pack(anchor="w")

        for label in [
            "a. Type B 3.0",
            "b. Type C 3.0",
            "c. Micro B 3.0",
            "d. Mini B 2.0",
            "e. Lightning",
            "f. Micro B 2.0",
        ]:
            ttk.Radiobutton(
                right_selector,
                text=label,
                value=label.replace("a. ", "").replace("b. ", "").replace("c. ", "").replace("d. ", "").replace("e. ", "").replace("f. ", ""),
                variable=self.right_connector_var,
            ).pack(anchor="w")

        for i, pin in enumerate(LEFT_PINS):
            var = tk.BooleanVar()
            var.trace_add("write", lambda *_: self._update_report())
            checkbutton = ttk.Checkbutton(left, text=f"{i+1:02d}  {pin}", variable=var)
            checkbutton.pack(anchor="w")
            self.vars[f"{pin}_{i}"] = var
            Tooltip(checkbutton, PIN_TOOLTIPS[pin])

        for i, pin in enumerate(RIGHT_PINS):
            var = tk.BooleanVar()
            var.trace_add("write", lambda *_: self._update_report())
            checkbutton = ttk.Checkbutton(right, text=f"{i+1:02d}  {pin}", variable=var)
            checkbutton.pack(anchor="w")
            self.vars[f"{pin}_{i+20}"] = var
            Tooltip(checkbutton, PIN_TOOLTIPS[pin])

        controls = ttk.Frame(main)
        controls.grid(row=1, column=0, columnspan=4, pady=(10, 0), sticky="ew")

        button_frame = ttk.Frame(controls)
        button_frame.pack(expand=True, anchor="center")

        ttk.Button(button_frame, text="Select All", command=lambda: self._set_all(True)).pack(side="left")
        ttk.Button(button_frame, text="Unselect All", command=lambda: self._set_all(False)).pack(side="left", padx=(8, 0))
        ttk.Button(button_frame, text="Copy to Clipboard", command=self._copy_to_clipboard).pack(side="left", padx=(8, 0))

        report_frame = ttk.LabelFrame(main, text="Live Analysis")
        report_frame.grid(row=2, column=0, columnspan=4, sticky="nsew", padx=10, pady=(15, 0))
        main.grid_rowconfigure(2, weight=1)

        # Create scrollbar for report text
        scrollbar = ttk.Scrollbar(report_frame)
        scrollbar.pack(side="right", fill="y")

        self.report_text = tk.Text(
            report_frame,
            wrap="word",
            height=12,
            borderwidth=0,
            highlightthickness=0,
            yscrollcommand=scrollbar.set,
        )
        self.report_text.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.config(command=self.report_text.yview)

        self._update_report()

    def _set_all(self, value: bool):
        self._suppress_update = True
        try:
            for var in self.vars.values():
                var.set(value)
        finally:
            self._suppress_update = False

        self._update_report()

    def _set_report_text(self, text: str):
        if self.report_text is None:
            return

        self.report_text.configure(state="normal")
        self.report_text.delete("1.0", "end")
        self.report_text.insert("1.0", text)
        self.report_text.configure(state="disabled")

    def _copy_to_clipboard(self):
        if self.report_text:
            text = self.report_text.get("1.0", "end-1c")
            self.clipboard_clear()
            self.clipboard_append(text)

    def _active_pins(self):
        active_pins = set()
        pin_counts: dict[str, int] = {}
        left_pins_checked = set()
        right_pins_checked = set()
        
        # TRANSFORMATION LAYER:
        # Maps the Board's specific silk-screen labels (Right Side) 
        # to the Standard USB Logical Signals required by analyze_cable().
        # This fixes the logic error without changing the GUI layout.
        right_side_translation = {
            "RX2+": "TX1+",  # Pin 2: Board labeled RX2+, physically TX1+
            "RX2-": "TX1-",  # Pin 3: Board labeled RX2-, physically TX1-
            "D-":   "D+",    # Pin 6: Board labeled D-, physically D+ location
            "D+":   "D-",    # Pin 7: Board labeled D+, physically D- location
            "TX1-": "RX2-",  # Pin 10: Board labeled TX1-, physically RX2-
            "TX1+": "RX2+"   # Pin 11: Board labeled TX1+, physically RX2+
        }

        for key, var in self.vars.items():
            if var.get():
                parts = key.split("_")
                pin_label = parts[0]
                pin_index = int(parts[1])

                # Check if this pin is on the Right Side (Indices 20-31)
                if pin_index >= 20:
                    # Translate board label to logical signal name
                    logical_name = right_side_translation.get(pin_label, pin_label)
                    active_pins.add(logical_name)
                    pin_counts[logical_name] = pin_counts.get(logical_name, 0) + 1
                    right_pins_checked.add(f"{pin_index - 19:02d} {pin_label}")
                else:
                    # Left Side pins (0-11) match standard layout; no change needed
                    active_pins.add(pin_label)
                    pin_counts[pin_label] = pin_counts.get(pin_label, 0) + 1
                    left_pins_checked.add(f"{pin_index + 1:02d} {pin_label}")
                    
        return active_pins, pin_counts, left_pins_checked, right_pins_checked

    def _build_report_text(
        self,
        active_pins: set[str],
        pin_counts: dict[str, int],
        left_pins_checked: set[str],
        right_pins_checked: set[str],
    ) -> str:
        """
        Builds the report text by delegating to the standalone analyze_cable function.
        
        Args:
            active_pins: Set of pin names that are active/connected
            pin_counts: Pin occurrence counts for multi-pin signals
            left_pins_checked: Physical pins checked on left side
            right_pins_checked: Physical pins checked on right side
            
        Returns:
            Formatted analysis report
        """
        return analyze_cable(
            active_pins,
            pin_counts,
            self.left_connector_var.get(),
            self.right_connector_var.get(),
            left_pins_checked,
            right_pins_checked,
        )

    def _update_report(self):
        if self._suppress_update:
            return

        active_pins, pin_counts, left_pins_checked, right_pins_checked = self._active_pins()
        self._set_report_text(
            self._build_report_text(
                active_pins, pin_counts, left_pins_checked, right_pins_checked
            )
        )


if __name__ == "__main__":
    USBCableChecker().mainloop()
