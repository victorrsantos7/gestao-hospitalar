import unittest

from gestao_hospitalar.validacao_historico import (
    data_historico_valida,
    normalizar_historico,
    referencia_historico_valida,
)


class ValidacaoHistoricoTests(unittest.TestCase):
    def test_validates_reference_and_date(self) -> None:
        self.assertTrue(referencia_historico_valida("1"))
        self.assertFalse(referencia_historico_valida("0"))
        self.assertTrue(data_historico_valida("2026-10-13"))
        self.assertFalse(data_historico_valida("13/10/2026"))

    def test_normalizes_and_orders_events(self) -> None:
        eventos = normalizar_historico(
            {
                "atendimentos": [
                    {
                        "data_atendimento": "2026-10-13",
                        "tipo": "consulta",
                        "motivo": "Dor",
                        "diagnosticos": [
                            {
                                "data_diagnostico": "2026-10-14",
                                "descricao": "Inflamacao",
                            }
                        ],
                    }
                ],
                "internacoes": [
                    {
                        "data_entrada": "2026-10-15",
                        "status": "internado",
                        "leito_id": 1,
                        "transferencias": [
                            {
                                "data_transferencia": "2026-10-16",
                                "destino": "UTI",
                                "motivo": "Monitoramento",
                            }
                        ],
                    }
                ],
            }
        )

        self.assertEqual(
            [evento["tipo"] for evento in eventos],
            ["atendimento", "diagnostico", "internacao", "transferencia"],
        )


if __name__ == "__main__":
    unittest.main()
