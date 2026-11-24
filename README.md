# 🏥 Sistema de Gestão Hospitalar

> Um só lugar para acompanhar o paciente do cadastro até a alta.

## Sumário

1. [Apresentação](#1-apresentação)
2. [Acesso ao aplicativo](#2-acesso-ao-aplicativo)
3. [Perfis de usuários](#3-perfis-de-usuários)
4. [Funcionalidades](#4-funcionalidades)
5. [Manual de utilização](#5-manual-de-utilização)
6. [Informações técnicas](#6-informações-técnicas)

---

## 1. Apresentação

**Sistema de Gestão Hospitalar** é um aplicativo web que reúne, em um único
lugar, tudo o que acontece com um paciente dentro do hospital: o cadastro, as
consultas, os diagnósticos, as internações, o leito em que ele está e as
mudanças de setor.

### Qual problema ele resolve?

Em muitos hospitais e clínicas, as informações do paciente ficam espalhadas
(papéis, planilhas, sistemas diferentes). Isso dificulta saber o que já foi
feito com o paciente, como ele está evoluindo e quantos leitos ainda estão
livres. O sistema **centraliza essas informações** e mantém um **histórico
completo e organizado** de cada paciente.

### Para quem é?

| Quem | Como usa o sistema |
|---|---|
| **Recepção / administrativo** | Cadastra pacientes, médicos e convênios e registra os atendimentos. |
| **Médicos** | Consultam pacientes e atendimentos e registram os diagnósticos. |
| **Enfermagem e gestão** | Controlam internações, leitos, transferências e acompanham relatórios. |
| **Administrador** | Tem acesso a todas as áreas do sistema. |

> ℹ️ Este é um projeto acadêmico. Os dados exibidos na versão publicada são
> **fictícios**.

---

## 2. Acesso ao aplicativo

🔗 **Versão publicada:** <https://gestao-hospitalar-neon-apple.reflex.run>

**Como entrar:**

1. Abra o link acima em um navegador (Chrome, Edge, Firefox ou Safari), no
   computador ou no celular.
2. Na tela de login, informe seu **Login** e sua **Senha** e clique em
   **Entrar** (ou pressione `Enter`).
3. O acesso é restrito a profissionais autorizados. As contas são criadas pelo
   administrador; **não existe cadastro público**. Para avaliar o sistema,
   solicite um login de teste ao grupo responsável pelo projeto — há uma conta
   para cada perfil descrito na próxima seção.

**Boas práticas e observações:**

- O aplicativo funciona melhor com conexão estável à internet.
- A versão publicada é um ambiente de testes e pode demorar alguns segundos
  para responder. Se não abrir, tente novamente mais tarde.
- Se a sessão expirar, o sistema avisa e leva você de volta ao login.
- Para sair com segurança, use o botão **Sair**, no fim do menu lateral.

Quer rodar o sistema no seu computador? Veja
[Informações técnicas](#6-informações-técnicas).

---

## 3. Perfis de usuários

Cada pessoa entra com um **perfil**, que define o que ela vê no menu e o que
pode fazer. As regras são aplicadas também no servidor: esconder uma tela não é
a única proteção, e quem não tem permissão não consegue executar a ação.

| Perfil | Responsabilidade | O que pode fazer |
|---|---|---|
| **Recepcionista** | Porta de entrada do paciente | Cadastrar e consultar **pacientes**; cadastrar **médicos** e **convênios**; registrar **atendimentos**. |
| **Médico** | Atendimento clínico | **Consultar** pacientes e atendimentos; registrar **diagnósticos**. |
| **Enfermagem e gestão** | Cuidado e ocupação do hospital | Registrar **internações**, cadastrar **leitos**, dar **alta**, registrar **transferências**, ver o **histórico do paciente** e os **relatórios**. |
| **Administrador** | Supervisão geral | Acesso a **todas** as áreas do sistema. |

### Quem enxerga o quê no menu

| Tela | Recepcionista | Médico | Enfermagem e gestão | Administrador |
|---|:---:|:---:|:---:|:---:|
| Painel | ✅ | ✅ | ✅ | ✅ |
| Pacientes | ✅ cadastra e consulta | 👁️ só consulta | — | ✅ |
| Médicos | ✅ | — | — | ✅ |
| Convênios | ✅ | — | — | ✅ |
| Atendimentos | ✅ registra | 👁️ consulta + diagnósticos | — | ✅ |
| Internações e leitos | — | — | ✅ | ✅ |
| Histórico do paciente | — | — | ✅ | ✅ |
| Relatórios | — | — | ✅ | ✅ |

---

## 4. Funcionalidades

- **Painel inicial** — totais (pacientes, médicos, atendimentos, internações),
  gráfico de atendimentos por período, ocupação de leitos, alertas e atividade
  recente.
- **Cadastro de pacientes** — nome, CPF, data de nascimento, telefone, endereço
  e contato de emergência, com validação do CPF (que não pode se repetir).
- **Cadastro de médicos** — nome, CRM, especialidade e telefone, com validação do
  CRM (que também não pode se repetir).
- **Cadastro de convênios** — planos e coberturas aceitos (particular, plano de
  saúde ou SUS).
- **Atendimentos** — consultas, retornos e emergências, ligando paciente, médico
  e, se houver, convênio.
- **Diagnósticos** — descrição e código CID registrados em cada atendimento.
- **Internações e leitos** — cadastro de leitos, registro de internação, alta e
  controle de leitos livres/ocupados (um leito só abriga um paciente por vez).
- **Transferências** — registro da mudança do paciente entre setores (ex.: UTI),
  com data e motivo.
- **Histórico do paciente** — linha do tempo com atendimentos, internações e
  transferências.
- **Relatórios** — ocupação de leitos e internações em andamento.
- **Ajuda dentro do sistema** — botão flutuante de ajuda, com explicações de cada
  tela conforme o seu perfil.
- **Busca e paginação** nas listas, e botões **Atualizar** e **Limpar** em todas
  as telas.

---

## 5. Manual de utilização

### 5.1 Primeiros passos (todos os perfis)

1. **Entre** com Login e Senha e clique em **Entrar**.
2. Use o **menu à esquerda** para trocar de tela — ele mostra só o que o seu
   perfil pode acessar. No celular, toque no ícone de menu no topo.
3. Botões que existem em quase todas as telas:
   - **Atualizar** — busca os dados novamente no servidor.
   - **Limpar** — esvazia a tela (busca, seleção e leitura); **não apaga nada**
     do sistema.
4. Toda ação mostra um indicador de carregamento e, ao terminar, um aviso de
   **sucesso** ou **erro**.
5. Para sair, clique em **Sair** no fim do menu.

### 5.2 Painel (todos os perfis)

- Os **cartões do topo** mostram os totais do hospital.
- Em **Atendimentos por período**, escolha 7 dias, 30 dias ou 12 semanas.
- A **ocupação de leitos** muda de cor: amarelo a partir de 75% e vermelho a
  partir de 90%.
- Os **alertas** avisam sobre ocupação alta, falta de leitos livres e
  emergências do dia.
- **Atividade recente** lista os últimos atendimentos, internações e altas.
- Dúvidas em qualquer tela? Clique no **botão de ajuda** flutuante.

### 5.3 Jornada da recepção

**a) Cadastrar um paciente** (menu **Pacientes**)

1. Preencha nome completo, CPF, data de nascimento, telefone, endereço e
   contato de emergência (todos obrigatórios).
2. Clique em **Cadastrar paciente**.
3. Se o CPF for inválido ou já existir, o sistema mostra a mensagem em vermelho
   acima do formulário; corrija e tente de novo.
4. Para ver a ficha completa, clique em **Ver detalhes** na lista.

**b) Cadastrar médicos** (menu **Médicos**)

1. Informe nome, CRM, especialidade e telefone e clique em **Cadastrar médico**.
2. Para alterar, clique em **Editar**, mude os dados e clique em **Atualizar
   médico** (ou **Cancelar edição**).
3. **Excluir** só funciona se o médico não tiver atendimentos vinculados.

**c) Cadastrar convênios** (menu **Convênios**)

1. Informe o nome, escolha o tipo (particular, plano ou SUS), descreva a
   cobertura e clique em **Cadastrar convênio**.
2. Use **Editar** e **Atualizar convênio** para corrigir. **Excluir** não pode
   ser desfeito.

**d) Registrar um atendimento** (menu **Atendimentos**)

1. Selecione o **paciente** e o **médico**.
2. Informe a **data**, o **tipo** e o **motivo**. O convênio é opcional.
3. Clique em **Cadastrar atendimento**; ele aparece na lista abaixo.
4. Clique em **Ver detalhes** para ver os dados e os diagnósticos do atendimento.

### 5.4 Jornada do médico

**Consultar pacientes e atendimentos** — nos menus **Pacientes** e
**Atendimentos**, use a busca e **Ver detalhes** (o perfil médico só consulta
pacientes).

**Registrar um diagnóstico** (menu **Atendimentos**)

1. Localize o atendimento e clique em **Ver detalhes**.
2. Informe a **descrição**, a **data** e, se quiser, o **código CID**.
3. Clique em **Cadastrar diagnóstico**.

### 5.5 Jornada da enfermagem e gestão

**a) Cadastrar leitos** (menu **Internações e leitos**)

1. Digite o número do leito (ex.: 101) e clique em **Cadastrar leito**. Todo
   leito novo começa **livre**.

**b) Internar um paciente**

1. Em **Registrar internação**, escolha o **atendimento elegível**, um **leito
   livre** e a **data de entrada**.
2. Clique em **Registrar internação**. O leito passa a **ocupado**.

**c) Transferir o paciente de setor**

