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
        self.geometry("350x540")
        self.vars = {}
        self._suppress_update = False
        self.report_text: tk.Text | None = None
        self._build_ui()

    def _build_ui(self):
        main = ttk.Frame(self, padding=10)
        main.pack(fill="both", expand=True)

        left = ttk.LabelFrame(main, text="Pin Row B (Left)")
        right = ttk.LabelFrame(main, text="Pin Row A (Right)")

        left.grid(row=0, column=0, padx=10, sticky="n")
        right.grid(row=0, column=1, padx=10, sticky="n")

        main.grid_columnconfigure(0, weight=1)
        main.grid_columnconfigure(1, weight=1)

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
        controls.grid(row=1, column=0, columnspan=2, pady=(10, 0), sticky="ew")

        button_frame = ttk.Frame(controls)
        button_frame.pack(expand=True, anchor="center")

        ttk.Button(button_frame, text="Select All", command=lambda: self._set_all(True)).pack(side="left")
        ttk.Button(button_frame, text="Unselect All", command=lambda: self._set_all(False)).pack(side="left", padx=(8, 0))
        ttk.Button(button_frame, text="Copy to Clipboard", command=self._copy_to_clipboard).pack(side="left", padx=(8, 0))

        report_frame = ttk.LabelFrame(main, text="Live Analysis")
        report_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=(15, 0))
        main.grid_rowconfigure(2, weight=1)

        self.report_text = tk.Text(
            report_frame,
            wrap="word",
            height=12,
            borderwidth=0,
            highlightthickness=0,
        )
        self.report_text.pack(fill="both", expand=True, padx=10, pady=10)

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
        for key, var in self.vars.items():
            if var.get():
                active_pins.add(key.split("_")[0])
        return active_pins

    def _build_report_text(self, active_pins: set[str]) -> str:
        report = []
        label = ""

        # --- USB 2.0 ---
        usb2 = {"D+", "D-"}.issubset(active_pins)
        report.append(f"USB 2.0 Data: {'YES' if usb2 else 'NO'}")

        # --- SuperSpeed ---
        ss_count = len(SS_PINS & active_pins)
        full_ss = ss_count == 8
        partial_ss = 0 < ss_count < 8

        report.append(f"SuperSpeed lanes detected: {ss_count}/8")
        if full_ss:
            report.append("Full USB 3.x wiring present")
        elif partial_ss:
            report.append("Partial SuperSpeed wiring (likely passive or damaged cable)")
        else:
            report.append("No SuperSpeed wiring")

        # --- CC lines ---
        cc_present = bool({"CC1", "CC2"} & active_pins)
        report.append(f"CC lines present: {'YES' if cc_present else 'NO'}")

        # --- SBU lines ---
        sbu_count = len({"SBU1", "SBU2"} & active_pins)
        report.append(f"SBU lines detected: {sbu_count}/2")

        # --- Power ---
        power = {"VBUS", "GND"}.issubset(active_pins)
        report.append(f"Power path (VBUS+GND): {'YES' if power else 'NO'}")

        # === AUTO CLASSIFICATION ===
        orientation_issue = False
        if {"TX1+", "TX1-", "RX1+", "RX1-"}.issubset(active_pins) ^ {"TX2+", "TX2-", "RX2+", "RX2-"}.issubset(active_pins):
            orientation_issue = True

        if power and not usb2 and ss_count == 0:
            label = "Charge-only USB-C cable"
        elif usb2 and not full_ss:
            label = "USB 2.0 data cable"
        elif full_ss and sbu_count == 0:
            label = "USB-C 3.x full-featured cable (no Alt-Mode)"
        elif full_ss and sbu_count == 2:
            label = "Full-featured USB-C cable (Alt-Mode capable)"
        elif partial_ss:
            label = "Non-standard / damaged SuperSpeed cable"
        else:
            label = "Unknown or non-compliant cable"

        if orientation_issue:
            label += " — orientation dependent"

        report.insert(0, f"AUTO CLASSIFICATION: {label}")
        report.insert(1, "" + "-" * 40)

        return "\n".join(report)

    def _update_report(self):
        if self._suppress_update:
            return

        active_pins = self._active_pins()
        self._set_report_text(self._build_report_text(active_pins))


if __name__ == "__main__":
    USBCableChecker().mainloop()
