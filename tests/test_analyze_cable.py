import unittest

from usb_cable_tool import analyze_cable


def counts(*pins):
    result = {}
    for pin in pins:
        result[pin] = result.get(pin, 0) + 1
    return result


class AnalyzeCableStandardInterpretationTests(unittest.TestCase):
    def test_full_usb_c_requires_all_visible_vbus_and_gnd_contacts(self):
        active = {
            "TX1+", "TX1-", "RX1+", "RX1-",
            "TX2+", "TX2-", "RX2+", "RX2-",
            "D+", "D-",
            "CC1", "CC2",
            "SBU1", "SBU2",
            "VBUS", "GND",
        }
        report = analyze_cable(
            active,
            counts("VBUS", "VBUS", "GND", "GND", "GND", "GND"),
            "Type C 3.0",
            "Type C 3.0",
        )

        self.assertIn("DAMAGED CABLE", report)
        self.assertIn("Power wiring incomplete", report)
        self.assertIn("detected 2/4 VBUS, 4/4 GND", report)

    def test_full_featured_usb_c_cable_is_valid_with_four_vbus_contacts(self):
        active = {
            "TX1+", "TX1-", "RX1+", "RX1-",
            "TX2+", "TX2-", "RX2+", "RX2-",
            "D+", "D-",
            "CC1", "CC2",
            "SBU1", "SBU2",
            "VBUS", "GND",
        }
        report = analyze_cable(
            active,
            counts("VBUS", "VBUS", "VBUS", "VBUS", "GND", "GND", "GND", "GND"),
            "Type C 3.0",
            "Type C 3.0",
        )

        self.assertIn("Premium USB-C Cable (Full Featured)", report)
        self.assertIn("detected 4/4 VBUS, 4/4 GND", report)

    def test_single_lane_usb_c_to_usb_c_is_non_standard_not_orientation_valid(self):
        active = {"TX1+", "TX1-", "RX1+", "RX1-", "D+", "D-", "CC1", "CC2", "VBUS", "GND"}
        report = analyze_cable(
            active,
            counts("VBUS", "VBUS", "VBUS", "VBUS", "GND", "GND", "GND", "GND"),
            "Type C 3.0",
            "Type C 3.0",
        )

        self.assertIn("NON-STANDARD Cable", report)
        self.assertNotIn("Works in one orientation only", report)

    def test_usb_c_to_legacy_usb3_does_not_require_cc_continuity(self):
        active = {"TX1+", "TX1-", "RX1+", "RX1-", "D+", "D-", "VBUS", "GND"}
        report = analyze_cable(
            active,
            counts("VBUS", "VBUS", "GND", "GND"),
            "Type C 3.0",
            "Type B 3.0",
        )

        self.assertIn("USB 3.x Data Cable (Single-Lane)", report)
        self.assertNotIn("DAMAGED CABLE", report)
        self.assertIn("Type-C CC termination/e-marker is not verified", report)

    def test_legacy_usb3_single_lane_counts_as_superspeed_yes(self):
        active = {"TX1+", "TX1-", "RX1+", "RX1-", "D+", "D-", "VBUS", "GND"}
        report = analyze_cable(
            active,
            counts("VBUS", "GND"),
            "Type A 3.0",
            "Type B 3.0",
        )

        self.assertIn("USB 3.x Data Cable (Single-Lane)", report)
        self.assertIn("SuperSpeed (USB 3.x): Yes", report)
        self.assertIn("detected 4/8 pins; expected 4", report)

    def test_legacy_usb3_accepts_mixed_type_c_row_pairs(self):
        active = {"TX2+", "TX2-", "RX1+", "RX1-", "D+", "D-", "VBUS", "GND"}
        report = analyze_cable(
            active,
            counts("VBUS", "GND"),
            "Type A 3.0",
            "Micro B 3.0",
        )

        self.assertIn("USB 3.x Data Cable (Single-Lane)", report)
        self.assertIn("SuperSpeed (USB 3.x): Yes", report)
        self.assertNotIn("Mismatch", report)
        self.assertNotIn("NON-STANDARD", report)

    def test_legacy_usb3_rejects_two_tx_pairs_without_rx_pair(self):
        active = {"TX1+", "TX1-", "TX2+", "TX2-", "D+", "D-", "VBUS", "GND"}
        report = analyze_cable(
            active,
            counts("VBUS", "GND"),
            "Type A 3.0",
            "Type B 3.0",
        )

        self.assertIn("NON-STANDARD Cable", report)
        self.assertIn("SuperSpeed (USB 3.x): Partial", report)

    def test_lightning_is_reported_as_proprietary_usb2_style_continuity(self):
        active = {"D+", "D-", "VBUS", "GND"}
        report = analyze_cable(
            active,
            counts("VBUS", "GND"),
            "Type A 2.0",
            "Lightning",
        )

        self.assertIn("USB 2.0 Data Cable", report)
        self.assertIn("USB 2.0 D+/D- wiring detected", report)
        self.assertIn("Lightning is proprietary", report)


if __name__ == "__main__":
    unittest.main()
