import logging
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update, Bot, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext

# Configuração de logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Estados da conversação
SENHA, NOME, ID_TELEGRAM, WHATSAPP, USUARIO_TELEGRAM, PLANO, EMAIL, VALOR, DATA_COBRANCA, FORMA_PAGAMENTO = range(10)
SELECIONAR_CAMPO, EDITAR_CAMPO, DADOS_ALTERADOS = range(10, 13)

# Token do Bot do Telegram
TELEGRAM_TOKEN = 'TOKEN BOT AQUI'
PASSWORD = "SUA SENHA AQUI"

# Configuração do Google Sheets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
CREDS = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', SCOPE)
client = gspread.authorize(CREDS)
sheet = client.open_by_url("URL DA SUA PLANINHA AQUI").sheet1

# Inicializa o bot
bot = Bot(TELEGRAM_TOKEN)

def start(update: Update, _: CallbackContext) -> int:
    update.message.reply_text('Por favor, insira a senha para iniciar o registro:')
    return SENHA

def senha(update: Update, context: CallbackContext) -> int:
    if update.message.text == PASSWORD:
        update.message.reply_text('Senha correta. Qual é o seu nome completo?')
        return NOME
    else:
        update.message.reply_text('Senha incorreta. Acesso negado.')
        return ConversationHandler.END

def nome(update: Update, context: CallbackContext) -> int:
    context.user_data['nome'] = update.message.text
    update.message.reply_text('Qual é o seu ID do Telegram?')
    return ID_TELEGRAM

def id_telegram(update: Update, context: CallbackContext) -> int:
    context.user_data['id_telegram'] = update.message.text
    update.message.reply_text('Qual é o seu WhatsApp?')
    return WHATSAPP

def whatsapp(update: Update, context: CallbackContext) -> int:
    context.user_data['whatsapp'] = update.message.text
    update.message.reply_text('Qual é o seu usuário do Telegram?')
    return USUARIO_TELEGRAM

def usuario_telegram(update: Update, context: CallbackContext) -> int:
    context.user_data['usuario_telegram'] = update.message.text
    update.message.reply_text('Qual é o plano contratado?')
    return PLANO

def plano(update: Update, context: CallbackContext) -> int:
    context.user_data['plano'] = update.message.text
    update.message.reply_text('Qual é o seu e-mail?')
    return EMAIL

def email(update: Update, context: CallbackContext) -> int:
    context.user_data['email'] = update.message.text
    update.message.reply_text('Qual é o valor?')
    return VALOR

def valor(update: Update, context: CallbackContext) -> int:
    context.user_data['valor'] = update.message.text
    update.message.reply_text('Qual é a data de cobrança?')
    return DATA_COBRANCA

def data_cobranca(update: Update, context: CallbackContext) -> int:
    context.user_data['data_cobranca'] = update.message.text
    update.message.reply_text('Qual é a forma de pagamento?')
    return FORMA_PAGAMENTO

def forma_pagamento(update: Update, context: CallbackContext) -> int:
    context.user_data['forma_pagamento'] = update.message.text
    # Salva os dados no Google Sheets
    user_data = context.user_data
    sheet.append_row([user_data['nome'], user_data['id_telegram'], user_data['whatsapp'],
                      user_data['usuario_telegram'], user_data['plano'], user_data['email'],
                      user_data['valor'], user_data['data_cobranca'],
                      user_data['forma_pagamento']])
    update.message.reply_text('Registro completo!')
    return ConversationHandler.END

def cancel(update: Update, _: CallbackContext) -> int:
    update.message.reply_text('Registro cancelado.')
    return ConversationHandler.END

def consultar(update: Update, context: CallbackContext) -> None:
    if not context.args:
        update.message.reply_text('Por favor, forneça o usuário do Telegram para consulta. Exemplo: /consultar @usuario')
        return

    usuario_consulta = context.args[0].lstrip('@')
    registros = sheet.get_all_records()

    for registro in registros:
        if registro.get('USUARIO_TELEGRAM', '').lstrip('@').lower() == usuario_consulta.lower():
            resposta = (
                f"Nome: {registro.get('NOME', 'Não disponível')}\n"
                f"ID Telegram: {registro.get('ID TELEGRAM', 'Não disponível')}\n"
                f"WhatsApp: {registro.get('WHATSAPP', 'Não disponível')}\n"
                f"Usuário Telegram: @{registro.get('USUARIO_TELEGRAM', 'Não disponível')}\n"
                f"Plano: {registro.get('PLANO', 'Não disponível')}\n"
                f"Email: {registro.get('EMAIL', 'Não disponível')}\n"
                f"Valor: {registro.get('VALOR', 'Não disponível')}\n"
                f"Data Cobrança: {registro.get('DATA COBRANÇA', 'Não disponível')}\n"
                f"Forma de Pagamento: {registro.get('FORMA DE PAGAMENTO', 'Não disponível')}"
            )
            update.message.reply_text(resposta)
            return

    update.message.reply_text("Usuário não encontrado.")

