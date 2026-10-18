import unittest

from inventory_loader import InventoryRepository


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.inventory = InventoryRepository()

    def test_eigrp_100_members(self):
        self.assertEqual(
            self.inventory.devices_for_group("eigrp_100"), ["R1", "R2", "R3", "R4"]
        )

    def test_r13_requires_management_ip(self):
        self.assertIsNone(self.inventory.device("R13")["management_ip"])


if __name__ == "__main__":
    unittest.main()

