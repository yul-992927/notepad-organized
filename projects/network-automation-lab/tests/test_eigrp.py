import unittest

from features.eigrp import EigrpFeature, EigrpRequest


class EigrpCommandTests(unittest.TestCase):
    def setUp(self):
        self.feature = EigrpFeature()

    def test_network_commands(self):
        request = EigrpRequest(
            action="network",
            as_number=100,
            network="198.18.0.0",
            wildcard="0.0.127.255",
        )
        self.assertEqual(
            self.feature.generate_commands(request),
            ["router eigrp 100", "network 198.18.0.0 0.0.127.255"],
        )

    def test_passive_interface(self):
        request = EigrpRequest(
            action="passive_interface", as_number=200, interface="GigabitEthernet0/1"
        )
        self.assertEqual(
            self.feature.generate_commands(request),
            ["router eigrp 200", "passive-interface GigabitEthernet0/1"],
        )

    def test_invalid_as_number(self):
        with self.assertRaises(ValueError):
            self.feature.generate_commands(EigrpRequest(action="create", as_number=0))


if __name__ == "__main__":
    unittest.main()

