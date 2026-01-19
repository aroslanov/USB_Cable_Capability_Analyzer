# USB Cable Capability Analyzer

![Occkic MRB063A USB Cable Tester](assets/board.png)

A GUI tool to analyze USB-C cable wiring and capabilities based on pin connections.

## Description

This tool mimics the Occkic MRB063A USB Cable Tester board. Users select which pins are active (LEDs ON), and the software infers the cable's wiring, capabilities, and auto-classifies it.

**Note:** This is a diagnostic tool, not a USB-IF compliance certifier.

## Features

- **Real-time Analysis**: Live diagnostic updates as you interact with checkboxes.
- **Comprehensive Cable Support**: Analyzes USB 2.0, SuperSpeed (USB 3.x), CC lines, SBU lines, and power delivery.
- **Broken Pair Detection**: Explicitly identifies incomplete differential pairs (e.g., TX1+ without TX1-) and reports them as potential cable damage.
- **Lane-Level Reporting**: Independent status for each SuperSpeed lane (Lane 1 & Lane 2) with specific pin counts.
- **Detailed Diagnostics**:
  - Complete lane status (OK / INCOMPLETE / MISSING)
  - Broken differential pair identification
  - Orientation-dependent operation warnings
- **Auto-Classification**: Smart cable type identification with specific labels (charge-only, USB 2.0, USB 3.x, Alt-Mode capable, non-compliant).
- **Convenient Controls**: Select All / Unselect All buttons and Copy to Clipboard functionality.
- **User-Friendly UI**: Tooltips on all pin checkboxes explaining each pin's function.

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/aroslanov/USB_Cable_Capability_Analyzer
   cd USB_Cable_Capability_Analyzer
   ```

2. Ensure Python 3.6+ is installed (Tkinter is included in standard Python installations).

3. (Optional) Create a virtual environment:
   ```
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   ```

4. Run the application:

   - **Directly with Python:**
     ```
     python usb_cable_tool.py
     ```

   - **On Linux/macOS:**
     ```
     chmod +x run.sh  # Run this only once to make the script executable
     ./run.sh
     ```

   - **On Windows (Batch):**
     ```
     run.bat
     ```

   - **On Windows (PowerShell):**
     ```
     .\run.ps1
     ```

## Usage

- Launch the GUI.
- Check the boxes corresponding to the pins that are active (LEDs ON) on your Occkic MRB063A USB Cable Tester board.
- The analysis updates in real-time below the checkboxes.
- Use "Select All" to check all pins, "Unselect All" to clear them.
- Click "Copy to Clipboard" to copy the full report.
- Hover over checkboxes for tooltips explaining each pin.

## Analysis Details

### Broken Pair Detection
The tool detects incomplete differential pairs (both TX and RX pairs) for each SuperSpeed lane. If a differential pair is broken (one wire present, the other missing), it will report "BROKEN PAIRS DETECTED" with specific identification of which pairs are broken.

**Example**: If TX1+ is present but TX1- is missing, the tool reports "Lane 1 TX pair broken" and classifies the cable as non-compliant.

### Lane-Level Reporting
Each SuperSpeed lane is analyzed independently:
- **OK**: All 4 pins present (TX+, TX-, RX+, RX-)
- **INCOMPLETE**: Partial pins detected with count (e.g., 3/4 pins)
- **MISSING**: No pins from that lane detected

### Auto-Classification
The tool automatically classifies cables into categories:
- Charge-only USB-C cable
- USB 2.0 data cable
- USB-C 3.x cable (with or without Alt-Mode support)
- Non-standard / damaged SuperSpeed cable
- Non-compliant cable (when broken pairs detected)

Orientation warnings are provided for single-lane operation (flip-dependent).

## Requirements

- Python 3.6 or higher
- Tkinter (included with Python)

## Screenshot

![Program Screenshot](assets/screenshot.png "USB Cable Capability Analyzer GUI")

## Contributing

Feel free to submit issues or pull requests.

## License

MIT License