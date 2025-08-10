import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px

# --- CONFIGURAÇÃO DA PÁGINA ---
# Usar o modo 'wide' para aproveitar melhor o espaço da tela
st.set_page_config(layout='wide')

# --- TÍTULO DO DASHBOARD ---
st.title("Dashboard de Vendas Superstore 📈")

# --- FUNÇÃO PARA CARREGAR OS DADOS ---
# Usamos o cache do Streamlit para não precisar recarregar os dados do banco a cada interação.
@st.cache_data
def load_data():
    """
    Função para conectar ao banco de dados Supabase de forma segura
    e carregar a tabela de vendas.
    """
    # Monta a URL de conexão a partir dos "secrets" configurados no Streamlit Cloud
    db_url = (
        f"postgresql://{st.secrets.database.user}:{st.secrets.database.password}"
        f"@{st.secrets.database.host}:{st.secrets.database.port}/{st.secrets.database.dbname}"
    )
    
    # Cria a "engine" de conexão com o banco
    engine = create_engine(db_url)
    
    # Lê a tabela 'clean_sales_data' e a carrega em um DataFrame do pandas
    df = pd.read_sql_table('clean_sales_data', engine)
    
    # Garante que as colunas de data estão no formato datetime
    df['order_date'] = pd.to_datetime(df['order_date'])
    df['ship_date'] = pd.to_datetime(df['ship_date'])
    return df

# --- EXECUÇÃO PRINCIPAL E TRATAMENTO DE ERROS ---
try:
    df = load_data()

    # --- BARRA LATERAL (SIDEBAR) COM FILTROS ---
    st.sidebar.header("Filtros do Dashboard")
    
    # Filtro por Região
    # O 'multiselect' permite que o usuário escolha uma ou mais regiões
    selected_regions = st.sidebar.multiselect(
        "Selecione a Região",
        options=df['region'].unique(),
        default=df['region'].unique() # Por padrão, todas as regiões são selecionadas
    )

    # Filtro por Categoria de Produto
    selected_categories = st.sidebar.multiselect(
        "Selecione a Categoria",
        options=df['category'].unique(),
        default=df['category'].unique()
    )

    # Aplica os filtros ao DataFrame
    # Apenas as linhas que correspondem às regiões E categorias selecionadas serão mantidas
    df_filtrado = df[
        df['region'].isin(selected_regions) &
        df['category'].isin(selected_categories)
    ]

    # --- MÉTRICAS PRINCIPAIS (KPIs) ---
    st.subheader("Métricas Principais")
    
    # Calcula os KPIs com base nos dados filtrados
    total_vendas = df_filtrado['sales'].sum()
    media_vendas = df_filtrado['sales'].mean()
    total_pedidos = df_filtrado['order_id'].nunique()

    # Organiza os KPIs em colunas para uma melhor visualização
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Vendas", f"R$ {total_vendas:,.2f}")
    col2.metric("Venda Média por Pedido", f"R$ {media_vendas:,.2f}")
    col3.metric("Total de Pedidos", f"{total_pedidos}")
    
    st.markdown("---") # Linha divisória

    # --- GRÁFICOS ---
    st.subheader("Visualizações")
    
    # Gráfico de Vendas por Categoria
    vendas_por_categoria = df_filtrado.groupby('category')['sales'].sum().sort_values(ascending=False)
    fig_cat = px.bar(
        vendas_por_categoria,
        x=vendas_por_categoria.index,
        y='sales',
        title='Vendas Totais por Categoria',
        labels={'sales': 'Total de Vendas', 'category': 'Categoria'},
        text_auto='.2s'
    )
    st.plotly_chart(fig_cat, use_container_width=True)

    # --- TABELA DE DADOS ---
    st.subheader("Dados Detalhados")
    st.dataframe(df_filtrado)

except Exception as e:
    st.error(f"Ocorreu um erro ao carregar o dashboard: {e}")
    st.warning("Verifique se os 'Secrets' foram configurados corretamente no Streamlit Cloud.")