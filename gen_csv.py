import json
import pandas as pd


def drop(d, keys):
    res = {**d}
    for key in keys:
        del res[key]
    return res

def load_standings(file_name):
    with open(file_name, encoding="utf8") as f:
        j = json.load(f)
    s = j['StandingsData']
    
    # filter and flatten
    s = list(filter(lambda x: x['TotalResult']['Count'] > 0, s))
    s = list(map(lambda x: {**x, **x['TotalResult']}, s))
    del_keys = ['TotalResult', 'TaskResults']
    del_keys += ['UserName', 'UserIsDeleted']
    del_keys += ['OldRating', 'IsRated', 'IsTeam']
    del_keys += ['Competitions', 'AtCoderRank', 'Frozen']
    del_keys += ['Additional', 'Penalty', 'Accepted']
    s = list(map(lambda x: drop(x, del_keys), s))
    
    df = pd.DataFrame.from_records(s)
    df['Score'] = df['Score'] // 100
    df['Elapsed'] = df['Elapsed'] // 1000000000 # seconds
    return df

df_prov = load_standings('provisional.json')
df_prov['MeanScore'] = df_prov['Score'] / 50.0 / 1e9 * 100

df_final = load_standings('final.json')
df_final['MeanScore'] = df_final['Score'] / 1000.0 / 1e9 * 100

df = pd.merge(df_final, df_prov, on=['UserScreenName'],
              how='inner', suffixes=['', '_provisional'])
df = df.drop(['Affiliation_provisional',
              'Country_provisional',
              'Count_provisional',
              'Rating_provisional',
              'Elapsed_provisional'
             ], axis=1)

df['Rank_delta'] = df['Rank_provisional'] - df['Rank']
df['MeanScore_delta'] = (df['MeanScore'] - df['MeanScore_provisional'])

df.to_csv('standings.csv', index=False)
