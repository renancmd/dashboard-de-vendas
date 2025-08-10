import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Dashboard de Vendas",
    page_icon="📊",
    layout="wide"
)

# --- CONEXÃO COM O BANCO DE DADOS ---
db_url = 'postgresql://postgres:minhasenha@localhost:5432/postgres'
engine = create_engine(db_url)

# --- FUNÇÃO PARA CARREGAR DADOS (COM CACHE) ---
@st.cache_data
def load_data():
    df = pd.read_sql_table('clean_sales_data', engine)
    return df
df = load_data()

# --- BARRA LATERAL DE FILTROS (SIDEBAR) ---
st.sidebar.header("Filtros")

# Filtro de Região
selected_regions = st.sidebar.multiselect(
    "Selecione a Região",
    df['region'].unique(),
    default=df['region'].unique() # Por padrão, todas as regiões são selecionadas
)

# Filtro de Categoria
selected_categories = st.sidebar.multiselect(
    "Selecione a Categoria",
    df['category'].unique(),
    default=df['category'].unique()
)

# Filtrando o DataFrame com base nas seleções
df_filtered = df[
    df['region'].isin(selected_regions) &
    df['category'].isin(selected_categories)
]

# --- TÍTULO PRINCIPAL ---
st.title("📊 Dashboard de Análise de Vendas")
st.markdown("---") # Adiciona uma linha horizontal

# --- MÉTRICAS PRINCIPAIS (KPIs) ---
total_sales = df_filtered['sales'].sum()
total_orders = df_filtered['order_id'].nunique() # nunique() conta valores únicos

# Usamos st.columns para organizar as métricas lado a lado
col1, col2 = st.columns(2)
col1.metric("Vendas Totais", f"R$ {total_sales:,.2f}")
col2.metric("Total de Pedidos", f"{total_orders}")

st.markdown("---")

# --- GRÁFICOS ---

# Gráfico 1: Vendas ao longo do tempo (Gráfico de Linha)
st.subheader("Vendas ao Longo do Tempo")
sales_over_time = df_filtered.groupby('order_year_month')['sales'].sum().reset_index()
fig_line = px.line(
    sales_over_time,
    x='order_year_month',
    y='sales',
    title='Evolução das Vendas',
    labels={'order_year_month': 'Mês/Ano', 'sales': 'Vendas (R$)'}
)
st.plotly_chart(fig_line, use_container_width=True)

# Gráfico 2: Vendas por Sub-Categoria (Gráfico de Barras)
st.subheader("Vendas por Sub-Categoria")
sales_by_subcategory = df_filtered.groupby('sub_category')['sales'].sum().sort_values(ascending=False).reset_index()
fig_bar = px.bar(
    sales_by_subcategory,
    x='sales',
    y='sub_category',
    orientation='h',
    title='Top Sub-Categorias por Vendas',
    labels={'sub_category': 'Sub-Categoria', 'sales': 'Vendas (R$)'},
    text_auto=True
)
st.plotly_chart(fig_bar, use_container_width=True)


# --- EXIBINDO OS DADOS FILTRADOS ---
st.subheader("Dados Detalhados")
st.dataframe(df_filtered)