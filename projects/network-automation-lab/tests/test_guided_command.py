import unittest

from features.guided_command import GuidedCommandFeature, GuidedCommandRequest
from profile_repository import TechnologyProfileRepository


class GuidedCommandFeatureTests(unittest.TestCase):
    def setUp(self):
        self.feature = GuidedCommandFeature(TechnologyProfileRepository())

    def test_r1_eigrp_profile_generates_complete_batch(self):
        batch = self.feature.generate(GuidedCommandRequest("R1", "eigrp_100"))
        self.assertEqual(batch.operation, "config")
        self.assertIn("router eigrp 100", batch.commands)
        self.assertIn("network 198.18.32.0 0.0.31.255", batch.commands)

    def test_pending_profile_cannot_run(self):
        with self.assertRaises(ValueError):
            self.feature.generate(GuidedCommandRequest("R4", "rip_v2"))

    def test_r2_lists_two_ready_eigrp_profiles(self):
        options = self.feature.available_technologies("R2")
        ready = {option.key for option in options if option.status == "ready"}
        self.assertEqual(ready, {"eigrp_100", "eigrp_200"})
