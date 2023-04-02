import os
import time
import pandas as pd
import streamlit as st

from ui_components.common_methods import prompt_clip_interrogator

def prompt_finder_page(project_name):
    st.write("This tool helps you find the prompt that would result in an image you provide. It's useful if you want to find a prompt for a specific image that you'd like to align your style with.")
    uploaded_file = st.file_uploader("What image would you like to find the prompt for?", type=['png','jpg','jpeg'], key="prompt_file")
    which_model = st.radio("Which model would you like to get a prompt for?", ["Stable Diffusion 1.5", "Stable Diffusion 2"], key="which_model", help="This is to know which model we should optimize the prompt for. 1.5 is usually best if you're in doubt", horizontal=True)
    best_or_fast = st.radio("Would you like to optimize for best quality or fastest speed?", ["Best", "Fast"], key="best_or_fast", help="This is to know whether we should optimize for best quality or fastest speed. Best quality is usually best if you're in doubt", horizontal=True).lower()
    if st.button("Get prompts"):                
        with open(f"videos/{project_name}/assets/resources/prompt_images/{uploaded_file.name}", "wb") as f:
            f.write(uploaded_file.getbuffer())
        prompt = prompt_clip_interrogator(f"videos/{project_name}/assets/resources/prompt_images/{uploaded_file.name}", which_model, best_or_fast)                
        if not os.path.exists(f"videos/{project_name}/prompts.csv"):
            with open(f"videos/{project_name}/prompts.csv", "w") as f:
                f.write("prompt,example_image,which_model\n")
        # add the prompt to prompts.csv
        with open(f"videos/{project_name}/prompts.csv", "a") as f:
            f.write(f'"{prompt}",videos/{project_name}/assets/resources/prompt_images/{uploaded_file.name},{which_model}\n')
        st.success("Prompt added successfully!")
        time.sleep(1)
        uploaded_file = ""
        st.experimental_rerun()
    # list all the prompts in prompts.csv
    if os.path.exists(f"videos/{project_name}/prompts.csv"):
        
        df = pd.read_csv(f"videos/{project_name}/prompts.csv",na_filter=False)
        prompts = df.to_dict('records')
                    
        col1, col2 = st.columns([1,2])
        with col1:
            st.markdown("### Prompt")
        with col2:
            st.markdown("### Example Image")
        with open(f"videos/{project_name}/prompts.csv", "r") as f:
            for i in prompts:
                index_of_current_item = prompts.index(i)                  
                col1, col2 = st.columns([1,2])
                with col1:
                    st.write(prompts[index_of_current_item]["prompt"])                        
                with col2:                            
                    st.image(prompts[index_of_current_item]["example_image"], use_column_width=True)
                st.markdown("***")