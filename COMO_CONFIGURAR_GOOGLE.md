# Como Configurar o Google Sheets (5 minutos)

Para que o LeadCapt consiga enviar os leads diretamente para a sua planilha,
voce precisa criar uma "Conta de Servico" no Google Cloud (é gratuito).

## Passo 1: Acessar o Google Cloud Console
1. Acesse: https://console.cloud.google.com/
2. Faca login com a sua conta Google (a mesma da planilha).

## Passo 2: Criar um Projeto
1. No topo da pagina, clique em "Selecionar projeto" > "Novo Projeto".
2. De um nome (ex: "LeadCapt") e clique em "Criar".
3. Selecione o projeto recem-criado.

## Passo 3: Ativar as APIs
1. No menu lateral, va em "APIs e Servicos" > "Biblioteca".
2. Pesquise por "Google Sheets API" e clique em "Ativar".
3. Pesquise por "Google Drive API" e clique em "Ativar".

## Passo 4: Criar a Conta de Servico
1. No menu lateral, va em "APIs e Servicos" > "Credenciais".
2. Clique em "+ Criar Credenciais" > "Conta de servico".
3. De um nome (ex: "leadcapt-bot") e clique em "Concluir".
4. Na lista de Contas de Servico, clique na que voce acabou de criar.
5. Va na aba "Chaves" > "Adicionar Chave" > "Criar nova chave".
6. Escolha o formato "JSON" e clique em "Criar".
7. Um arquivo JSON sera baixado automaticamente.

## Passo 5: Colocar o Arquivo no Projeto
1. Renomeie o arquivo baixado para: credentials.json
2. Mova/copie ele para a pasta do projeto:
   c:\Users\drewg\Downloads\lead-scraper\credentials.json

## Passo 6: Compartilhar a Planilha
1. Abra o arquivo credentials.json e procure o campo "client_email".
   Ele tera algo como: leadcapt-bot@leadcapt-XXXXX.iam.gserviceaccount.com
2. Copie esse email.
3. Abra a sua planilha do Google Sheets.
4. Clique em "Compartilhar" (botao verde no canto superior direito).
5. Cole o email da conta de servico e de permissao de "Editor".
6. Clique em "Enviar".

## Pronto!
Agora o LeadCapt conseguira enviar os leads direto para a sua planilha.
Basta rodar uma captacao normalmente pela interface web.