1. Na internação, abra **Ver transferências** e use **Nova transferência**.
2. Informe a **data**, o **setor de destino** (ex.: UTI) e o **motivo**, e clique
   em **Registrar transferência**.
3. Internações já encerradas não aceitam novas transferências.

**d) Dar alta**

1. Clique em **Registrar alta** na internação, informe a **data de saída** e
   confirme em **Confirmar alta**.
2. A internação é encerrada e o leito volta a ficar **livre**.

**e) Consultar o histórico** (menu **Histórico do paciente**)

1. Selecione o paciente e clique em **Consultar histórico**.
2. A linha do tempo mostra, em ordem, atendimentos, internações e transferências.

**f) Ver relatórios** (menu **Relatórios**)

- Veja o total de leitos, quantos estão ocupados e livres, e a lista de
  internações em andamento (paciente, leito e data de entrada). Use
  **Atualizar** para ler os dados de novo.

### 5.6 Administrador

Tem acesso a todas as telas acima. As contas e o perfil de cada pessoa são
definidos pela administração do sistema; quem precisar de mais acesso deve
falar com o administrador.

### 5.7 Problemas comuns

| Situação | O que fazer |
|---|---|
| Aviso de falha ao carregar | Clique em **Tentar novamente**. O sistema já tenta sozinho algumas vezes antes de avisar. |
| Lista parece desatualizada | Clique em **Atualizar**. |
| Voltou para a tela de login | A sessão expirou. Entre de novo (dados de formulários não salvos são perdidos). |
| Erro ao salvar um formulário | Leia a mensagem em vermelho acima do formulário e corrija o campo indicado. |
| Não aparece uma tela no menu | Seu perfil não tem acesso a ela. Fale com o administrador. |
| Erro que não passa depois de alguns minutos | Avise o administrador. |

