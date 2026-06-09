import os
from scraper import run_scraper
from exporter import export_to_excel

def main():
    print("="*50)
    print("🚀 SISTEMA DE CAPTAÇÃO DE LEADS (Google Maps)")
    print("Filtro: Apenas empresas SEM SITE")
    print("="*50)
    
    # Ler os nichos/buscas do arquivo searches.txt
    searches_file = "searches.txt"
    if not os.path.exists(searches_file):
        print(f"[!] Erro: Arquivo {searches_file} não encontrado.")
        print("Crie um arquivo 'searches.txt' e coloque um termo de busca por linha.")
        return
        
    with open(searches_file, "r", encoding="utf-8") as f:
        searches = [line.strip() for line in f if line.strip()]
        
    if not searches:
        print(f"[!] O arquivo {searches_file} está vazio.")
        return
        
    print(f"[*] {len(searches)} buscas encontradas para processar.\n")
    
    for search_term in searches:
        try:
            # 1. Executar o scraper
            leads = run_scraper(search_term)
            
            # 2. Exportar os resultados
            if leads:
                export_to_excel(leads, search_term)
            else:
                print(f"[-] Sem leads viáveis para exportar em '{search_term}'.")
                
        except Exception as e:
            print(f"[!] Erro crítico ao processar '{search_term}': {e}")
            
        print("-" * 50)
        
    print("\n✅ Processo finalizado com sucesso!")

if __name__ == "__main__":
    main()
