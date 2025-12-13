import tkinter as tk
from tkinter import ttk, messagebox

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

class USBCableChecker(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("USB Cable Capability Analyzer")
        self.geometry("780x540")
        self.vars = {}
        self._build_ui()

    def _build_ui(self):
        main = ttk.Frame(self, padding=10)
        main.pack(fill="both", expand=True)

        left = ttk.LabelFrame(main, text="Pin Row B (Left)")
        right = ttk.LabelFrame(main, text="Pin Row A (Right)")

        left.grid(row=0, column=0, padx=10, sticky="n")
        right.grid(row=0, column=1, padx=10, sticky="n")

        for i, pin in enumerate(LEFT_PINS):
            var = tk.BooleanVar()
            ttk.Checkbutton(left, text=f"{i+1:02d}  {pin}", variable=var).pack(anchor="w")
            self.vars[f"{pin}_{i}"] = var

        for i, pin in enumerate(RIGHT_PINS):
            var = tk.BooleanVar()
            ttk.Checkbutton(right, text=f"{i+1:02d}  {pin}", variable=var).pack(anchor="w")
            self.vars[f"{pin}_{i+20}"] = var

        ttk.Button(main, text="Analyze Cable", command=self.analyze).grid(
            row=1, column=0, columnspan=2, pady=15
        )

    def analyze(self):
        active_pins = set()
        for key, var in self.vars.items():
            if var.get():
                active_pins.add(key.split("_")[0])

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
            report.append("✔ Full USB 3.x wiring present")
        elif partial_ss:
            report.append("⚠ Partial SuperSpeed wiring (likely passive or damaged cable)")
        else:
            report.append("✖ No SuperSpeed wiring")

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

        messagebox.showinfo("Cable Analysis Report", "\n".join(report))


if __name__ == "__main__":
    USBCableChecker().mainloop()
