import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ProductContractTests(unittest.TestCase):
    def test_catalog_is_one_time_and_not_fake_live_checkout(self):
        catalog = json.loads((ROOT / "product" / "catalog.json").read_text(encoding="utf-8"))
        self.assertEqual(catalog["schema_version"], "MM-COMMERCE-1")
        self.assertEqual(catalog["currency"], "usd")
        self.assertEqual(len(catalog["offers"]), 1)
        offer = catalog["offers"][0]
        self.assertEqual(offer["unit_amount"], 75000)
        self.assertEqual(offer["billing"], "one_time")
        self.assertIsNone(offer["checkout_url"])
        self.assertIn("blocked", offer["stripe_activation_status"])

    def test_schemas_are_valid_json_and_fail_closed(self):
        order = json.loads((ROOT / "product" / "order.schema.json").read_text(encoding="utf-8"))
        delivery = json.loads((ROOT / "product" / "deliverable.schema.json").read_text(encoding="utf-8"))
        self.assertFalse(order["additionalProperties"])
        self.assertFalse(delivery["additionalProperties"])
        statuses = delivery["properties"]["claims"]["items"]["properties"]["status"]["enum"]
        self.assertEqual(statuses, ["VERIFIED", "ATTRIBUTED", "INFERENCE", "UNSUPPORTED", "CONFLICT"])
        integrity = delivery["properties"]["integrity"]["properties"]
        self.assertTrue(all(value.get("const") is True for value in integrity.values()))


if __name__ == "__main__":
    unittest.main()

