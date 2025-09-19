#%%
from dash import html, Input, Output, State, ctx, dcc
import dash
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
import pandas as pd
import os


def formatar_data(df):
    if 'data_nascimento' in df.columns:
        df['data_nascimento'] = pd.to_datetime(df['data_nascimento'], errors='coerce').dt.strftime('%d/%m/%Y')
    return df


try:
    df1 = formatar_data(pd.read_pickle('data/df1.pkl')).sort_values('nome')
    df1['id'] = df1['id'].apply(lambda x: int(x.split('_')[1]))

except Exception as e:
    print(f"Error loading PROJUDI data: {e}")
    df1 = pd.DataFrame(columns=['id', 'nome', 'nome_mae', 'data_nascimento', 'sexo', 'numero_cpf'])

try:
    df2 = formatar_data(pd.read_pickle('data/df2.pkl')).sort_values('nome')
    df2['id'] = df2['id'].apply(lambda x: int(x.split('_')[1]))
except Exception as e:
    print(f"Error loading BNMP data: {e}")
    df2 = pd.DataFrame(columns=['id', 'nome', 'nome_mae', 'data_nascimento', 'sexo', 'numero_cpf'])

try:
    df3 = formatar_data(pd.read_pickle('data/df3.pkl')).sort_values('nome')
    df3['id'] = df3['id'].apply(lambda x: int(x.split('_')[1]))
except Exception as e:
    print(f"Error loading GOIASPEN data: {e}")
    df3 = pd.DataFrame(columns=['id', 'nome', 'nome_mae', 'data_nascimento', 'sexo', 'numero_cpf'])

try:
    df_principal = formatar_data(pd.read_pickle('data/df_no_cross.pkl'))
    if 'total_score' in df_principal.columns:
        df_principal['score_total'] = df_principal['total_score']
    df_principal = df_principal[df_principal['score_total'] >= 0.75]
except Exception as e:
    print(f"Error loading principal data: {e}")
    df_principal = pd.DataFrame(columns=['id_x', 'id_y', 'score_total'])
    df_principal['score_total'] = 0


#%%
#df_ids = df_principal['id_x'].tolist() + df_principal['id_y'].tolist()
# count = 0
# def take(df, tipo):
#     for i, row in df.iterrows():
#         global count
#         id_x = tipo + '_' + str(row['id'])
#         count += 1
#         print(count,'/',len(df))
#         df.loc[i, 'Encontrado'] = 'Sim' if id_x in df_ids else 'Nao'
#     count = 0
#     return df


# df2 = take(df2, 'bnmp')
# df1 = take(df1, 'projudi')
# df3 = take(df3, 'goiaspen')

# df2.to_pickle('data/df2.pkl')
# df1.to_pickle('data/df2.pkl')
# df3.to_pickle('data/df2.pkl')

df_principal['tipo_x'] = df_principal['id_x'].str.extract(r'(\w+)_')
df_principal['tipo_y'] = df_principal['id_y'].str.extract(r'(\w+)_')

map_dfs = {
    'bnmp': df2.set_index('id'),
    'projudi': df1.set_index('id'),
    'goiaspen': df3.set_index('id')
}

def style_css():
    return html.Link(rel='stylesheet', href='/assets/dbc.css')

defaultColDefMain = {
    "headerClass": 'center-aligned-header',
    "resizable": True,
    "sortable": True,
    "filter": True,
    "floatingFilter": True,
    "rowHeight": 28,
    "editable":True
}

defaultColDefRelated = {
    "headerClass": 'center-aligned-header',
    "resizable": True,
    "sortable": True,
    "rowHeight": 28,
    "editable":True,
    "autoSize":True
}

dashGridOptionsMain={
            "rowSelection": "single",
            "defaultColDef": defaultColDefMain,
        }
dashGridOptionsRelated={
            "rowSelection": "single",
            "defaultColDef": defaultColDefRelated,
            "onGridReady": {
            "function": """
            function(params) {
                const allColumnIds = [];
                params.columnApi.getAllColumns().forEach(col => allColumnIds.push(col.getId()));
                params.columnApi.autoSizeColumns(allColumnIds, false);
            }
            """
        }
        }

def generate_columns(df):
    cols = ['id','nome', 'nome_mae', 'data_nascimento', 'sexo', 'numero_cpf', 'Encontrado']
    cols_list = [{"field": col, "headerName": col} for col in cols]
    # cols_list[0]={"field":"id", "headerName":"id", "floatingFilter":False}
    # cols_list[4]={"field":"sexo", "headerName":"sexo", "floatingFilter":False}

    return cols_list

def generate_related_columns(df):
    cols = ['id','nome', 'nome_mae', 'data_nascimento', 'sexo', 'score_total']
    return [{"field": col, "headerName": col} for col in cols]

dbc_css = style_css()
dash_extra_args = {}
if os.environ.get('APP_PATH', None) is not None:
    dash_extra_args['routes_pathname_prefix'] = os.environ.get('APP_PATH')

app = dash.Dash(__name__, external_stylesheets=[dbc_css, dbc.themes.DARKLY], **dash_extra_args)


def create_aggrid(id, df, related=False):
    return dag.AgGrid(
        id=id,
        rowData=None if related else df.to_dict("records"),
        columnDefs=generate_related_columns(df) if related else generate_columns(df),
        className="ag-theme-alpine",
        dashGridOptions= dashGridOptionsMain if not related else dashGridOptionsRelated
    )

