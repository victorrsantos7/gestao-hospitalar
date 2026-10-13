import unittest

from gestao_hospitalar.validacao_transferencias import (
    data_transferencia_valida,
    referencia_transferencia_valida,
    transferencia_texto_valida,
)


class ValidacaoTransferenciasTests(unittest.TestCase):
    def test_validates_reference_and_date(self) -> None:
        self.assertTrue(referencia_transferencia_valida("71"))
        self.assertFalse(referencia_transferencia_valida("0"))
        self.assertTrue(data_transferencia_valida("2026-10-13"))
        self.assertFalse(data_transferencia_valida("13/10/2026"))

    def test_validates_destination_and_reason(self) -> None:
        self.assertTrue(transferencia_texto_valida("UTI"))
        self.assertFalse(transferencia_texto_valida("  "))
        self.assertTrue(transferencia_texto_valida("Acompanhamento medico"))


if __name__ == "__main__":
    unittest.main()
