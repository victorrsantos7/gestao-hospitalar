"""Conteúdo da ajuda de uso do sistema, organizado por módulo e por perfil.

Dados puros (sem Reflex) para facilitar o teste: a interface em `ui/ajuda.py`
monta o modal a partir de `TOPICOS`. `permissao` é o nome da variável de
`AuthState` que libera o módulo (a mesma usada no menu); `None` aparece para todos.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Topico:
    id: str
    titulo: str
    icone: str
    permissao: str | None
    resumo: str
    passos: tuple[str, ...]
    dicas: tuple[str, ...] = ()
    perfis: str = ""


TOPICO_INICIAL = "primeiros-passos"

TOPICOS: tuple[Topico, ...] = (
    Topico(
        id=TOPICO_INICIAL,
        titulo="Primeiros passos",
        icone="rocket",
        permissao=None,
        resumo="Como entrar, navegar e usar os botões comuns a todas as telas.",
        passos=(
            "Entre com seu login e senha e pressione Enter ou clique em Entrar.",
            "Use o menu à esquerda para trocar de tela; ele mostra só o que o seu perfil pode acessar.",
            "Atualizar consulta os dados de novo no servidor. Limpar esvazia a leitura, a seleção e a busca da tela.",
            "Cada ação mostra um indicador de carregamento e, ao terminar, um aviso de sucesso ou de erro.",
            "Para sair, use o botão Sair no fim do menu.",
        ),
        dicas=(
            "Em telas pequenas o menu fica recolhido: toque no ícone de menu no topo.",
            "Se a sessão expirar, o sistema avisa e leva você de volta ao login.",
        ),
    ),
    Topico(
        id="painel",
        titulo="Painel",
        icone="layout_dashboard",
        permissao=None,
        resumo="Visão geral da operação, com indicadores e alertas conforme o seu perfil.",
        passos=(
            "Os cartões do topo mostram totais (pacientes, médicos, atendimentos, internações).",
            "Em Atendimentos por período escolha 7 dias, 30 dias ou 12 semanas.",
            "Ocupação de leitos muda de cor: âmbar a partir de 75% e vermelho a partir de 90%.",
            "Os alertas avisam ocupação elevada, falta de leitos livres e emergências do dia.",
            "Atividade recente lista os últimos eventos de atendimentos, internações e altas.",
        ),
        dicas=(
            "Os números são reaproveitados por até 60 segundos; clique em Atualizar para forçar nova leitura.",
            "Os gráficos carregam logo depois dos indicadores, sem travar a navegação.",
        ),
    ),
    Topico(
        id="pacientes",
        titulo="Pacientes",
        icone="users",
        permissao="pode_ver_pacientes",
        resumo="Cadastro e consulta de pacientes.",
        passos=(
            "Para cadastrar, preencha nome completo, CPF, data de nascimento, telefone, endereço e contato de emergência (todos obrigatórios) e clique em Cadastrar paciente.",
            "O CPF é validado e não pode repetir: cada paciente tem um CPF único.",
            "Na lista, use Ver detalhes para abrir a ficha completa do paciente.",
            "Navegue entre as páginas pelo rodapé da lista.",
        ),
        dicas=(
            "A busca filtra apenas os registros da página aberta; troque de página para procurar em outros.",
        ),
        perfis="Recepção e administração cadastram. Perfil médico só consulta.",
    ),
    Topico(
        id="medicos",
        titulo="Médicos",
        icone="stethoscope",
        permissao="pode_ver_medicos",
        resumo="Corpo clínico: nome, CRM e especialidade.",
        passos=(
            "Preencha nome, CRM, especialidade e telefone e clique em Cadastrar médico.",
            "O CRM é validado e deve ser único.",
            "Use Editar para alterar um médico e Atualizar médico para salvar; Cancelar edição descarta a alteração.",
            "Excluir remove o médico apenas se ele não tiver atendimentos vinculados.",
        ),
        dicas=("A busca vale só para a página aberta (nome, CRM ou especialidade).",),
        perfis="Recepção e administração.",
    ),
    Topico(
        id="convenios",
        titulo="Convênios",
        icone="shield_check",
        permissao="pode_ver_convenios",
        resumo="Planos e coberturas aceitas pelo hospital.",
        passos=(
            "Informe o nome, escolha o tipo (particular, plano ou SUS), descreva a cobertura e clique em Cadastrar convênio.",
            "Editar altera o convênio selecionado; Atualizar convênio salva.",
            "Excluir remove o convênio da lista e a ação não pode ser desfeita.",
        ),
        dicas=("Busque por nome ou tipo no campo acima da lista.",),
        perfis="Recepção e administração.",
    ),
    Topico(
        id="atendimentos",
        titulo="Atendimentos e diagnósticos",
        icone="clipboard_list",
        permissao="pode_ver_atendimentos",
        resumo="Consultas, retornos e emergências, com os diagnósticos de cada um.",
        passos=(
            "Para registrar, selecione paciente e médico, informe a data, o tipo e o motivo. O convênio é opcional.",
            "Clique em Cadastrar atendimento. Ele aparece na lista de atendimentos registrados.",
            "Em Ver detalhes você vê os dados do atendimento e seus diagnósticos.",
            "Médicos registram o diagnóstico: informe a descrição, a data e, se quiser, o código CID, e clique em Cadastrar diagnóstico.",
        ),
        dicas=("Busque por paciente, médico ou data.",),
        perfis="Recepção e administração registram atendimentos; médicos registram diagnósticos.",
    ),
    Topico(
        id="internacoes",
        titulo="Internações e leitos",
        icone="bed_double",
        permissao="pode_ver_internacoes",
        resumo="Ocupação de leitos, internações, altas e transferências.",
        passos=(
            "Cadastre os leitos pelo número em Cadastrar leito; eles começam livres.",
            "Para internar, escolha um atendimento elegível, um leito livre e a data de entrada.",
            "Em Registrar alta informe a data de saída e confirme: a internação é encerrada e o leito volta a ficar livre.",
            "Em Nova transferência informe a data, o setor de destino e o motivo e confirme.",
            "Internações encerradas não aceitam novas transferências.",
        ),
        dicas=("Busque por paciente, atendimento, leito ou status.",),
        perfis="Enfermagem, gestão e administração.",
    ),
    Topico(
        id="historico",
        titulo="Histórico do paciente",
        icone="history",
        permissao="pode_ver_historico",
        resumo="Linha do tempo consolidada de atendimentos, internações e transferências.",
        passos=(
            "Selecione o paciente e clique em Consultar histórico.",
            "A linha do tempo mostra os eventos em ordem, com data e detalhes.",
        ),
        perfis="Enfermagem, gestão e administração.",
    ),
    Topico(
        id="relatorios",
        titulo="Relatórios",
        icone="chart_no_axes_combined",
        permissao="pode_ver_relatorios",
        resumo="Ocupação de leitos e internações em andamento.",
        passos=(
            "Veja o total de leitos, quantos estão ocupados e livres.",
            "A lista de internações ativas mostra paciente, leito e data de entrada.",
            "Use Atualizar para ler os dados de novo.",
        ),
        perfis="Enfermagem, gestão e administração.",
    ),
    Topico(
        id="perfis",
        titulo="Perfis e acessos",
        icone="user_check",
        permissao=None,
        resumo="O que cada perfil enxerga e faz.",
        passos=(
            "Recepção: pacientes (cadastro e consulta), médicos, convênios e atendimentos.",
            "Médico: consulta pacientes e atendimentos e registra diagnósticos.",
            "Enfermagem e gestão: internações, leitos, transferências, histórico e relatórios.",
            "Administrador: acesso a todos os módulos.",
        ),
        dicas=(
            "As permissões também são aplicadas no servidor: esconder uma tela não é a única proteção.",
            "Se faltar acesso a algo de que você precisa, fale com o administrador.",
        ),
    ),
    Topico(
        id="problemas",
        titulo="Problemas comuns",
        icone="life_buoy",
        permissao=None,
        resumo="O que fazer quando uma tela não carrega ou uma ação falha.",
        passos=(
            "Se aparecer um aviso de falha ao carregar, clique em Tentar novamente: o sistema já repete a leitura sozinho algumas vezes antes de avisar.",
            "Se a lista parece desatualizada, use Atualizar.",
            "Se a sessão expirar, entre de novo; o que você já digitou em formulários não salvos é perdido.",
            "Erros em formulários indicam o campo a corrigir; leia a mensagem em vermelho acima do formulário.",
        ),
        dicas=("Se o erro persistir por mais de alguns minutos, avise o administrador.",),
    ),
)


def topico_por_id(identificador: str) -> Topico | None:
    for topico in TOPICOS:
        if topico.id == identificador:
            return topico
    return None
