import pandas as pd
from sqlalchemy import create_engine
import os

# Conexão com o Banco de Dados
db_url = 'postgresql://postgres:2525@localhost:5432/postgres'
engine = create_engine(db_url)

# Extração e Carga dos dados
file_path = os.path.join('data', 'Superstore.csv')

print('Iniciando a leitura do arquivo CSV...')
chunk_interator = pd.read_csv(file_path, chunksize=10000, encoding='latin1')

print('Aquivo lido com sucesso! Iniciando a carga dos dados para o banco...')

for i, chunk in enumerate(chunk_interator):
    print(f'Carregando chunk {i+1}')

    if i == 0:
        chunk.to_sql('sales_data', con=engine, if_exists='replace', index=False)
    else:
        chunk.to_sql('sales_data', con=engine, if_exists='append', index=False)
    
print("Carga de dados concluída com sucesso!")
print("Os dados do Superstore agora estão na tabela 'sales_data' do seu banco PostgreSQL.")


