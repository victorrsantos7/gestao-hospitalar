import unittest

from gestao_hospitalar.cpf import cpf_valido, normalizar_cpf


class CpfTests(unittest.TestCase):
    def test_normalizes_formatted_cpf(self) -> None:
        self.assertEqual(normalizar_cpf("529.982.247-25"), "52998224725")

    def test_accepts_valid_cpf(self) -> None:
        self.assertTrue(cpf_valido("529.982.247-25"))

    def test_rejects_invalid_check_digit(self) -> None:
        self.assertFalse(cpf_valido("529.982.247-26"))

    def test_rejects_repeated_digits(self) -> None:
        self.assertFalse(cpf_valido("111.111.111-11"))

    def test_rejects_wrong_length(self) -> None:
        self.assertFalse(cpf_valido("123456789"))


if __name__ == "__main__":
    unittest.main()
