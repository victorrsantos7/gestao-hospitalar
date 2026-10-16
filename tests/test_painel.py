import unittest
from datetime import date

from gestao_hospitalar.painel import (
    DIAS_SERIE,
    calcular_alertas,
    emergencias_de_hoje,
    eventos_atendimentos,
    eventos_internacoes,
    grafico,
    ler_data,
    mesclar_atividade,
    serie_diaria,
    totais_por_tipo,
)

HOJE = date(2026, 10, 16)


def atendimento(dia: str, tipo: str = "consulta", nome: str = "Ana") -> dict:
    return {"data_atendimento": dia, "tipo": tipo, "paciente_nome": nome}


class SerieTests(unittest.TestCase):
    def test_serie_tem_um_ponto_por_dia_com_zeros(self) -> None:
        serie = serie_diaria([], HOJE)

        self.assertEqual(len(serie), DIAS_SERIE)
        self.assertEqual(serie[-1]["dia"], "2026-10-16")
        self.assertEqual(serie[0]["dia"], "2026-07-25")
        self.assertTrue(all(linha["total"] == "0" for linha in serie))

    def test_conta_total_e_tipo_por_dia(self) -> None:
        serie = serie_diaria(
            [
                atendimento("2026-10-16", "consulta"),
                atendimento("2026-10-16T09:30:00", "emergencia"),
                atendimento("2026-10-15", "retorno"),
            ],
            HOJE,
        )

        hoje = serie[-1]
        self.assertEqual(hoje["total"], "2")
        self.assertEqual(hoje["consulta"], "1")
        self.assertEqual(hoje["emergencia"], "1")
        self.assertEqual(serie[-2]["retorno"], "1")

    def test_ignora_fora_da_janela_data_invalida_e_futuro(self) -> None:
        serie = serie_diaria(
            [
                atendimento("2020-01-01"),
                atendimento("2026-10-17"),
                atendimento("sem data"),
                atendimento(""),
            ],
            HOJE,
        )

        self.assertTrue(all(linha["total"] == "0" for linha in serie))

    def test_tipo_desconhecido_conta_no_total_apenas(self) -> None:
        serie = serie_diaria([atendimento("2026-10-16", "teleconsulta")], HOJE)

        self.assertEqual(serie[-1]["total"], "1")
        self.assertEqual(serie[-1]["consulta"], "0")


class GraficoTests(unittest.TestCase):
    def setUp(self) -> None:
        registros = [atendimento("2026-10-16")] * 3 + [atendimento("2026-10-10")] * 2
        self.serie = serie_diaria(registros, HOJE)

    def test_periodos_diarios(self) -> None:
        sete = grafico(self.serie, "7")
        trinta = grafico(self.serie, "30")

        self.assertEqual(len(sete), 7)
        self.assertEqual(len(trinta), 30)
        self.assertEqual(sete[-1], {"rotulo": "16/10", "atendimentos": 3})
        self.assertEqual(sum(p["atendimentos"] for p in sete), 5)

    def test_periodo_semanal_agrupa_em_12_blocos(self) -> None:
        semanas = grafico(self.serie, "semanas")

        self.assertEqual(len(semanas), 12)
        self.assertEqual(sum(p["atendimentos"] for p in semanas), 5)

    def test_sem_serie_nao_ha_pontos(self) -> None:
        self.assertEqual(grafico([], "30"), [])


class TiposTests(unittest.TestCase):
    def test_totais_percentuais_e_ordem(self) -> None:
        serie = serie_diaria(
            [atendimento("2026-10-16", "emergencia")] * 3
            + [atendimento("2026-10-15", "consulta")],
            HOJE,
        )

        tipos = totais_por_tipo(serie, "7")

        self.assertEqual(tipos[0], {"tipo": "emergencia", "total": 3, "pct": 75})
        self.assertEqual(tipos[1]["tipo"], "consulta")
        self.assertEqual(tipos[1]["pct"], 25)

    def test_respeita_o_periodo(self) -> None:
        serie = serie_diaria([atendimento("2026-09-01", "retorno")], HOJE)

        self.assertEqual(sum(t["total"] for t in totais_por_tipo(serie, "7")), 0)
        self.assertEqual(sum(t["total"] for t in totais_por_tipo(serie, "semanas")), 1)

    def test_sem_atendimentos_percentual_zero(self) -> None:
        self.assertTrue(all(t["pct"] == 0 for t in totais_por_tipo(serie_diaria([], HOJE), "30")))

    def test_emergencias_de_hoje(self) -> None:
        serie = serie_diaria([atendimento("2026-10-16", "emergencia")] * 2, HOJE)

        self.assertEqual(emergencias_de_hoje(serie), 2)
        self.assertEqual(emergencias_de_hoje([]), -1)