def cobrar(update: Update, context: CallbackContext) -> None:
    if not context.args:
        update.message.reply_text('Por favor, forneça o usuário do Telegram para cobrança. Exemplo: /cobrar @usuario')
        return

    usuario_cobranca = context.args[0].lstrip('@')
    registros = sheet.get_all_records()

    for registro in registros:
        if registro.get('USUARIO_TELEGRAM', '').lstrip('@').lower() == usuario_cobranca.lower():
            chat_id = registro.get('ID TELEGRAM')
            if chat_id:
                try:
                    bot.send_message(chat_id=chat_id, text="Sua assinatura está prestes a expirar...")
                    update.message.reply_text(f"Mensagem de cobrança enviada para @{usuario_cobranca}.")
                except Exception as e:
                    logger.error(f"Erro ao enviar mensagem para @{usuario_cobranca}: {e}")
                    update.message.reply_text("Erro ao enviar a mensagem.")
            else:
                update.message.reply_text(f"Usuário @{usuario_cobranca} não tem um chat ID registrado.")
            return

    update.message.reply_text(f"Usuário @{usuario_cobranca} não encontrado.")

def verificacao(update: Update, context: CallbackContext) -> None:
    hoje = datetime.datetime.now().strftime("%d/%m/%Y")
    # Passando os cabeçalhos esperados para a função get_all_records
    registros = sheet.get_all_records(expected_headers=["NOME", "ID TELEGRAM", "WHATSAPP", "USUARIO_TELEGRAM", "PLANO", "EMAIL", "VALOR", "DATA COBRANÇA", "FORMA DE PAGAMENTO"])
    usuarios_a_expirar = []

    for registro in registros:
        data_cobranca = registro.get("DATA COBRANÇA", "")
        if data_cobranca == hoje:
            info_usuario = registro.get('USUARIO_TELEGRAM', 'Usuário sem nome')
            usuarios_a_expirar.append(info_usuario)

    if usuarios_a_expirar:
        mensagem = "Usuários com assinatura expirando hoje:\n" + "\n".join(usuarios_a_expirar)
    else:
        mensagem = "Não há assinaturas expirando hoje."

    update.message.reply_text(mensagem)

def editar(update: Update, context: CallbackContext) -> int:
    if not context.args:
        update.message.reply_text('Por favor, forneça o usuário do Telegram para editar. Exemplo: /editar @usuario')
        return ConversationHandler.END

    usuario_editar = context.args[0].lstrip('@')
    registros = sheet.get_all_records()

    for registro in registros:
        if registro.get('USUARIO_TELEGRAM', '').lstrip('@').lower() == usuario_editar.lower():
            context.user_data['usuario_editar'] = usuario_editar
            context.user_data['registros'] = registros
            campos = [
                'Nome', 'ID Telegram', 'WhatsApp', 'Plano', 'Email', 'Valor',
                'Data Cobrança', 'Forma de Pagamento'
            ]
            teclado = [[campo] for campo in campos]
            update.message.reply_text('Selecione o campo que deseja editar:', reply_markup=ReplyKeyboardMarkup(teclado, one_time_keyboard=True))
            return SELECIONAR_CAMPO

    update.message.reply_text(f"Usuário @{usuario_editar} não encontrado.")
    return ConversationHandler.END

def selecionar_campo(update: Update, context: CallbackContext) -> int:
    novo_valor = update.message.text
    context.user_data['campo_editar'] = novo_valor
    update.message.reply_text(f'Você selecionou editar o campo: {novo_valor}. Por favor, envie o novo valor.')
    return EDITAR_CAMPO

def editar_campo(update: Update, context: CallbackContext) -> int:
    novo_valor = update.message.text
    usuario_editar = context.user_data['usuario_editar']
    campo_editar = context.user_data['campo_editar']
    registros = context.user_data['registros']

    for registro in registros:
        if registro.get('USUARIO_TELEGRAM', '').lstrip('@').lower() == usuario_editar.lower():
            registro[campo_editar.upper()] = novo_valor
            sheet.update_cell(registros.index(registro) + 2, list(registro.keys()).index(campo_editar.upper()) + 1, novo_valor)
            update.message.reply_text('DADOS ALTERADOS COM SUCESSO')
            break

    return ConversationHandler.END

def main() -> None:
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('registrar', start), CommandHandler('editar', editar)],
        states={
            SENHA: [MessageHandler(Filters.text & ~Filters.command, senha)],
            NOME: [MessageHandler(Filters.text & ~Filters.command, nome)],
            ID_TELEGRAM: [MessageHandler(Filters.text & ~Filters.command, id_telegram)],
            WHATSAPP: [MessageHandler(Filters.text & ~Filters.command, whatsapp)],
            USUARIO_TELEGRAM: [MessageHandler(Filters.text & ~Filters.command, usuario_telegram)],
            PLANO: [MessageHandler(Filters.text & ~Filters.command, plano)],
            EMAIL: [MessageHandler(Filters.text & ~Filters.command, email)],
            VALOR: [MessageHandler(Filters.text & ~Filters.command, valor)],
            DATA_COBRANCA: [MessageHandler(Filters.text & ~Filters.command, data_cobranca)],
            FORMA_PAGAMENTO: [MessageHandler(Filters.text & ~Filters.command, forma_pagamento)],
            SELECIONAR_CAMPO: [MessageHandler(Filters.regex(r'^(Nome|ID Telegram|WhatsApp|Plano|Email|Valor|Data Cobrança|Forma de Pagamento)$'), selecionar_campo)],
            EDITAR_CAMPO: [MessageHandler(Filters.text & ~Filters.command, editar_campo)]
        },
        fallbacks=[CommandHandler('cancelar', cancel)]
    )

    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler("consultar", consultar, pass_args=True))
    dp.add_handler(CommandHandler("cobrar", cobrar, pass_args=True))
    dp.add_handler(CommandHandler("verificacao", verificacao))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
