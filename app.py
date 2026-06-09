import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
from scraper import run_scraper
from google_sheets import send_leads_to_sheet

# ───────────────────────────── CONFIG ─────────────────────────────
st.set_page_config(
    page_title="LeadCapt | Captação de Leads",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ───────────────────────────── CSS ────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    /* ── Reset & Global ── */
    *, *::before, *::after { box-sizing: border-box; }
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
        font-family: 'Inter', sans-serif !important;
        background: #0a0a0f !important;
        color: #e2e8f0 !important;
    }
    [data-testid="stHeader"] { background: transparent !important; }
    [data-testid="stSidebar"] { background: #111118 !important; }
    
    /* ── Hero Section ── */
    .hero {
        text-align: center;
        padding: 2.5rem 1rem 1.5rem;
    }
    .hero-badge {
        display: inline-block;
        background: linear-gradient(135deg, rgba(99,102,241,.15), rgba(168,85,247,.15));
        border: 1px solid rgba(99,102,241,.25);
        border-radius: 999px;
        padding: .35rem 1rem;
        font-size: .75rem;
        font-weight: 600;
        letter-spacing: .08em;
        text-transform: uppercase;
        color: #a78bfa;
        margin-bottom: 1rem;
    }
    .hero h1 {
        font-size: 2.8rem;
        font-weight: 900;
        background: linear-gradient(135deg, #818cf8, #c084fc, #f472b6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 0 .6rem;
        line-height: 1.15;
    }
    .hero p {
        color: #94a3b8;
        font-size: 1.05rem;
        max-width: 560px;
        margin: 0 auto;
        line-height: 1.6;
    }

    /* ── Glass Card ── */
    .glass-card {
        background: rgba(255,255,255,.03);
        border: 1px solid rgba(255,255,255,.06);
        border-radius: 16px;
        padding: 2rem;
        backdrop-filter: blur(12px);
        margin-bottom: 1.2rem;
    }
    .glass-card h3 {
        font-size: 1.1rem;
        font-weight: 700;
        color: #c4b5fd;
        margin: 0 0 1.2rem;
    }

    /* ── Stat Cards ── */
    .stat-row {
        display: flex;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    .stat-card {
        flex: 1;
        background: linear-gradient(145deg, rgba(99,102,241,.08), rgba(168,85,247,.06));
        border: 1px solid rgba(99,102,241,.12);
        border-radius: 14px;
        padding: 1.4rem;
        text-align: center;
    }
    .stat-card .num {
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .stat-card .label {
        font-size: .8rem;
        color: #94a3b8;
        margin-top: .3rem;
        text-transform: uppercase;
        letter-spacing: .06em;
        font-weight: 600;
    }

    /* ── Streamlit Overrides ── */
    .stTextInput > div > div > input {
        background: rgba(255,255,255,.04) !important;
        border: 1px solid rgba(255,255,255,.1) !important;
        border-radius: 10px !important;
        color: #e2e8f0 !important;
        padding: .75rem 1rem !important;
        font-size: .95rem !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #818cf8 !important;
        box-shadow: 0 0 0 2px rgba(129,140,248,.25) !important;
    }
    .stSlider > div > div > div { color: #818cf8 !important; }

    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 12px !important;
        padding: .85rem 1.5rem !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        letter-spacing: .02em;
        transition: all .25s ease !important;
        box-shadow: 0 4px 20px rgba(99,102,241,.35) !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 28px rgba(99,102,241,.5) !important;
    }
    .stDownloadButton > button {
        width: 100%;
        background: linear-gradient(135deg, #059669, #10b981) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 12px !important;
        padding: .85rem 1.5rem !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        box-shadow: 0 4px 20px rgba(16,185,129,.3) !important;
    }

    /* Table styling */
    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* Status text */
    .status-log {
        background: rgba(0,0,0,.3);
        border: 1px solid rgba(255,255,255,.05);
        border-radius: 10px;
        padding: 1rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: .82rem;
        color: #94a3b8;
        max-height: 220px;
        overflow-y: auto;
        line-height: 1.7;
    }

    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem 0;
        color: #475569;
        font-size: .78rem;
    }
</style>
""", unsafe_allow_html=True)

# ───────────────────────────── HERO ───────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-badge">🎯 Sistema Inteligente de Captação</div>
    <h1>LeadCapt</h1>
    <p>Encontre empresas sem site diretamente do Google Maps.<br>
    Filtrado, separado por nicho e exportado para Excel + Google Sheets automaticamente.</p>
</div>
""", unsafe_allow_html=True)

# ───────────────────────────── FORM ───────────────────────────────
col_left, col_right = st.columns([1.2, 1], gap="large")

with col_left:
    st.markdown('<div class="glass-card"><h3>🔎 Configurar Busca</h3>', unsafe_allow_html=True)
    search_input = st.text_input(
        "Nicho + Localização",
        placeholder="Ex: Academias em Curitiba",
        label_visibility="collapsed",
    )
    max_results = st.slider("Máximo de resultados para analisar", 5, 60, 20, step=5)
    start_btn = st.button("🚀 Iniciar Captação")
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown("""
    <div class="glass-card">
        <h3>📖 Como Funciona</h3>
        <p style="color:#94a3b8;font-size:.9rem;line-height:1.7;">
            <strong style="color:#c4b5fd;">1.</strong> Digite o nicho e a cidade que deseja prospectar.<br>
            <strong style="color:#c4b5fd;">2.</strong> Clique em <em>Iniciar Captação</em>.<br>
            <strong style="color:#c4b5fd;">3.</strong> O robô abrirá o Google Maps em segundo plano.<br>
            <strong style="color:#c4b5fd;">4.</strong> Empresas <strong>sem site</strong> serão filtradas automaticamente.<br>
            <strong style="color:#c4b5fd;">5.</strong> Baixe a planilha Excel com os leads prontos!
        </p>
    </div>
    """, unsafe_allow_html=True)

# ───────────────────────────── ENGINE ─────────────────────────────
if start_btn:
    if not search_input.strip():
        st.error("⚠️ Por favor, digite um termo de busca (ex: Restaurantes em Belo Horizonte)")
    else:
        # Status container
        status_area = st.empty()
        log_lines = []

        def update_status(msg):
            log_lines.append(msg)
            status_area.markdown(
                '<div class="status-log">' + "<br>".join(log_lines) + '</div>',
                unsafe_allow_html=True
            )

        with st.spinner("Robô em execução... acompanhe abaixo ⬇️"):
            leads = run_scraper(search_input.strip(), max_results, status_callback=update_status)

        # ─── Results ───
        if leads:
            df = pd.DataFrame(leads)
            df.rename(columns={
                "Name": "Nome da Empresa",
                "Phone": "Telefone",
                "Address": "Endereço",
                "Category": "Nicho / Categoria",
                "Rating": "Avaliação",
                "Reviews": "Avaliações",
            }, inplace=True)

            # Stats
            st.markdown(f"""
            <div class="stat-row">
                <div class="stat-card">
                    <div class="num">{len(leads)}</div>
                    <div class="label">Leads SEM Site</div>
                </div>
                <div class="stat-card">
                    <div class="num">{df['Telefone'].astype(bool).sum()}</div>
                    <div class="label">Com Telefone</div>
                </div>
                <div class="stat-card">
                    <div class="num">{df['Endereço'].astype(bool).sum()}</div>
                    <div class="label">Com Endereço</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.info("Empresas com site foram descartadas. Empresas ja vistas em buscas anteriores foram puladas automaticamente.")

            # Table
            st.markdown('<div class="glass-card"><h3>Leads Encontrados (somente SEM site)</h3>', unsafe_allow_html=True)
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Downloads
            safe = "".join(c if c.isalnum() else "_" for c in search_input)
            ts = datetime.now().strftime('%Y%m%d_%H%M%S')

            dl_col1, dl_col2 = st.columns(2)

            with dl_col1:
                # Excel download
                buffer = BytesIO()
                df.to_excel(buffer, index=False, engine="openpyxl")
                buffer.seek(0)
                st.download_button(
                    label="📥 Baixar Excel (.xlsx)",
                    data=buffer,
                    file_name=f"leads_{safe}_{ts}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

            with dl_col2:
                # TXT download (Bloco de Notas)
                lines = []
                lines.append("=" * 60)
                lines.append(f"  LEADS CAPTADOS - {search_input.strip()}")
                lines.append(f"  Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
                lines.append("=" * 60)
                lines.append("")
                for i, lead in enumerate(leads, 1):
                    lines.append(f"--- Lead #{i} ---")
                    lines.append(f"  Empresa:   {lead.get('Name', '')}")
                    lines.append(f"  Telefone:  {lead.get('Phone', '') or 'Nao informado'}")
                    lines.append(f"  Endereco:  {lead.get('Address', '') or 'Nao informado'}")
                    lines.append(f"  Nicho:     {lead.get('Category', '')}")
                    lines.append(f"  Avaliacao: {lead.get('Rating', '') or '-'}")
                    lines.append("")
                lines.append("=" * 60)
                lines.append(f"  Total: {len(leads)} leads sem site")
                lines.append("=" * 60)
                txt_content = "\r\n".join(lines)

                st.download_button(
                    label="📝 Baixar Bloco de Notas (.txt)",
                    data=txt_content.encode("utf-8-sig"),
                    file_name=f"leads_{safe}_{ts}.txt",
                    mime="text/plain",
                )

            # ─── Google Sheets ───
            st.markdown('---')
            try:
                sheets_msg = send_leads_to_sheet(leads, search_input.strip())
                st.success(f"📊 {sheets_msg}")
            except FileNotFoundError as e:
                st.warning(f"⚠️ Google Sheets: {e}")
            except Exception as e:
                st.error(f"❌ Erro ao enviar para Google Sheets: {e}")
        else:
            st.warning("Nenhum lead sem site foi encontrado para essa busca. Tente outro nicho ou outra cidade.")

# ───────────────────────────── FOOTER ─────────────────────────────
st.markdown("""
<div class="footer">
    LeadCapt &mdash; Sistema de Captação de Leads via Google Maps &bull; 2026
</div>
""", unsafe_allow_html=True)
