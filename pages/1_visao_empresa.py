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


st.set_page_config( page_title='Visão Empresa', layout='wide')

#---------------------------------------------Funções----------------------------------------------

def clean_code(df1):
    """Esta função tem a responsabilidade de limpar o Data Frame
    
       Tipos de limpeza:
       -Tirar NAN
       -Acertar tipo de coluna de dados
       -Remoção de espaços vazios
       
       Input: Dataframe
       Output: Dataframe limpo
    """
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
#----------------------------------------------------------------------------------------------------------

def order_metric(df1):
               
    ped_dia = df1[['Order_Date', 'ID']].groupby('Order_Date').count().reset_index()
    
    fig = px.bar( ped_dia ,
                x= 'Order_Date' ,
                y= 'ID',);
    
    return fig
#---------------------------------------------------------------------------------------------------------
def traffic_order_share(df1):
                          
    ped_dia = df1[['Road_traffic_density', 'ID']].groupby('Road_traffic_density').count().reset_index()
    ped_dia['percentil'] = (ped_dia['ID'] / ped_dia['ID'].sum() *100)
    fig1 = px.pie(ped_dia, values='percentil', names='Road_traffic_density')
    
    return fig1
#---------------------------------------------------------------------------------------------------------

def traffic_order_city(df1):
                
    df_aux = df1.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()
    fig2 =px.scatter(df_aux, x='City', y= 'Road_traffic_density', size='ID', color='City')
                
    return fig2

#---------------------------------------------------------------------------------------------------------

def order_by_week(df1):
    df1['Week_Number'] = df1['Order_Date'].dt.isocalendar().week
    ped_semana = df1[['ID', 'Week_Number']].groupby('Week_Number').count().reset_index()
    fig3 = px.line( ped_semana,
                    x= 'Week_Number',
                    y= 'ID',)
    return fig3

#--------------------------------------------------------------------------------------------------------

def number_order_delivery(df1):
            
    ped_entr_sem = df1[['ID','Week_Number']].groupby('Week_Number').count().reset_index()
    n_entr = df1[['Delivery_person_ID', 'Week_Number']].groupby('Week_Number').nunique().reset_index()
    df_aux =pd.merge(ped_entr_sem, n_entr, how = 'inner' )
    df_aux['Order_delivery'] = (df_aux['ID']/df_aux['Delivery_person_ID'])
        
    plt.figure(figsize=(15, 8));
    dx = px.line( df_aux ,
                      x= 'Week_Number' ,
                      y='Order_delivery' , )
    return dx

#------------------------------------------------------------------------------------------------------

def country_maps(df1):
    df_aux1 = (df1[['City','Delivery_location_latitude', 'Delivery_location_longitude', 'Road_traffic_density']]
               .groupby(['City','Road_traffic_density'])
               .median()
               .reset_index()
               .reset_index())
    

    mapa = folium.Map()
    for index, location_info in df_aux1.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'],
                       location_info['Delivery_location_longitude']],
                       popup=location_info['City']).add_to(mapa)
    return mapa


#_______________________________________Inicio da estrutura lógica do código_____________________________________
#import data set

df = pd.read_csv('train.csv')


#limpar a lista

df1 = clean_code(df)





#========================================
#Barra lateral
#========================================
st.header( 'Markeyplace - Visão Cliente')

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
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visaõ Tatica', 'Visão Geografica'])

with tab1:
    with st.container():
        #order 
        st.markdown('# Order by Day')
        
        fig = order_metric(df1)
        
        st.plotly_chart(fig, use_container_width=True)
   
    
    with st.container():
    #=================
    #Quebrar 2 colunas
    #=================
    
        col1, col2 = st.columns (2)
        with col1:
            st.markdown('# Traffic Order Share')
            
            fig1 = traffic_order_share(df1)
                                 
            st.plotly_chart(fig1, use_container_width= True)
            
            
        with col2:
            st.markdown('# Traffic Order City')
            fig2 = traffic_order_city(df1)
           
            st.plotly_chart(fig2, use_container_width= True)
        
    
with tab2:
    with st.container():
        
        st.markdown('# Order by Week')
        fig3 = order_by_week(df1)
        
        st.plotly_chart(fig3, use_container_width= True)
    
    with st.container():
        
        st.markdown('# Number of Order by Deliver')
        dx = number_order_delivery(df1)
        
        st.plotly_chart(dx, use_container_width= True)       
    
with tab3:
    st.markdown('# Country Maps')
    mapa = country_maps(df1)
    
    folium_static(mapa, width= 1024, height = 600)
    




