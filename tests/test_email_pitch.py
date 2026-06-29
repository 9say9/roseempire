import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from send_leads_emails import _default_pitch


class EmailPitchTests(unittest.TestCase):
    def test_default_pitch_mentions_company_name_and_cta(self) -> None:
        subject, body = _default_pitch("Harbor Care Homes", "Care Home")
        self.assertIn("Harbor Care Homes", subject)
        self.assertIn("Harbor Care Homes", body)
        self.assertIn("request a quote", body.lower())
        self.assertIn("Rose Empire", body)


if __name__ == "__main__":
    unittest.main()
