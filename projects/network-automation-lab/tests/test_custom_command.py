import unittest

from features.custom_command import CustomCommandFeature, ManualCommandRequest


class CustomCommandFeatureTests(unittest.TestCase):
    def setUp(self):
        self.feature = CustomCommandFeature()

    def test_multiline_config_commands(self):
        request = ManualCommandRequest(
            command_text="router eigrp 100\nnetwork 198.18.0.0 0.0.31.255",
            operation="config",
        )
        self.assertEqual(
            self.feature.generate_commands(request),
            ["router eigrp 100", "network 198.18.0.0 0.0.31.255"],
        )

    def test_show_mode_rejects_config_command(self):
        with self.assertRaises(ValueError):
            self.feature.generate_commands(
                ManualCommandRequest("show ip route\nrouter eigrp 100", operation="show")
            )

    def test_destructive_command_is_blocked(self):
        with self.assertRaises(ValueError):
            self.feature.generate_commands(ManualCommandRequest("write erase", operation="exec"))

