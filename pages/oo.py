import streamlit as st
import pandas as pd
import subprocess
import os
import joblib
from rdkit import Chem
from rdkit.Chem import Descriptors
from rdkit.ML.Descriptors import MoleculeDescriptors


# Page configuration
st.set_page_config(
  page_title='Predict Activity of single molecule',
  initial_sidebar_state='expanded')

# Session state
if 'smiles_input' not in st.session_state:
  st.session_state.smiles_input = ''

# Utilities
if os.path.isfile('molecule.smi'):
  os.remove('molecule.smi') 
  
def PUbchemfp_desc_calc():
    # Performs the descriptor calculation
    bashCommand = "java -Xms2G  -Djava.awt.headless=true -jar ./PaDEL-Descriptor/PaDEL-Descriptor.jar -removesalt -standardizenitro -fingerprints  -descriptortypes ./PaDEL-Descriptor/PubchemFingerprinter.xml  -dir ./ -file descriptors.csv"
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    os.remove('molecule.smi')  



def descriptors(smiles):
    mols = [Chem.MolFromSmiles(s) for s in smiles] 
    calc = MoleculeDescriptors.MolecularDescriptorCalculator([x[0] for x in Descriptors._descList])
    desc_names = calc.GetDescriptorNames()
    
    Mol_descriptors =[]
    for mol in mols:

        descriptors = calc.CalcDescriptors(mol)
        Mol_descriptors.append(descriptors)
    return Mol_descriptors,desc_names     
 
# The App    
st.title('LRRK2 Activity Prediction App')
st.info('The LRRK2 Activity Prediction App can be used to predict whether a  molecule is active or inactive for lrrk2 target protein .')

if st.session_state.smiles_input == '':
    

      smiles_txt = st.text_input('Enter Compound in Smile Format', st.session_state.smiles_input)
      st.session_state.smiles_input = smiles_txt

      with st.expander('Example SMILES'):

        st.code('CC5CN(c4cc3nc(NC2C=NN(C1CC1)C2C)ncc3cc4Cl)CCC5(C)O')
        st.code('O=C(Nc1ncco1)c1cc(Br)ccc1OCc1ccccc1')
submit_button = st.button('Predict')

      
      
if submit_button:
        st.subheader(' Input molecule:')
        with st.expander(' SMILES', expanded=True):
          
          st.text(st.session_state.smiles_input)
          x=pd.DataFrame(st.session_state.smiles_input,columns=["smiles"])

          #x=pd.DataFrame(st.session_state.smiles_input)
      # Input SMILES saved to file
          smile_file = open('molecule.smi', 'w')
          smile_file.write(f'{st.session_state.smiles_input}\tName_00')
          smile_file.close()


if st.session_state.smiles_input != '':
        st.subheader(' Descriptors')
        if os.path.isfile('molecule.smi'):
             PUbchemfp_desc_calc()

        descriptors = pd.read_csv('descriptors.csv')
        descriptors.drop('Name', axis=1, inplace=True)
        st.expander('Full set of molecule discriptors')
        
        st.write(descriptors)
        st.write(descriptors.shape)

        st.header('set of descriptors used to prediction')
        train_set=pd.read_csv('Pubchem_features.csv')
        feature_list=list(train_set.columns)
        desc_subset = descriptors[feature_list]
        st.write(desc_subset)
        st.write(desc_subset.shape)
        x.to_csv('molecule.csv', sep = '\t', index = False,header=None)

        first_column = x.iloc[:, 0] 
        Mol_descriptors,desc_names =descriptors(first_column)
        df_with_200_descriptors = pd.DataFrame(Mol_descriptors,columns=desc_names)
        df=df_with_200_descriptors[["MolWt","MolLogP","NumHAcceptors","NumHDonors"]]
        st.subheader("Lipinski Rule of 5 Descriptors")
        st.write(df)


      
if st.session_state.smiles_input != '':
 model = joblib.load('model_1.0.2.pkl')

if st.session_state.smiles_input != '':
        st.subheader(' Predictions')
        prediction = model.predict(desc_subset)
        prediction_probability=model.predict_proba(desc_subset)
        prediction_output = pd.Series(prediction, name='Activity')
        x=pd.DataFrame(prediction_probability,columns=["Inactive probability","Active_probability"])
        Result= pd.concat([prediction_output,x], axis=1)
        result = []
        for x in Result["Activity"]:
          if x==1:
            result.append("Active")
          if x==0:
            result.append("Inactive")
        Result["Activity"]=result
        st.write(Result)
        prediction_csv = Result.to_csv(index=False)
        st.download_button(label="Download prediction result",data=prediction_csv,file_name="My_result.csv")
