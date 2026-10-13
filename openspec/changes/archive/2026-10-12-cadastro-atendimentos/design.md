# Design

## Context

O projeto usa Reflex no frontend e um cliente HTTP compartilhado para consumir
endpoints privados do Xano. Pacientes, medicos e convenios ja possuem cadastro
e consulta remotos, e a matriz fixa ja reserva `atendimentos` para recepcionista
e medico, com acesso total para admin. A nova entidade precisa referenciar
registros existentes sem duplicar seus dados.

## Goals / Non-Goals

**Goals:**

- Criar no Xano a tabela de atendimentos com referencias para paciente, medico e
  convenio opcional.
- Expor criacao e listagem por endpoints privados, protegidos por `usuarios_hospital`.
- Reutilizar o cliente Xano, o token de sessao e o padrao de tratamento de erros.
- Adicionar estado, validacao e tela Reflex para cadastro e consulta.
- Cobrir validacao, autorizacao e transporte com testes automatizados.

**Non-Goals:**

- Alterar os cadastros de pacientes, medicos ou convenios.
- Criar diagnosticos, internacoes, leitos, transferencias ou historico.
- Implementar edicao ou exclusao de atendimentos nesta primeira fatia.
- Permitir que enfermagem/gestao consulte atendimentos antes da change de historico.

## Decisions

1. **Tabela remota dedicada no Xano.**
   O atendimento sera persistido em uma tabela propria com IDs de paciente,
   medico e convenio, data, motivo e tipo. Isso preserva a normalizacao e deixa
   os relacionamentos prontos para diagnosticos e internacoes. Uma tabela local
   SQLite foi descartada porque os fluxos concluidos ja usam Xano como fonte
   remota.

2. **Endpoints de criacao, listagem e consulta detalhada.**
   O cliente tera operacoes correspondentes a `POST /attendimentos`,
   `GET /attendimentos` e `GET /attendimentos/{id}`, com o token bruto da
   sessao no cabecalho conforme o comportamento ja validado no Xano. A
   listagem padrao nao enviara parametros de paginacao, mantendo o contrato
   funcional existente; paginacao explicita podera ser adicionada depois.

3. **Autorizacao em duas camadas.**
   A interface ocultara operacoes nao permitidas pela matriz, mas cada endpoint
   tambem tera precondition verificando `usuarios_hospital` e o papel. A
   autorizacao no Xano e a fonte de seguranca contra chamadas diretas.

4. **Validacao antes do envio e no backend.**
   O State normalizara campos de texto e verificara formato, tipo e obrigatorios
   para feedback imediato. O endpoint repetira as regras e validara a existencia
   das referencias, evitando confiar no cliente.

5. **Formulario com selecao de referencias carregadas.**
   A tela usara as listagens protegidas de pacientes, medicos e convenios para
   oferecer selecao por identificador e nome. O convenio tera opcao vazia. A
   listagem de atendimentos exibira os dados necessarios para identificacao sem
   incluir token, senha ou payload bruto de erro.

## Risks / Trade-offs

- **Referencias removidas ou inconsistentes** -> o endpoint valida cada ID antes
  de persistir e retorna erro sem gravacao parcial.
- **Falha do Xano durante o cadastro** -> o cliente nao fara retry automatico em
  escrita e o State exibira mensagem generica sem confirmar sucesso.
- **Lista de selecoes desatualizada** -> a tela recarrega referencias antes do
  uso e trata referencias rejeitadas pelo backend como erro de validacao.
- **Divergencia entre matriz local e preconditions Xano** -> os papeis e o
  recurso serao cobertos por testes e revisados junto com a publicacao dos
  endpoints.

## Migration Plan

1. Criar a tabela e os endpoints privados no Xano, testar cada contrato e
   publicar no ambiente live.
2. Implementar cliente, validadores, State, tela e testes locais.
3. Executar testes, compilacao Reflex e validacao estrita do OpenSpec.
4. Fazer validacao manual dos papeis autorizados e negados antes do archive.
5. Em caso de falha, retirar a rota/tela local e despublicar os endpoints; a
   tabela pode permanecer vazia sem afetar os modulos existentes.