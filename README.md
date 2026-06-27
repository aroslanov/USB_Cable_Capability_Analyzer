# USB Cable Capability Analyzer

![Treedix C-TRX5-0575 / Occkic MRB063A / Noname USB Cable Tester](assets/board.png)

A GUI tool to analyze USB-C cable wiring and capabilities based on pin connections.

## Description

This tool mimics the Treedix C-TRX5-0575 / Occkic MRB063A / Noname USB Cable Tester board. Users select which pins are active (LEDs ON), choose the connector types on each end of the cable, and the software infers the cable's wiring, capabilities, and auto-classifies it.

**Note:** This is a diagnostic tool, not a USB-IF compliance certifier.

## Features

- **Real-time Analysis**: Live diagnostic updates as you interact with checkboxes or change connector selections.
- **Connector Selectors**: Choose the connector type for each cable end (Left: Type A 2.0 / 3.0, Type C 3.0; Right: Type B 3.0, Type C 3.0, Micro B 3.0, Mini B 2.0, Lightning, Micro B 2.0). The analysis adapts based on your selections.
- **Comprehensive Cable Support**: Analyzes USB 2.0, SuperSpeed (USB 3.x), CC lines, SBU lines, and power delivery across multiple connector types.
- **Right-Side Pin Translation**: Automatically maps physical board silk-screen labels (Right Row A) to logical USB signal names for accurate analysis.
- **Broken Pair Detection**: Explicitly identifies incomplete differential pairs (e.g., TX1+ without TX1-) and reports them as potential cable damage.
- **Incomplete Power Wiring Detection**: Detects missing VBUS or GND connections and reports them as damage.
- **Mismatch Detection**: Flags inconsistencies between selected connector types and detected SuperSpeed wiring.
- **Wiring Warnings**: Distinguishes between critical broken pairs (damage) and non-critical advisories (e.g., missing CC on a charge-only USB-C cable).
- **Lane-Level Reporting**: Independent status for each SuperSpeed lane (Lane 1 & Lane 2) with specific pin counts.
- **Detailed Diagnostics**:
  - Complete lane status (OK / INCOMPLETE / MISSING)
  - Broken differential pair identification
  - Wiring warnings for non-critical issues
  - Orientation-dependent operation warnings
  - Connector configuration summary
  - Checked pin listing per side
- **Auto-Classification**: Smart cable type identification with specific labels:
  - Premium USB-C Cable (Full Featured)
  - USB 3.x Fast Data Cable
  - USB 3.x Data Cable (Single-Lane)
  - USB 2.0 Data Cable (legacy or generic)
  - Charging Cable
  - Charging Cable (Incomplete Power Wiring)
  - NON-STANDARD Cable (incomplete SuperSpeed)
  - DAMAGED CABLE (broken wiring detected)
  - Mismatch (connector vs wiring)
  - Unknown Cable
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
- Select the connector types for the **Left** and **Right** ends of the cable using the radio button panels.
- Check the boxes corresponding to the pins that are active (LEDs ON) on your USB Cable Tester board.
- The analysis updates in real-time below the checkboxes.
- Use "Select All" to check all pins, "Unselect All" to clear them.
- Click "Copy to Clipboard" to copy the full report.
- Hover over checkboxes for tooltips explaining each pin.

## Analysis Details

### Connector Selection
The left panel offers **Type A 2.0**, **Type A 3.0**, and **Type C 3.0** connectors. The right panel offers **Type B 3.0**, **Type C 3.0**, **Micro B 3.0**, **Mini B 2.0**, **Lightning**, and **Micro B 2.0**. The expected number of SuperSpeed pins and power wiring adjusts based on your selections:
- **USB-C both ends**: Expects 8 SuperSpeed pins, 2× VBUS, 4× GND, CC, SBU.
- **USB 3.0 (non-C)**: Expects 4 SuperSpeed pins (Lane 1 only), 1× VBUS, 1× GND.
- **USB 2.0 (non-C)**: Expects no SuperSpeed pins, 1× VBUS, 1× GND.

### Right-Side Pin Translation
The physical board's Right Row A has a different silk-screen labeling than the logical USB-C standard. The tool automatically translates board labels to logical signals:
| Board Label | Logical Signal |
|-------------|---------------|
| RX2+ (Pin 2) | TX1+ |
| RX2- (Pin 3) | TX1- |
| D- (Pin 6) | D+ |
| D+ (Pin 7) | D- |
| TX1- (Pin 10) | RX2- |
| TX1+ (Pin 11) | RX2+ |

No translation is needed for the Left Row B (pins follow standard labeling).

### Broken Pair Detection
The tool detects incomplete differential pairs (both TX and RX pairs) for each SuperSpeed lane, as well as broken USB 2.0 D+/D- pairs and incomplete power wiring. If any broken pairs are found, the cable is classified as **DAMAGED CABLE** with specific identification.

**Examples**:
- TX1+ present but TX1- missing → "Lane 1 TX pair broken"
- D+ present but D- missing → "USB 2.0 D+/D- pair broken"
- VBUS present but GND missing → "Power wiring incomplete (VBUS/GND)"

### Wiring Warnings
Non-critical issues are reported as warnings rather than damage:
- Missing CC wiring on a charge-only USB-C cable (no data, no SuperSpeed)
- Incomplete CC wiring (only one CC pin detected on a USB-C cable with data)

### Lane-Level Reporting
Each SuperSpeed lane is analyzed independently:
- **OK**: All 4 pins present (TX+, TX-, RX+, RX-)
- **INCOMPLETE**: Partial pins detected with count (e.g., 3/4 pins)
- **MISSING**: No pins from that lane detected

### Auto-Classification
The tool automatically classifies cables into categories based on detected wiring and connector selection:
- **Premium USB-C Cable (Full Featured)** — All 8 SuperSpeed pins + USB 2.0 + CC + both SBU lines
- **USB 3.x Fast Data Cable** — Full SuperSpeed (8 pins) + USB 2.0 + CC
- **USB 3.x Data Cable (Single-Lane)** — 4 SuperSpeed pins + USB 2.0
- **USB 2.0 Data Cable** — USB 2.0 data only, no SuperSpeed
- **Charging Cable** — Power only, no data lines
- **Charging Cable (Incomplete Power Wiring)** — Power only but VBUS/GND incomplete
- **NON-STANDARD Cable** — USB 2.0 with incomplete SuperSpeed pins
- **DAMAGED CABLE** — Broken differential pairs or incomplete power detected
- **Mismatch** — Connector selection doesn't match detected wiring
- **Unknown Cable** — Cannot determine cable type

Orientation warnings are provided for single-lane operation (flip-dependent).

## Running Tests

Unit tests are provided in `tests/test_analyze_cable.py`. Run them with:

```
python -m unittest tests.test_analyze_cable
```

Tests cover:
- All valid connector pair combinations (3 left × 6 right = 18 combinations)
- USB 2.0 legacy (Type A to Micro B)
- USB 3.0 legacy single-lane (Type A 3.0 to Type B 3.0)
- Full-featured USB-C (both ends)
- Missing CC on USB-C (detected as damaged)
- USB-C to Type B (single-lane)
- Charge-only legacy cable
- Broken USB 2.0 pair
- SuperSpeed mismatch with connector selection
- Lane 2 on legacy USB 3.0 mismatch
- Incomplete power wiring

## Requirements

- Python 3.6 or higher
- Tkinter (included with Python)
- No external pip dependencies

## Screenshot

![Program Screenshot](assets/screenshot.png "USB Cable Capability Analyzer GUI")

## Contributing

Feel free to submit issues or pull requests.

## License

MIT License