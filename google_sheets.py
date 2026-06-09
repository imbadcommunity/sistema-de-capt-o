import gspread
from google.oauth2.service_account import Credentials
import os

# ID da planilha extraído do link do usuário
SPREADSHEET_ID = "1JEm0uTUdrwCM3zkZpcsxlUV5gLEVwtc5ge13hI46GQ8"
CREDENTIALS_FILE = "credentials.json"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def get_client():
    """Autentica e retorna o cliente gspread."""
    creds_path = os.path.join(os.path.dirname(__file__), CREDENTIALS_FILE)
    if not os.path.exists(creds_path):
        raise FileNotFoundError(
            f"Arquivo '{CREDENTIALS_FILE}' nao encontrado na pasta do projeto.\n"
            "Siga o guia 'COMO_CONFIGURAR_GOOGLE.md' para criar suas credenciais."
        )
    creds = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    return gspread.authorize(creds)


def send_leads_to_sheet(leads: list, search_term: str):
    """
    Envia uma lista de leads para o Google Sheets.
    Cada lead é um dicionário com chaves: Name, Phone, Address, Category, Rating, Reviews.
    Os dados são adicionados na primeira aba da planilha.
    """
    if not leads:
        return "Nenhum lead para enviar."

    client = get_client()
    sheet = client.open_by_key(SPREADSHEET_ID)
    worksheet = sheet.sheet1

    # Verificar se o cabeçalho já existe
    existing = worksheet.get_all_values()
    header = ["Nome da Empresa", "Telefone", "Endereco", "Nicho / Categoria", "Avaliacao", "Avaliacoes", "Termo de Busca"]

    if not existing:
        worksheet.append_row(header, value_input_option="USER_ENTERED")

    # Adicionar cada lead como uma nova linha
    rows = []
    for lead in leads:
        rows.append([
            lead.get("Name", ""),
            lead.get("Phone", ""),
            lead.get("Address", ""),
            lead.get("Category", ""),
            lead.get("Rating", ""),
            lead.get("Reviews", ""),
            search_term,
        ])

    worksheet.append_rows(rows, value_input_option="USER_ENTERED")

    return f"Enviados {len(rows)} leads para o Google Sheets com sucesso!"
