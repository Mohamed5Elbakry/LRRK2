import streamlit as st

st.set_page_config(
    page_title="Home",
    initial_sidebar_state='expanded')

st.title('LRRK2 Activity prediction App')
st.info('The LRRK2 Activity Prediction App can be used to predict whether a  molecule is active or inactive for lrrk2 target protein .')

st.subheader("App function:")
st.write("The sidebar of App Contain Four function Page")
st.write("The first page use can use it if you have a smiles of only one molecule and want to do know his activity ")
st.write("The second page use can use it if you have file that contain more than smiles for more moleule ")
st.write("The third page has information about model performance that used to predict the model")
st.write("The last page has information about target protien")