---

## 6. Informações técnicas

Esta seção é voltada a quem deseja entender ou executar o projeto.

**Tecnologias:** [Reflex](https://reflex.dev) (Python, frontend e backend) e
[Xano](https://www.xano.com) (banco de dados e API remota).

**Rodar localmente** (Python 3.10+):

```bash
py -m venv .venv
.venv\Scripts\Activate.ps1   # Windows PowerShell
pip install -r requirements.txt
reflex run
```

Acesse `http://localhost:3000`. É necessário configurar a variável
`XANO_API_URL` (veja o guia técnico).

**Documentação complementar:**

- [docs/desenvolvimento.md](docs/desenvolvimento.md) — guia técnico: configuração, variáveis, autorização, interface e convenções.
- [docs/project-overview.md](docs/project-overview.md) — visão geral do sistema.
- [docs/domain-model.md](docs/domain-model.md) — conceitos e relacionamentos do domínio.
- [docs/matriz-permissoes-xano.md](docs/matriz-permissoes-xano.md) — permissões por perfil em cada endpoint.
- [docs/publicacao-reflex-cloud.md](docs/publicacao-reflex-cloud.md) — como publicar o aplicativo.
- [docs/apresentacao/index.html](docs/apresentacao/index.html) — apresentação do sistema (abrir no navegador).
- [AGENTS.md](AGENTS.md) e [openspec/](openspec) — regras de desenvolvimento e histórico de mudanças.
