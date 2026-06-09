import pandas as pd
from datetime import datetime
import os

def export_to_excel(leads: list, search_term: str):
    """
    Recebe uma lista de dicionários (leads) e exporta para um arquivo Excel (.xlsx).
    Cada linha representará uma empresa.
    """
    if not leads:
        print(f"Nenhum lead sem site encontrado para a busca '{search_term}'.")
        return

    # Limpar caracteres não permitidos no nome do arquivo
    safe_term = "".join(c if c.isalnum() else "_" for c in search_term)
    
    # Criar diretório "exports" se não existir
    if not os.path.exists("exports"):
        os.makedirs("exports")
        
    filename = f"exports/{safe_term}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    # Converter a lista de dicionários em um DataFrame do pandas
    df = pd.DataFrame(leads)
    
    # Organizar e renomear colunas, se existirem
    columns_order = ["Name", "Phone", "Address", "Category", "Rating", "Reviews"]
    existing_cols = [col for col in columns_order if col in df.columns]
    
    # Adicionar colunas faltantes se necessário
    for col in columns_order:
        if col not in df.columns:
            df[col] = ""
            
    df = df[columns_order]
    
    # Renomeando para português no Excel
    df.rename(columns={
        "Name": "Nome da Empresa",
        "Phone": "Telefone",
        "Address": "Endereço",
        "Category": "Nicho / Categoria",
        "Rating": "Avaliação Média",
        "Reviews": "Qtd. Avaliações"
    }, inplace=True)
    
    # Exportar para Excel
    df.to_excel(filename, index=False, engine='openpyxl')
    print(f"✅ Exportado com sucesso: {filename} ({len(leads)} leads)")
