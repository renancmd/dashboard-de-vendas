import pandas as pd
from sqlalchemy import create_engine

# --- CONEXÃO COM O BANCO DE DADOS ---
db_url = 'postgresql://postgres:minhasenha@localhost:5432/postgres'
engine = create_engine(db_url)

print("Conectando ao banco e lendo a tabela 'sales_data'...")
df = pd.read_sql_table('sales_data', engine)

print("Dados lidos com sucesso. Iniciando transformações...")

# --- TRANSFORMAÇÕES DOS DADOS ---

# 1. Renomear colunas para um formato padrão (lowercase_com_underscore)
print("Renomeando colunas...")
df.columns = [col.lower().replace(' ', '_').replace('-', '_') for col in df.columns]

# 2. Converter colunas de data para o tipo datetime
print("Convertendo tipos de dados de data...")
# O formato 'mixed' ajuda o pandas a inferir o formato correto de forma mais flexível
df['order_date'] = pd.to_datetime(df['order_date'], format='mixed')
df['ship_date'] = pd.to_datetime(df['ship_date'], format='mixed')


# 3. Extrair informações úteis da data, como ano e mês
print("Criando novas colunas de data (ano_mes)...")
df['order_year_month'] = df['order_date'].dt.to_period('M').astype(str)

# 4. Garantir que os tipos de dados numéricos estão corretos
print("Limpando e convertendo colunas numéricas...")
# CORREÇÃO: Ajustamos a lista para incluir apenas a coluna numérica 'sales' que existe no nosso dataset.
numeric_cols = ['sales']
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Remove linhas onde os valores de 'sales' são nulos após a conversão
df.dropna(subset=numeric_cols, inplace=True)


# --- CARGA DA TABELA TRANSFORMADA ---
print("Transformações concluídas. Carregando a tabela 'clean_sales_data' no banco...")
df.to_sql('clean_sales_data', con=engine, if_exists='replace', index=False)

print("Tabela 'clean_sales_data' carregada com sucesso!")
print("O processo de transformação está completo.")