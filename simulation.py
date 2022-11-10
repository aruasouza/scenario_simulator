import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px

sim = pd.read_csv('simulacao.csv',index_col = 'situacao')

st.set_page_config(page_title = 'Simulacão de cenários',page_icon = ':bar_chart:',layout = 'wide')

def distribution(media,minimo,maximo,n):
    step = (maximo - minimo) / n
    dist = np.arange(minimo,maximo,step)
    while len(dist) < n:
        dist = np.append(dist,media)
    while len(dist) > n:
        dist = dist[1:]
    return list(map(lambda x: x + (np.random.normal(0.5,0.17) * (media - x)),dist))

def gerar_cenarios(n,simulacao):
    # IPCA
    cenarios_ipca = distribution(simulacao.loc['medio','ipca'],simulacao.loc['min','ipca'],simulacao.loc['max','ipca'],n)
    np.random.shuffle(cenarios_ipca)
    # CDI
    cenarios_cdi = distribution(simulacao.loc['medio','cdi'],simulacao.loc['min','cdi'],simulacao.loc['max','cdi'],n)
    np.random.shuffle(cenarios_cdi)
    # Cambio
    cenarios_cambio = distribution(simulacao.loc['medio','cambio'],simulacao.loc['min','cambio'],simulacao.loc['max','cambio'],n)
    np.random.shuffle(cenarios_cambio)

    # Resposta
    return pd.DataFrame({'ipca':cenarios_ipca,'cdi':cenarios_cdi,'cambio':cenarios_cambio})

def check(simulacao):
    for column in simulacao.columns:
        if (simulacao.loc['min',column] < simulacao.loc['medio',column] < simulacao.loc['max',column]):
            continue
        else:
            mensagem_erro = '''
            ERRO: 
            O valor mínimo deve ser menor que o valor médio e o valor médio deve ser menor que o valor máximo.'''
            st.error(mensagem_erro,icon="🚨")
            return False
    return True

@st.cache
def load_data(simulacao):
    ativos = pd.read_csv('ativos.csv')
    passivos = pd.read_csv('passivos.csv')
    simulacao.to_csv('simulacao.csv',index_label = 'situacao')

    cenarios = gerar_cenarios(1000,simulacao)

    # CDI
    cenarios['impacto_cdi_ativos'] = cenarios['cdi'] * ativos.loc[0,'cdi']
    cenarios['impacto_cdi_passivos'] = cenarios['cdi'] * passivos.loc[0,'cdi']
    cenarios['impacto_cdi_total'] = cenarios['impacto_cdi_ativos'] - cenarios['impacto_cdi_passivos']

    # IPCA
    cenarios['impacto_ipca_ativos'] = cenarios['ipca'] * ativos.loc[0,'ipca']
    cenarios['impacto_ipca_passivos'] = cenarios['ipca'] * passivos.loc[0,'ipca']
    cenarios['impacto_ipca_total'] = cenarios['impacto_ipca_ativos'] - cenarios['impacto_ipca_passivos']

    # Cambio
    cenarios['impacto_cambio_ativos'] = cenarios['cambio'] * ativos.loc[0,'cambio']
    cenarios['impacto_cambio_passivos'] = cenarios['cambio'] * passivos.loc[0,'cambio']
    cenarios['impacto_cambio_total'] = cenarios['impacto_cambio_ativos'] - cenarios['impacto_cambio_passivos']

    # Total
    cenarios['impacto_total'] = cenarios['impacto_cdi_total'] + cenarios['impacto_ipca_total'] + cenarios['impacto_cambio_total']

    return cenarios

def change_data():
    st.session_state['data'] = simulacao

st.header('Simulação de Cenários')
st.sidebar.title('Criar simulação')

st.sidebar.header('Inflação (IPCA) %')

