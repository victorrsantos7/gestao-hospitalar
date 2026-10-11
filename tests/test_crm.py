import unittest

from gestao_hospitalar.crm import crm_valido, formatar_crm, normalizar_crm


class CrmTests(unittest.TestCase):
    def test_normalizes_masked_crm(self) -> None:
        self.assertEqual(normalizar_crm("CRM 1234567 / sp"), "1234567/SP")
        self.assertEqual(normalizar_crm("12244/SP"), "12244/SP")

    def test_rejects_invalid_crm(self) -> None:
        self.assertFalse(crm_valido("123/SP"))
        self.assertFalse(crm_valido("1234567/XX"))
        self.assertEqual(normalizar_crm("sem crm"), "")

    def test_formats_crm_input(self) -> None:
        self.assertEqual(formatar_crm("1234567sp"), "1234567/SP")


if __name__ == "__main__":
    unittest.main()