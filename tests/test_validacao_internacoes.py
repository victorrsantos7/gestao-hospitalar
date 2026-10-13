import unittest

from gestao_hospitalar.validacao_internacoes import (
    data_internacao_valida,
    data_saida_valida,
    numero_leito_valido,
    status_internacao_valido,
    status_leito_valido,
)


class ValidacaoInternacoesTests(unittest.TestCase):
    def test_validates_bed_number_and_statuses(self) -> None:
        self.assertTrue(numero_leito_valido("101"))
        self.assertFalse(numero_leito_valido("0"))
        self.assertTrue(status_leito_valido("livre"))
        self.assertTrue(status_leito_valido("ocupado"))
        self.assertFalse(status_leito_valido("reservado"))
        self.assertTrue(status_internacao_valido("internado"))
        self.assertTrue(status_internacao_valido("alta"))
        self.assertFalse(status_internacao_valido("cancelada"))

    def test_validates_admission_and_discharge_dates(self) -> None:
        self.assertTrue(data_internacao_valida("2026-10-13"))
        self.assertFalse(data_internacao_valida("13/10/2026"))
        self.assertTrue(data_saida_valida("2026-10-14", "2026-10-13"))
        self.assertTrue(data_saida_valida("2026-10-13", "2026-10-13"))
        self.assertFalse(data_saida_valida("2026-10-12", "2026-10-13"))


if __name__ == "__main__":
    unittest.main()
