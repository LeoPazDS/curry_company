# bibliotecas necessárias
import pandas as pd
import io
import seaborn as sns
from matplotlib import pyplot as plt
import plotly.express as px
import streamlit as st
from PIL import Image

import folium
from streamlit_folium import folium_static

from haversine import haversine
import numpy as np

import plotly.graph_objects as go
#import data set

st.set_page_config( page_title='Visão REstaurantes', layout='wide')


#------------------------------------Funções-----------------------------------------------

def clean_data(df1):
    
    #limpar a lista

    #remover espaço
    df1.loc[:,'ID'] = df1.loc[:,'ID'].str.strip()
    df1.loc[:,'Delivery_person_ID'] = df.loc[:,'Delivery_person_ID'].str.strip()
    df1.loc[:,'Road_traffic_density'] = df.loc[:,'Road_traffic_density'].str.strip()
    df1.loc[:,'Type_of_order'] = df.loc[:,'Type_of_order'].str.strip()
    df1.loc[:,'Type_of_vehicle'] = df.loc[:,'Type_of_vehicle'].str.strip()
    df1.loc[:,'Festival'] = df.loc[:,'Festival'].str.strip()
    df1.loc[:,'City'] = df.loc[:,'City'].str.strip()
    df1.loc[:,'Type_of_order'] = df.loc[:,'Type_of_order'].str.strip()
    df1 = df1.loc[df1['Delivery_person_Age'] != 'NaN ',:]
    linhas_vazias = df1['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[linhas_vazias, :]
    linhas_vazias = df1['Weatherconditions'] != 'NaN'
    df1 = df1.loc[linhas_vazias, :]
    df1 = df1.loc[df1['Delivery_person_Ratings'] != 'NaN',:]
    df1 = df1.loc[df1['Road_traffic_density'] != 'NaN',:]
    df1 = df1.loc[df1['City'] != 'NaN',:]

    df1['Time_taken(min)' ] = df1['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])
    df1['Time_taken(min)' ] = df1['Time_taken(min)'].astype(int)
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)


    df1['Order_Date'] = pd.to_datetime( df1['Order_Date'], format='%d-%m-%Y' )

    return df1

#-------------------------------------------------------------------------------------------------

def distancia_media(df1):
    #distancia média
    cols = ['Restaurant_latitude',	'Restaurant_longitude',	'Delivery_location_latitude' ,	'Delivery_location_longitude']
    df1['Distance'] = (df1.loc[:, cols]
                        .apply(lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude'])
                                                     ,(x['Delivery_location_latitude'] , x['Delivery_location_longitude']))
                                , axis = 1))
    avg_distance = np.round(df1['Distance'].mean(),2)
    return avg_distance

#--------------------------------------------------------------------------------------------------
def tempo_mean_std(df1, festival = 'Yes'):
     #Tempo medio entregas durante festivais
    medio = df1[['Festival', 'Time_taken(min)']].groupby('Festival').agg({'Time_taken(min)': ['mean', 'std']})
            
    medio.columns= ['Time_taken_mean', 'Time_taken_std']
    medio = medio.reset_index()
    medio =np.round(medio.loc[medio['Festival']== festival,:],2)
    return medio

#-------------------------------------------------------------------------------------------------

def tempo_mean_cidade(df1):
    medio = df1[['City', 'Time_taken(min)']].groupby('City').agg({'Time_taken(min)' : ['mean', 'std']})
    medio.columns= ['Time_taken_mean', 'Time_taken_std']
    medio = medio.reset_index()
    fig = go.Figure()
    fig.add_trace( go.Bar( name = 'Control',
                            x=medio['City'],
                            y= medio['Time_taken_mean'],
                            error_y=dict(type='data', array=medio['Time_taken_std'])))
    fig.update_layout(barmode='group')
    return fig

#--------------------------------------------------------------------------------------------------
def dist_mean_city(df1):
    cols = ['Restaurant_latitude',	'Restaurant_longitude',	'Delivery_location_latitude' ,	'Delivery_location_longitude']
    df1['Distance'] = (df1.loc[:, cols]
                        .apply(lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),
                                            (x['Delivery_location_latitude'] , x['Delivery_location_longitude'])), axis = 1))
    avg_distance = df1[['City', 'Distance']].groupby('City').mean().reset_index()

    fig = go.Figure( data=[go.Pie(labels=avg_distance['City'], values= avg_distance['Distance'], pull=[0,0.1,0])])
    return fig

