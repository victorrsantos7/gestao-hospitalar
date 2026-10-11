# Tasks

## 1. Validadores

- [x] 1.1 Criar validação de nome com suporte a Unicode, espaços, hífen e apóstrofo, rejeitando números e símbolos inválidos; adicionar testes.
- [x] 1.2 Criar normalização e validação de telefone brasileiro para 10 ou 11 dígitos; adicionar testes para fixo, celular, excesso e quantidade insuficiente.
- [x] 1.3 Criar validação de data real não futura; adicionar testes para data válida, inexistente e futura.

## 2. Estado e formulário Reflex

- [x] 2.1 Aplicar máscara de CPF e restringir a entrada normalizada a 11 dígitos sem alterar a validação de dígitos verificadores.
- [x] 2.2 Aplicar máscara de telefone e contato de emergência para os formatos brasileiros de 10/11 dígitos.
- [x] 2.3 Integrar as validações ao evento de cadastro e garantir que entradas inválidas não chamem o Xano.
- [x] 2.4 Ajustar mensagens de erro sem expor payloads ou dados sensíveis.

## 3. Testes e documentação

- [x] 3.1 Adicionar cobertura unitária para os novos validadores e cenários de normalização.
- [x] 3.2 Executar testes, `py_compile` e `reflex compile --dry`.
- [x] 3.3 Validar manualmente máscaras, colagem, entradas inválidas e cadastro válido no navegador.
- [x] 3.4 Atualizar a documentação do cadastro e arquivar a change após a validação.
