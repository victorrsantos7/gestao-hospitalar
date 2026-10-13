import unittest

from gestao_hospitalar.validacao_atendimentos import (
    data_atendimento_valida,
    motivo_atendimento_valido,
    referencia_atendimento_valida,
    tipo_atendimento_valido,
)


class ValidacaoAtendimentosTests(unittest.TestCase):
    def test_accepts_supported_types(self) -> None:
        self.assertTrue(tipo_atendimento_valido("consulta"))
        self.assertTrue(tipo_atendimento_valido("emergencia"))
        self.assertTrue(tipo_atendimento_valido("retorno"))
        self.assertFalse(tipo_atendimento_valido("internacao"))

    def test_validates_iso_date_and_reason(self) -> None:
        self.assertTrue(data_atendimento_valida("2026-10-12"))
        self.assertFalse(data_atendimento_valida("12/10/2026"))
        self.assertTrue(motivo_atendimento_valido("Dor abdominal"))
        self.assertFalse(motivo_atendimento_valido("  "))

    def test_validates_positive_references(self) -> None:
        self.assertTrue(referencia_atendimento_valida("10"))
        self.assertFalse(referencia_atendimento_valida("0"))
        self.assertFalse(referencia_atendimento_valida("abc"))


if __name__ == "__main__":
    unittest.main()