def create_tab(label, id, df):
    return dbc.Tab(create_aggrid(id=id, df=df), label=label, tab_id=id)


def create_related_col(label, id, df):
    return dbc.Col([
        html.Div(html.H6(label), className="text-center mt-2", id=str(id)+'-div'),
        create_aggrid(id=id, df=df, related=True)
    ])

app.layout = dbc.Container([

    html.H4("🔍 SISTEMA DE BUSCA POR SIMILARIDADE - Controle de Prisões", className="text-center"),
    dbc.Row([
        dbc.Col([],md=1),
        dbc.Col([
            dbc.Card([
                dbc.Tabs([
                    create_tab("BNMP", "grid-bnmp", df2,),
                    create_tab("PROJUDI", "grid-projudi", df1,),
                    create_tab("GOIASPEN", "grid-goiaspen", df3,),
                ], id="tabs-grids", active_tab="grid-bnmp")
            ])
        ], md=10),
        dbc.Col([],md=1)
        # dbc.Col([
        #     html.A("Score mínimo:"),
        #     dcc.Slider(
        #         id='score-slider',
        #         min=0.7,
        #         max=1,
        #         step=0.01,
        #         value=0.7,
        #         marks={i / 10: str(i / 10) for i in range(0, 11)},
        #         tooltip={"placement": "bottom", "always_visible": True},
        #         vertical=True
        #     )
        # ], md=1, className='d-none'),
    ]),

    html.Br(),

    dbc.Card([
        dbc.Row([
            create_related_col("BNMP", "related-bnmp", df2),
            create_related_col("PROJUDI", "related-projudi", df1),
            create_related_col("GOIASPEN", "related-goiaspen", df3),
        ])
    ])
], fluid=True, className="dbc dbc-ag-grid")


# @app.callback(
#     Output('related-bnmp-div', 'className'),
#     Output('related-bnmp', 'className'),
#     Output('related-projudi-div', 'className'),
#     Output('related-goiaspen-div', 'className'),
#     Input('grid-bnmp', 'selectedRows'),
#     Input('grid-projudi', 'selectedRows'),
#     Input('grid-goiaspen', 'selectedRows')
# )
# def update_layout(rows_bnmp, rows_projudi, rows_goiaspen):
    
#     if rows_bnmp and len(rows_bnmp) > 0:
#         return "d-none","d-none", "col-md-6", "col-md-6"
#     else:
#         return  "col-md-4","col-md-4", "col-md-4", "col-md-4",


@app.callback(
    Output("grid-bnmp", "rowData"),
    Output("grid-projudi", "rowData"),
    Output("grid-goiaspen", "rowData"),
    Input("tabs-grids", "active_tab")
)
def refresh_grid_data(active_tab):
    return (
        df2.to_dict("records") if active_tab == "grid-bnmp" else dash.no_update,
        df1.to_dict("records") if active_tab == "grid-projudi" else dash.no_update,
        df3.to_dict("records") if active_tab == "grid-goiaspen" else dash.no_update,
    )

@app.callback(
    Output("related-bnmp", "rowData"),
    Output("related-projudi", "rowData"),
    Output("related-goiaspen", "rowData"),
    Input("grid-bnmp", "selectedRows"),
    Input("grid-projudi", "selectedRows"),
    Input("grid-goiaspen", "selectedRows"),
    # Input("score-slider", "value")
)
def update_related(bnmp_sel, projudi_sel, goiaspen_sel):
    sel_id = None
    tipo_origem = None

    def get_selection_info(source_type, selection):
        if selection:
            return f"{source_type}_{selection[0]['id']}", source_type
        return None, None

    if ctx.triggered_id == "grid-bnmp":
        sel_id, tipo_origem = get_selection_info('bnmp', bnmp_sel)
    elif ctx.triggered_id == "grid-projudi":
        sel_id, tipo_origem = get_selection_info('projudi', projudi_sel)
    elif ctx.triggered_id == "grid-goiaspen":
        sel_id, tipo_origem = get_selection_info('goiaspen', goiaspen_sel)

    elif ctx.triggered_id == "score-slider":
        for source_type, selection in [('bnmp', bnmp_sel), ('projudi', projudi_sel), ('goiaspen', goiaspen_sel)]:
            sel_id, tipo_origem = get_selection_info(source_type, selection)
            if sel_id:
                break

    if not sel_id:
        return [], [], []
    
    score_threshold = 0.75
    filtered = df_principal[
        ((df_principal['id_x'] == sel_id) | (df_principal['id_y'] == sel_id)) &
        (df_principal['score_total'] >= score_threshold)
    ]

    results = {'bnmp': [], 'projudi': [], 'goiaspen': []}

    for _, row in filtered.iterrows():
        if row['id_x'] == sel_id:
            tipo_alvo = row['tipo_y']
            id_alvo = row['id_y'].split('_')[1]
            score = row['score_total']
        else:
            tipo_alvo = row['tipo_x']
            id_alvo = row['id_x'].split('_')[1]
            score = row['score_total']

        if id_alvo.isdigit() and tipo_alvo in map_dfs:
            try:
                dados = map_dfs[tipo_alvo].loc[int(id_alvo)].to_dict()
                dados['score_total'] = round(score, 4)
                dados['id'] = id_alvo
                results[tipo_alvo].append(dados)
            except KeyError:
                continue

    return results['bnmp'], results['projudi'], results['goiaspen']



if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=8050)