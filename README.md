

# Telegram User Management Bot :robot:

Um bot do Telegram para registro e gerenciamento de usuários.

## Descrição

Este bot permite aos usuários se registrarem e gerencia suas informações em uma planilha do Google Sheets.

## Tecnologias Utilizadas

- Python
- Telegram Bot API
- gspread (Google Sheets API)
- oauth2client

## Como Usar

1. Clone o repositório.
2. Instale as dependências usando `pip install -r requirements.txt`.
3. Configure as credenciais do Google Sheets.
4. Execute o bot usando `python bot.py`.

## Exemplo de Uso

- `/registrar` - Inicia o processo de registro de um novo usuário.
- `/editar` - Inicia o processo de edição das informações de um usuário existente.
- `/consultar @username` - Consulta as informações de um usuário.
- `/verificacao` - Verifica as assinaturas expirando hoje.

## Contribuição

Contribuições são bem-vindas! Por favor, abra uma issue antes de enviar um pull request.

## Licença

Este projeto está licenciado sob a [MIT License](LICENSE).
