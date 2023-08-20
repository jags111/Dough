

import streamlit as st
import time
from shared.constants import InternalFileType
from ui_components.widgets.frame_time_selector import single_frame_time_selector
from ui_components.widgets.image_carousal import display_image
from utils.constants import ImageStage
from utils.data_repo.data_repo import DataRepo
from ui_components.constants import WorkflowStageType
from shared.file_upload.s3 import upload_file
from ui_components.common_methods import delete_frame, add_image_variant, promote_image_variant, save_uploaded_image, replace_image_widget


def frame_selector_widget():
    data_repo = DataRepo()
    
    time1, time2 = st.columns([1,1])

    timing_details = data_repo.get_timing_list_from_project(project_uuid=st.session_state["project_uuid"])
    with time1:
        if 'prev_frame_index' not in st.session_state:
            st.session_state['prev_frame_index'] = 1

        # st.write(st.session_state['prev_frame_index'])
        # st.write(st.session_state['current_frame_index'])
        st.session_state['current_frame_index'] = st.number_input(f"Key frame # (out of {len(timing_details)})", 1, len(timing_details), value=st.session_state['prev_frame_index'], step=1, key="which_image_selector")
        st.session_state['current_frame_uuid'] = timing_details[st.session_state['current_frame_index'] - 1].uuid
        if st.session_state['prev_frame_index'] != st.session_state['current_frame_index']:
            st.session_state['prev_frame_index'] = st.session_state['current_frame_index']
            st.session_state['current_frame_uuid'] = timing_details[st.session_state['current_frame_index'] - 1].uuid
            st.session_state['reset_canvas'] = True
            st.session_state['frame_styling_view_type_index'] = 0
            st.session_state['frame_styling_view_type'] = "Individual View"
                                        
            st.experimental_rerun()       

    with time2:
        single_frame_time_selector(st.session_state['current_frame_uuid'], 'navbar')
    



    image_1, image_2 = st.columns([1,1])
    with image_1:
        st.warning(f"Guidance Image:")
        display_image(st.session_state['current_frame_uuid'], stage=WorkflowStageType.SOURCE.value, clickable=False)
        with st.expander("Replace guidance image"):
            replace_image_widget(st.session_state['current_frame_uuid'], stage=WorkflowStageType.SOURCE.value)
    with image_2:
        st.success(f"Main Styled Image:")
        display_image(st.session_state['current_frame_uuid'], stage=WorkflowStageType.STYLED.value, clickable=False)
        with st.expander("Replace styled image"):
            replace_image_widget(st.session_state['current_frame_uuid'], stage=WorkflowStageType.STYLED.value)
    
    st.markdown("***")
    
    if st.button("Delete key frame"):
        delete_frame(st.session_state['current_frame_uuid'])
        st.experimental_rerun()