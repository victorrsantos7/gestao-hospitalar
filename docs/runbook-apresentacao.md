# Runbook da apresentação

## 1. Na véspera

1. Conecte o computador à internet.
2. Confira que o arquivo `.env` existe e contém `XANO_API_URL`.
3. Crie um backup externo:

   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\backup_apresentacao.ps1 -DestinationRoot "D:\Backups"
   ```

4. Execute o preflight:

   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\preflight.ps1
   ```

5. Se as credenciais dedicadas estiverem configuradas, execute o smoke test:

   ```powershell
   $env:RUN_XANO_INTEGRATION = "1"
   .\.venv\Scripts\python.exe -m unittest tests.test_xano_integration -v
   Remove-Item Env:RUN_XANO_INTEGRATION
   ```

6. Reinicie o computador e repita o preflight.

## 2. Início da apresentação

1. Feche outros servidores locais.
2. Execute `iniciar_reflex.bat`.
3. Aguarde a mensagem de início.
4. Abra **somente** `http://localhost:3000`.
5. Não abra `http://0.0.0.0:3000`; esse endereço representa escuta de rede,
   não o destino do navegador.

O inicializador executa o preflight, restringe o backend a `127.0.0.1` e grava
o processo Reflex em `logs\reflex.log`. O log da aplicação permanece no caminho
definido por `GESTAO_LOG_FILE`.

## 3. Contas e roteiro funcional

Use somente contas dedicadas:

1. **recepcionista**: Pacientes, Médicos, Convênios e Atendimentos;
2. **médico**: consulta de pacientes/atendimentos e Diagnósticos;
3. **enfermagem_gestao**: Internações, Leitos, Transferências, Histórico e
   Relatórios;
4. **admin**: conferência geral.

Roteiro sugerido:

1. login e painel;
2. cadastro/consulta de paciente;
3. atendimento e diagnóstico;
4. internação, leito e transferência;
5. histórico e relatório de ocupação;
6. logout e demonstração de bloqueio por papel.

## 4. Diagnóstico rápido

### Porta 3000 ocupada

O preflight mostra PID e nome do processo, sem encerrá-lo. Confirme:

```powershell
Get-NetTCPConnection -State Listen -LocalPort 3000
Get-Process -Id <PID>
```

Encerre apenas o processo identificado e somente se tiver certeza de que ele
não é necessário. Nunca encerre processos por nome.

### Xano indisponível

1. Confirme internet e `XANO_API_URL`.
2. Execute novamente `scripts\preflight.ps1 -SkipTests -SkipCompile`.
3. Não tente criar ou editar registros enquanto o serviço estiver instável.
4. Continue a apresentação com telas já explicadas e documentação; não use
   dados reais nem simule sucesso de gravação.

### Dependência ou compilação falhou

Não atualize pacotes no momento da apresentação. Mantenha Reflex 0.9.12. Use o
backup e reinstale exatamente:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Reinício

Feche a janela do Reflex com `Ctrl+C`, confirme que a porta 3000 foi liberada e
execute novamente `iniciar_reflex.bat`. O modo de produção não possui hot
reload.

## 5. Restauração ensaiada

Restaure primeiro em pasta temporária, nunca sobre o projeto:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\restaurar_backup.ps1 `
  -BackupPath "D:\Backups\gestao-hospitalar-AAAAMMDD-HHMMSS" `
  -RestorePath "D:\Restauracao-Teste"
```

O script valida todos os hashes e executa `PRAGMA quick_check` no SQLite. O
workspace Xano exportado não é republicado automaticamente.

## 6. Limite do backup do Xano

O backup padrão usa `xano workspace pull` sem `--env` e sem `--records`. Assim,
ele preserva schema, endpoints e configurações versionáveis, mas **não** os
registros remotos nem variáveis secretas.

Se for necessário recuperar registros, um administrador deve realizar um
export específico pelo painel/API administrativa do Xano, armazená-lo em local
criptografado e controlar acesso conforme a política de dados. Esse export não
deve entrar no Git nem no pacote comum da apresentação.
