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