left_bar_ipca,middle_bar_ipca,righ_bar_ipca = st.sidebar.columns(3)
min_ipca = left_bar_ipca.number_input('Mínimo',key = 'min_ipca',value = sim.loc['min','ipca'] * 100) / 100
med_ipca = middle_bar_ipca.number_input('Médio',key = 'med_ipca',value = sim.loc['medio','ipca'] * 100) / 100
max_ipca = righ_bar_ipca.number_input('Máximo',key = 'max_ipca',value = sim.loc['max','ipca'] * 100) / 100

st.sidebar.header('CDI %')
left_bar_cdi,middle_bar_dci,righ_bar_cdi = st.sidebar.columns(3)
min_cdi = left_bar_cdi.number_input('Mínimo',key = 'min_cdi',value = sim.loc['min','cdi'] * 100) / 100
med_cdi = middle_bar_dci.number_input('Médio',key = 'med_cdi',value = sim.loc['medio','cdi'] * 100) / 100
max_cdi = righ_bar_cdi.number_input('Máximo',key = 'max_cdi',value = sim.loc['max','cdi'] * 100) / 100

st.sidebar.header('Variação no Câmbio %')
left_bar_cambio,middle_bar_cambio,righ_bar_cambio = st.sidebar.columns(3)
min_cambio = left_bar_cambio.number_input('Mínimo',key = 'min_cambio',value = sim.loc['min','cambio'] * 100) / 100
med_cambio = middle_bar_cambio.number_input('Médio',key = 'med_cambio',value = sim.loc['medio','cambio'] * 100) / 100
max_cambio = righ_bar_cambio.number_input('Máximo',key = 'max_cambio',value = sim.loc['max','cambio'] * 100) / 100

dados = {'cambio':[min_cambio,med_cambio,max_cambio],'ipca':[min_ipca,med_ipca,max_ipca],'cdi':[min_cdi,med_cdi,max_cdi]}
simulacao = pd.DataFrame(dados,index = ['min','medio','max'])

button = st.sidebar.button('Simular',on_click = change_data)

verificado = False
if 'data' in st.session_state:
    if check(st.session_state.data):
        verificado = True
        df = load_data(st.session_state.data)
else:
    if check(sim):
        verificado = True
        df = load_data(sim)

if verificado:
    left_column,middle_column,right_column = st.columns(3)
    with left_column:
        ipca_fig = px.histogram(df,x = 'ipca')
        ipca_fig.update_layout(title = 'Simulação inflação (IPCA) %',margin=dict(l = 0,r = 0,b = 0,t = 40),height = 200)
        ipca_fig.update_xaxes(title = '')
        ipca_fig.update_yaxes(title = '')
        st.plotly_chart(ipca_fig,use_container_width = True)

    with middle_column:
        cdi_fig = px.histogram(df,x = 'cdi')
        cdi_fig.update_layout(title = 'Simulação CDI %',margin=dict(l = 0,r = 0,b = 0,t = 40),height = 200)
        cdi_fig.update_xaxes(title = '')
        cdi_fig.update_yaxes(title = '')
        st.plotly_chart(cdi_fig,use_container_width = True)

    with right_column:
        cambio_fig = px.histogram(df,x = 'cambio')
        cambio_fig.update_layout(title = 'Simulação variação câmbio %',margin=dict(l = 0,r = 0,b = 0,t = 40),height = 200)
        cambio_fig.update_xaxes(title = '')
        cambio_fig.update_yaxes(title = '')
        st.plotly_chart(cambio_fig,use_container_width = True)

    fig = px.histogram(df,x = 'impacto_total')
    fig.update_layout(title = 'Simulação de Impacto Financeiro',margin=dict(l = 0,r = 0,b = 0,t = 40),height = 350)
    fig.update_xaxes(title = '')
    fig.update_yaxes(title = '')
    st.plotly_chart(fig,use_container_width = True)
    st.download_button('Baixar Cenários',df.to_csv(index = False),'cenarios.csv')


style = '''
<style>
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}
.block-container {padding-top:1rem;}
.e1fqkh3o4 {padding-top:1rem;}
</style>
'''

st.markdown(style,unsafe_allow_html=True)

