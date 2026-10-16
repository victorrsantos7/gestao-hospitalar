"""Cálculos do painel: série por período, tipos, atividade recente e alertas."""

from datetime import date, timedelta
from typing import Any

from gestao_hospitalar.validacao_atendimentos import TIPOS_ATENDIMENTO

DIAS_SERIE = 84
PERIODOS: dict[str, str] = {"7": "7 dias", "30": "30 dias", "semanas": "12 semanas"}
LIMITE_ATIVIDADE = 8
OCUPACAO_ATENCAO = 75
OCUPACAO_CRITICA = 90
MINIMO_LEITOS_LIVRES = 2
ROTULOS_TIPO = {"emergencia": "emergência"}


def ler_data(valor: Any) -> date | None:
    """Data ISO (AAAA-MM-DD, com ou sem hora) ou None se inválida."""
    try:
        return date.fromisoformat(str(valor)[:10])
    except ValueError:
        return None


def serie_diaria(atendimentos: list[dict[str, Any]], hoje: date) -> list[dict[str, str]]:
    """Contagem diária (total e por tipo) dos últimos DIAS_SERIE dias, com zeros."""
    inicio = hoje - timedelta(days=DIAS_SERIE - 1)
    contagem: dict[date, dict[str, int]] = {}
    for registro in atendimentos:
        dia = ler_data(registro.get("data_atendimento", ""))
        if dia is None or dia < inicio or dia > hoje:
            continue
        do_dia = contagem.setdefault(dia, {})
        do_dia["total"] = do_dia.get("total", 0) + 1
        tipo = str(registro.get("tipo", ""))
        if tipo in TIPOS_ATENDIMENTO:
            do_dia[tipo] = do_dia.get(tipo, 0) + 1

    serie = []
    for deslocamento in range(DIAS_SERIE):
        dia = inicio + timedelta(days=deslocamento)
        do_dia = contagem.get(dia, {})
        linha = {"dia": dia.isoformat(), "total": str(do_dia.get("total", 0))}
        for tipo in TIPOS_ATENDIMENTO:
            linha[tipo] = str(do_dia.get(tipo, 0))
        serie.append(linha)
    return serie


def _janela(serie: list[dict[str, str]], periodo: str) -> list[dict[str, str]]:
    if periodo == "7":
        return serie[-7:]
    if periodo == "30":
        return serie[-30:]
    return serie


def _rotulo(dia_iso: str) -> str:
    return f"{dia_iso[8:10]}/{dia_iso[5:7]}"


def grafico(serie: list[dict[str, str]], periodo: str) -> list[dict[str, Any]]:
    """Pontos do gráfico: diários (7 e 30 dias) ou semanais (12 semanas)."""
    if not serie:
        return []
    if periodo == "semanas":
        return [
            {
                "rotulo": _rotulo(bloco[0]["dia"]),
                "atendimentos": sum(int(linha["total"]) for linha in bloco),
            }
            for bloco in (serie[i : i + 7] for i in range(0, len(serie), 7))
        ]
    return [
        {"rotulo": _rotulo(linha["dia"]), "atendimentos": int(linha["total"])}
        for linha in _janela(serie, periodo)
    ]


def totais_por_tipo(serie: list[dict[str, str]], periodo: str) -> list[dict[str, Any]]:
    """Atendimentos por tipo no período, do mais ao menos frequente."""
    janela = _janela(serie, periodo)
    total_periodo = sum(int(linha["total"]) for linha in janela)
    itens = []
    for tipo in TIPOS_ATENDIMENTO:
        soma = sum(int(linha[tipo]) for linha in janela)
        pct = round(100 * soma / total_periodo) if total_periodo else 0
        itens.append({"tipo": tipo, "total": soma, "pct": pct})
    return sorted(itens, key=lambda item: -item["total"])


def emergencias_de_hoje(serie: list[dict[str, str]]) -> int:
    """Emergências do último dia da série; -1 sem leitura."""
    if not serie:
        return -1
    return int(serie[-1].get("emergencia", 0))


def eventos_atendimentos(
    atendimentos: list[dict[str, Any]], limite: int = LIMITE_ATIVIDADE
) -> list[dict[str, str]]:
    eventos = []
    for registro in reversed(atendimentos):
        dia = ler_data(registro.get("data_atendimento", ""))
        if dia is None:
            continue
        eventos.append(
            {
                "tipo": "atendimento",
                "data": dia.isoformat(),
                "titulo": f"Atendimento · {ROTULOS_TIPO.get(str(registro.get('tipo', '')), registro.get('tipo', ''))}",
                "detalhe": str(registro.get("paciente_nome", "")),
            }
        )
    return sorted(eventos, key=lambda evento: evento["data"], reverse=True)[:limite]


def eventos_internacoes(
    internacoes: list[dict[str, Any]], limite: int = LIMITE_ATIVIDADE
) -> list[dict[str, str]]:
    eventos = []
    for registro in reversed(internacoes):
        detalhe = f"Leito {registro.get('leito_id', '')} · paciente #{registro.get('paciente_id', '')}"
        entrada = ler_data(registro.get("data_entrada", ""))
        if entrada is not None:
            eventos.append(
                {
                    "tipo": "internação",
                    "data": entrada.isoformat(),
                    "titulo": "Internação iniciada",
                    "detalhe": detalhe,
                }
            )
        saida = ler_data(registro.get("data_saida", ""))
        if saida is not None and registro.get("status") == "alta":
            eventos.append(
                {
                    "tipo": "alta",
                    "data": saida.isoformat(),
                    "titulo": "Alta registrada",
                    "detalhe": detalhe,
                }
            )
    return sorted(eventos, key=lambda evento: evento["data"], reverse=True)[:limite]


def mesclar_atividade(
    *listas: list[dict[str, str]], limite: int = LIMITE_ATIVIDADE
) -> list[dict[str, str]]:
    todos = [evento for lista in listas for evento in lista]
    return sorted(todos, key=lambda evento: evento["data"], reverse=True)[:limite]


def calcular_alertas(taxa: int, livres: int, emergencias_hoje: int) -> list[dict[str, str]]:
    """Alertas operacionais; `nivel` é a cor do componente (red, amber, blue)."""
    alertas = []
    if taxa >= 0:
        if livres == 0:
            alertas.append({"nivel": "red", "texto": f"Sem leitos livres (ocupação de {taxa}%)."})
        else:
            if taxa >= OCUPACAO_CRITICA:
                alertas.append({"nivel": "red", "texto": f"Ocupação crítica: {taxa}% dos leitos em uso."})
            elif taxa >= OCUPACAO_ATENCAO:
                alertas.append({"nivel": "amber", "texto": f"Ocupação elevada: {taxa}% dos leitos em uso."})
            if 0 < livres <= MINIMO_LEITOS_LIVRES:
                alertas.append({"nivel": "amber", "texto": f"Poucos leitos livres: {livres}."})
    if emergencias_hoje > 0:
        plural = "atendimento de emergência" if emergencias_hoje == 1 else "atendimentos de emergência"
        alertas.append({"nivel": "blue", "texto": f"{emergencias_hoje} {plural} hoje."})
    return alertas