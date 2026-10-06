# Domain Model — Sistema de Gestão Hospitalar

Este documento descreve os conceitos fundamentais do domínio do sistema e
seus relacionamentos. Ele representa os **conceitos** do sistema, não
necessariamente as tabelas físicas do banco.

## Visão geral do modelo

Paciente
│
├── Atendimento
│       ├── Diagnóstico
│       └── Internação
│               ├── Leito
│               └── Transferência
│
├── Médico (via Atendimento)
│
└── Convênio (via Atendimento)


## Entidades com consultas passíveis de subquery

O modelo é conceitual e ainda não define consultas SQL implementadas. As
subqueries abaixo são possibilidades derivadas dos relacionamentos e das
regras do domínio. Elas não são obrigatórias: a implementação deve comparar
o plano de execução com alternativas como `JOIN`, `GROUP BY` e `EXISTS`.

### Consultas prioritárias

| Entidade principal | Consulta de negócio | Uso possível de subquery |
| --- | --- | --- |
| Paciente | Listar pacientes que possuem pelo menos um atendimento, diagnóstico ou internação | Usar `EXISTS` para verificar registros relacionados sem duplicar pacientes; também é possível comparar a quantidade de atendimentos com uma média calculada em subquery. |
| Atendimento | Encontrar o último atendimento de cada paciente ou atendimentos acima da média de atendimentos por paciente | Usar subquery correlacionada com `MAX(data)` ou uma subquery agregada para calcular a média. |
| Diagnóstico | Localizar pacientes que receberam determinado código CID ou atendimentos que possuem diagnóstico | Usar `EXISTS` para testar a existência do diagnóstico relacionado ao atendimento ou ao paciente. |
| Internação | Identificar pacientes atualmente internados e pacientes com mais de uma internação | Usar `EXISTS`/`NOT EXISTS` para verificar internação sem data de saída e subquery agregada para contar internações por paciente. |
| Leito | Listar leitos livres, ocupados e possíveis conflitos de ocupação | Usar `EXISTS` para verificar se existe internação ativa vinculada ao leito; `NOT EXISTS` pode identificar leitos sem internação ativa. |
| Transferência | Encontrar a transferência mais recente de cada internação ou internações com múltiplas transferências | Usar subquery correlacionada com `MAX(data)` ou subquery agregada com `COUNT(*)`. |

### Consultas secundárias

As entidades `Médico` e `Convênio` também admitem subqueries, embora seus
casos dependam mais de relatórios:

- **Médico**: listar médicos que realizaram atendimentos acima da média ou
  que atenderam pacientes com determinado diagnóstico. A subquery pode
  calcular a média por médico ou verificar a existência de diagnósticos na
  cadeia `Médico -> Atendimento -> Diagnóstico`.
- **Convênio**: listar convênios utilizados em atendimentos dentro de um
  período ou convênios com quantidade de atendimentos acima de um limite. A
  subquery pode calcular a quantidade por convênio ou testar a existência de
  atendimentos no período.

### Resumo de aplicabilidade

As entidades com uso mais justificável de subquery são **Paciente,
Atendimento, Diagnóstico, Internação, Leito e Transferência**, principalmente
por causa de histórico, existência de registros relacionados, identificação
do registro mais recente e agregações por entidade. **Médico** e **Convênio**
também são compatíveis, mas aparecem sobretudo em consultas analíticas.


## Paciente

Representa a pessoa atendida pelo hospital.

### Principais informações

- nome;
- CPF (único);
- data de nascimento;
- telefone;
- endereço;
- contato de emergência.

### Relacionamentos

- Um paciente pode ter **vários atendimentos**.
- Um paciente pode ter **várias internações** (uma por atendimento que gera
  internação).

### Regras estruturais

- O CPF deve ser único no sistema.

## Médico

Representa o profissional de saúde que atende o paciente.

### Principais informações

- nome;
- CRM (único);
- especialidade;
- telefone.

### Relacionamentos

- Um médico pode realizar **vários atendimentos**.

### Regras estruturais

- O CRM deve ser único no sistema.

## Convênio

Representa o plano de saúde, atendimento particular ou SUS.

### Principais informações

- nome;
- tipo (particular, plano, SUS);
- cobertura.

### Relacionamentos

- Um convênio pode estar vinculado a **vários atendimentos**.

## Atendimento

Representa o registro de uma consulta ou atendimento do paciente.

### Principais informações

- data;
- motivo;
- tipo (consulta, emergência, retorno).

### Relacionamentos

- Um atendimento pertence a **um paciente**.
- Um atendimento é realizado por **um médico**.
- Um atendimento pode estar vinculado a **um convênio**.
- Um atendimento pode ter **vários diagnósticos**.
- Um atendimento pode gerar **no máximo uma internação**.

### Regras estruturais

- Nem todo atendimento gera internação.

## Diagnóstico

Representa o diagnóstico registrado em um atendimento.

### Principais informações

- descrição;
- código CID;
- data.

### Relacionamentos

- Um diagnóstico pertence a **um atendimento**.

## Internação

Representa o período em que o paciente fica internado no hospital.

### Principais informações

- data de entrada;
- data de saída;
- status (internado, alta).

### Relacionamentos

- Uma internação está vinculada a **um atendimento**.
- Uma internação pertence a **um paciente**.
- Uma internação ocupa **um leito**.
- Uma internação pode ter **várias transferências**.

## Leito

Representa a cama/unidade onde o paciente fica internado.

### Principais informações

- número;
- status (livre, ocupado).

### Relacionamentos

- Um leito pode ser ocupado por **várias internações** ao longo do tempo
  (uma por vez).

### Regras estruturais

- Um leito só pode estar ocupado por um paciente por vez.

## Transferência

Representa a movimentação do paciente durante uma internação.

### Principais informações

- data;
- motivo.

### Relacionamentos

- Uma transferência pertence a **uma internação**.

### Regras estruturais

- Uma internação pode ter múltiplas transferências, registrando a
  movimentação do paciente dentro do hospital.

## Usuário do sistema

Representa o funcionário do hospital (recepcionista, médico, equipe de
enfermagem/gestão) que acessa o sistema. É um conceito distinto de
Paciente, Médico e Convênio: não representa a jornada do paciente, mas sim
quem opera o sistema.

### Principais informações

- login (único);
- senha (armazenada apenas como hash);
- papel (recepcionista, médico, enfermagem/gestão).

### Relacionamentos

- Não possui relacionamento direto com Paciente, Atendimento ou demais
  entidades da jornada do paciente nesta fase do projeto.

### Regras estruturais

- O login deve ser único no sistema.
- A senha nunca é armazenada em texto aberto, apenas como hash.
- O campo papel define o perfil de acesso, mas regras de autorização por
  papel ainda não estão implementadas (ver change `autenticacao-login`).
