import unittest

from gestao_hospitalar.validacao_diagnosticos import (
    data_diagnostico_valida,
    diagnostico_texto_valido,
    referencia_diagnostico_valida,
)


class ValidacaoDiagnosticosTests(unittest.TestCase):
    def test_validates_text_and_iso_date(self) -> None:
        self.assertTrue(diagnostico_texto_valido("Hipertensao"))
        self.assertFalse(diagnostico_texto_valido("  "))
        self.assertTrue(data_diagnostico_valida("2026-10-13"))
        self.assertFalse(data_diagnostico_valida("13/10/2026"))

    def test_validates_positive_attendance_reference(self) -> None:
        self.assertTrue(referencia_diagnostico_valida("41"))
        self.assertFalse(referencia_diagnostico_valida("0"))
        self.assertFalse(referencia_diagnostico_valida("abc"))


if __name__ == "__main__":
    unittest.main()
