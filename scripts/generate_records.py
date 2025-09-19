#%%
import pandas as pd
import recordlinkage
from recordlinkage.index import SortedNeighbourhood
from numpy import nan
import time
from generate_data import gerar_dataframe
import os

#%%
now = int(time.time())

############################# SETTINGS ###################################
WINDOW = 131
JOBS = -1
THRESHOLD = 0.75
DATA_LENGTH = 1000*30
##########################################################################

df1 = gerar_dataframe(DATA_LENGTH, id_inicio=1)
df2 = gerar_dataframe(DATA_LENGTH, id_inicio=1)
df3 = gerar_dataframe(DATA_LENGTH, id_inicio=1)


df1.loc[:, 'id'] = 'projudi_' + df1['id'].astype(str)
df2.loc[:, 'id'] = 'bnmp_' + df2['id'].astype(str)
df3.loc[:, 'id'] = 'goiaspen_' + df3['id'].astype(str)

#%%
def preprocess(df):
    df = df.copy()
    # df['data_nascimento'] = pd.to_datetime(df['data_nascimento'], dayfirst=True).dt.strftime('%Y%m%d')
    return df

df1_clean = preprocess(df1)
df2_clean = preprocess(df2)
df3_clean = preprocess(df3)

#%%
def create_final_result(df1, df2, matches):
    df1_reset = df1.reset_index()
    df2_reset = df2.reset_index()

    df1_reset['index_1'] = df1.index
    df2_reset['index_2'] = df2.index

    matches = matches.reset_index()

    final_df = matches.merge(
        df1_reset,
        left_on='level_0',
        right_on='index_1',
        how='left'
    ).merge(
        df2_reset,
        left_on='level_1',
        right_on='index_2',
        how='left'
    )
    final_df = final_df.sort_values(by=['total_score', 'nome_score', 'mae_score'], ascending=False)
    return final_df

df_full = pd.concat([df1_clean, df2_clean, df3_clean]).reset_index(drop=True)

indexer = recordlinkage.Index()
indexer.add(SortedNeighbourhood('data_nascimento', window=WINDOW))
indexer.block(left_on='nome', right_on='nome')

candidate_pairs = indexer.index(df_full)

compare = recordlinkage.Compare(n_jobs=JOBS)
compare.string('nome', 'nome', method='levenshtein', label='nome_score')
compare.string('nome_mae', 'nome_mae', method='levenshtein', label='mae_score')
compare.string('data_nascimento', 'data_nascimento', label='nascimento_score')

features = compare.compute(candidate_pairs, df_full)


features['total_score'] = (0.5 * features['nome_score'] +
                          0.3 * features['mae_score'] +
                          0.2 * features['nascimento_score'])

matches = features[features['total_score'] >= THRESHOLD]
df_matches = create_final_result(df_full, df_full, matches)
df_matches_cleaned = df_matches[['id_x', 'id_y', 'total_score', 'nome_score','mae_score','nascimento_score', 'nome_x', 'nome_y',
                                'nome_mae_x', 'nome_mae_y',
                                'data_nascimento_x', 'data_nascimento_y']]


df_matches_all = df_matches_cleaned[df_matches_cleaned['id_x'] != df_matches_cleaned['id_y']].sort_values(by=['nome_x'], ascending=True).reset_index(drop=True)
df = df_matches_all.copy()
df.to_pickle('data/df_no_cross.pkl')

print(f"Total de matches encontrados: {len(df_matches_cleaned)}")
now_ = int(time.time() - now)
print('Tempo gasto:', now_)
print('WINDOW:',WINDOW)
print('JOBS:',JOBS)
print('Tarefa finalizada.')


count = 0
def take(df, name):
    for i, row in df.iterrows():
        global count
        id_x = str(row['id'])
        count += 1
        print(count,'/',len(df), '/', id_x)
        df.loc[i, 'Encontrado'] = 'Sim' if id_x in df_ids else 'Nao'
        
    count = 0
    return df


df['score_total'] = df['total_score']
df = df[df['score_total'] >= THRESHOLD]

df_ids = df['id_x'].tolist() + df['id_y'].tolist()
df2 = take(df2, 'bnmp')
df1 = take(df1, 'projudi')
df3 = take(df3, 'goiaspen')

df2.to_pickle('data/df2.pkl')
df1.to_pickle('data/df1.pkl')
df3.to_pickle('data/df3.pkl')