import unittest
from datetime import date

from gestao_hospitalar.relatorios_calculo import contagem_leitos, internacoes_ativas


class RelatoriosCalculoTests(unittest.TestCase):
    def test_contagem_leitos_livres_ocupados_e_total(self) -> None:
        leitos = [
            {"id": "1", "numero": "101", "status": "livre"},
            {"id": "2", "numero": "102", "status": "ocupado"},
            {"id": "3", "numero": "103", "status": "ocupado"},
        ]
        self.assertEqual(
            contagem_leitos(leitos), {"livres": 1, "ocupados": 2, "total": 3}
        )

    def test_contagem_leitos_vazia(self) -> None:
        self.assertEqual(
            contagem_leitos([]), {"livres": 0, "ocupados": 0, "total": 0}
        )

    def test_internacoes_ativas_calcula_dias_internado(self) -> None:
        internacoes = [
            {
                "id": "1",
                "status": "internado",
                "leito_numero": "101",
                "data_entrada": "2026-10-10",
            }
        ]
        resultado = internacoes_ativas(internacoes, hoje=date(2026, 10, 14))
        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0]["dias_internado"], 4)
        self.assertEqual(resultado[0]["leito_numero"], "101")

    def test_internacao_com_alta_nao_aparece(self) -> None:
        internacoes = [
            {
                "id": "1",
                "status": "alta",
                "leito_numero": "101",
                "data_entrada": "2026-10-10",
            }
        ]
        self.assertEqual(internacoes_ativas(internacoes, hoje=date(2026, 10, 14)), [])

    def test_internacoes_ativas_vazia(self) -> None:
        self.assertEqual(internacoes_ativas([], hoje=date(2026, 10, 14)), [])

    def test_data_entrada_invalida_e_ignorada(self) -> None:
        internacoes = [
            {
                "id": "1",
                "status": "internado",
                "leito_numero": "101",
                "data_entrada": "",
            },
            {
                "id": "2",
                "status": "internado",
                "leito_numero": "102",
                "data_entrada": "10/10/2026",
            },
        ]
        self.assertEqual(internacoes_ativas(internacoes, hoje=date(2026, 10, 14)), [])