class AtividadeTests(unittest.TestCase):
    def test_atendimentos_mais_recentes_primeiro_e_limite(self) -> None:
        registros = [atendimento(f"2026-10-{dia:02d}", nome=f"P{dia}") for dia in range(1, 13)]

        eventos = eventos_atendimentos(registros, limite=3)

        self.assertEqual([e["detalhe"] for e in eventos], ["P12", "P11", "P10"])
        self.assertEqual(eventos[0]["titulo"], "Atendimento · consulta")

    def test_rotulo_do_tipo_leva_acento(self) -> None:
        eventos = eventos_atendimentos([atendimento("2026-10-16", "emergencia")])

        self.assertEqual(eventos[0]["titulo"], "Atendimento · emergência")

    def test_no_mesmo_dia_o_cadastro_mais_novo_vem_antes(self) -> None:
        eventos = eventos_atendimentos(
            [atendimento("2026-10-16", nome="antigo"), atendimento("2026-10-16", nome="novo")]
        )

        self.assertEqual(eventos[0]["detalhe"], "novo")

    def test_internacoes_geram_entrada_e_alta(self) -> None:
        eventos = eventos_internacoes(
            [
                {"leito_id": 4, "paciente_id": 2, "data_entrada": "2026-10-10", "data_saida": "2026-10-12", "status": "alta"},
                {"leito_id": 5, "paciente_id": 3, "data_entrada": "2026-10-14", "data_saida": None, "status": "internado"},
            ]
        )

        self.assertEqual([e["tipo"] for e in eventos], ["internação", "alta", "internação"])
        self.assertEqual(eventos[0]["detalhe"], "Leito 5 · paciente #3")

    def test_alta_sem_status_alta_nao_gera_evento(self) -> None:
        eventos = eventos_internacoes(
            [{"leito_id": 1, "paciente_id": 1, "data_entrada": "2026-10-10", "data_saida": "2026-10-12", "status": "internado"}]
        )

        self.assertEqual([e["tipo"] for e in eventos], ["internação"])

    def test_mesclar_ordena_por_data_e_limita(self) -> None:
        a = [{"tipo": "atendimento", "data": "2026-10-16", "titulo": "A", "detalhe": ""}]
        b = [
            {"tipo": "alta", "data": "2026-10-17", "titulo": "B", "detalhe": ""},
            {"tipo": "internação", "data": "2026-10-01", "titulo": "C", "detalhe": ""},
        ]

        self.assertEqual([e["titulo"] for e in mesclar_atividade(a, b)], ["B", "A", "C"])
        self.assertEqual(len(mesclar_atividade(a, b, limite=2)), 2)


class AlertasTests(unittest.TestCase):
    def test_sem_alertas_em_situacao_normal(self) -> None:
        self.assertEqual(calcular_alertas(50, 5, 0), [])

    def test_ocupacao_elevada_e_critica(self) -> None:
        self.assertEqual(calcular_alertas(75, 6, 0)[0]["nivel"], "amber")
        critico = calcular_alertas(90, 6, 0)[0]
        self.assertEqual(critico["nivel"], "red")
        self.assertIn("90%", critico["texto"])

    def test_poucos_leitos_livres(self) -> None:
        alertas = calcular_alertas(60, 2, 0)

        self.assertEqual([a["texto"] for a in alertas], ["Poucos leitos livres: 2."])

    def test_sem_leitos_livres_substitui_o_alerta_de_ocupacao(self) -> None:
        alertas = calcular_alertas(100, 0, 0)

        self.assertEqual(len(alertas), 1)
        self.assertEqual(alertas[0]["nivel"], "red")
        self.assertIn("Sem leitos livres", alertas[0]["texto"])

    def test_emergencias_hoje_no_singular_e_plural(self) -> None:
        self.assertEqual(calcular_alertas(-1, -1, 1)[0]["texto"], "1 atendimento de emergência hoje.")
        self.assertEqual(calcular_alertas(-1, -1, 3)[0]["texto"], "3 atendimentos de emergência hoje.")

    def test_dados_desconhecidos_nao_geram_alerta(self) -> None:
        self.assertEqual(calcular_alertas(-1, -1, -1), [])


class LerDataTests(unittest.TestCase):
    def test_formatos(self) -> None:
        self.assertEqual(ler_data("2026-10-16"), date(2026, 10, 16))
        self.assertEqual(ler_data("2026-10-16T10:00:00Z"), date(2026, 10, 16))
        self.assertIsNone(ler_data(None))
        self.assertIsNone(ler_data("16/10/2026"))


if __name__ == "__main__":
    unittest.main()