#---------------------------------------------------------------------------------------------------
def time_traffic_mean(df1):
    medio =( df1[['City', 'Road_traffic_density', 'Time_taken(min)']]
                    .groupby(['City','Road_traffic_density'])
                    .agg({'Time_taken(min)' : ['mean', 'std']}))
    medio.columns= ['Time_taken_mean', 'Time_taken_std']
    medio = medio.reset_index()

    fig = px.sunburst(medio, path=['City', 'Road_traffic_density'], values = 'Time_taken_mean', color ='Time_taken_std',
            color_continuous_scale='RdBu' , color_continuous_midpoint=np.average(medio['Time_taken_std']))
    return fig

#-------------------------------------------------------------------------------------------------
def mean_std_city_food(df1):
    medio = (df1[['City', 'Type_of_order', 'Time_taken(min)']]
                 .groupby(['City','Type_of_order'])
                 .agg({'Time_taken(min)' : ['mean', 'std']}))
        
    medio.columns= ['Time_taken_mean', 'Time_taken_std']
    medio = medio.reset_index()
    return medio




#---------------------------------Inicio-----------------------------------------------------------
df = pd.read_csv('train.csv')

df1 = clean_data(df)

#========================================
#Barra lateral
#========================================
st.header( 'Marketplace - Visão Restaurantes')

#image_path = 'C:/Users/Leonardo Paz/Documents/Repos/fundamentos_ftc/ciclo 6/alvo.png'
image=Image.open('alvo.png')
st.sidebar.image('alvo.png', width=120)

st.sidebar.markdown('# Cury Company')

st.sidebar.markdown('## Fastest Delivery in town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')
values = st.sidebar.slider(
    'Até qual valor',
    value=pd.datetime(2022, 4, 13),
    min_value=pd.datetime(2022, 2, 11),
    max_value=pd.datetime(2022, 4, 13),
    format='DD-MM-YYYY')

st.sidebar.markdown("""---""")

traffic_options=st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low', 'Medium' , 'High', 'Jam'],
    default=['Low', 'Medium' , 'High', 'Jam'])

st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by CDS')

#Filtro de data
linhas_selecionadas = df1['Order_Date'] < values
df1 = df1.loc[linhas_selecionadas, :]

#Filtro de transito

linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

#========================================
#Layout no Streamlit
#========================================


tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title('Overal Metrics')
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            
            # A quantidade de entregadores únicos.
            uni = df1['Delivery_person_ID'].nunique()
            col1.metric('N° Entregadores',uni)
            
            
            
        with col2:
            
            avg_distance = distancia_media(df1)
            col2.metric('Dist. Média',avg_distance)
        
        
        
        with col3:
             #Tempo medio entregas durante festivais
            
            medio = tempo_mean_std(df1, festival = 'Yes')
            col3.metric('Tempo medio F',medio['Time_taken_mean'])
            
            
            
        with col4:
            #Desvio padrão entregas durante festivais
           
            medio = tempo_mean_std(df1, festival = 'Yes')
            col4.metric('STD Fest',medio['Time_taken_std'])
            
        with col5:
            #Tempo medio entregas durante não festivais
            
            medio = tempo_mean_std(df1, festival = 'No')
            col5.metric('Tempo médio Ñ F',medio['Time_taken_mean'])
            
        with col6:
            #Desvio padrão entregas durante não festivais
           
            medio = tempo_mean_std(df1, festival = 'No')
            col6.metric('STD Ñ F',medio['Time_taken_std'])
            
        st.markdown("""---""")
        
    with st.container():
        st.title('Tempo Médio de Entregas por Cidade')
        #Tempo desvio padrão entregas por cidade      
    
        fig = tempo_mean_cidade(df1)
        st.plotly_chart(fig)
       
        
        st.markdown("""---""")
        
    with st.container():
        st.title('Distribuição do Tempo')
        
        col1, col2 = st.columns(2)
        
        with col1:
            
            #distancia média por cidade
            
            
            fig = dist_mean_city(df1)
            st.plotly_chart(fig)  
                        
                           
            
        with col2:
            
            #Tempo desvio padrão entregas por cidade e tipo de trafego
            
            
            fig = time_traffic_mean(df1)
            st.plotly_chart(fig)
        
        st.markdown("""---""")
        
    with st.container():
        st.title('Distribuição da Distância')
        #Tempo desvio padrão entregas por cidade e tipo de comida
    
        medio = mean_std_city_food(df1)
        st.dataframe(medio)