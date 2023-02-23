import streamlit as st
from PIL import Image

st.set_page_config(
    page_title = 'Home',
    page_icon=''
    
)




#image_path = 'C:/Users/Leonardo Paz/Documents/Repos/fundamentos_ftc/ciclo 6/alvo.png'
image = Image.open('alvo.png')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in town')
st.sidebar.markdown("""---""")

st.write('# Curry Company Growth Dashboard')

st.markdown( 
    """
    Acompanhamento do crescimento da empresa.

    ### Como utilizar
        -Empresa:
            -Visão gerencial: Metricas gerais
            -Visão Tática: Indicadores semanais
            -Visão Geográfica: Geolocalização
        -Entregador:
            - Indicadores semanaisde crescimento
        -Restaurante:
            - Indicadores semanaisde crescimento
                
    ### Ajuda
            -email
""")
            