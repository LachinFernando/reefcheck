import streamlit as st
import os
import uuid
from PIL import Image
import io

from utils import handle_image_orientation
from llm import image_label_generator_fish_invert
from utils import create_fish_slate_dataframe, fish_slate_excel_creation, load_and_prepare_excel_for_fish_slate
from utils import upload_bucket_path, fish_excel_data_extractor
from s3_utils import upload_to_s3

# constants
FISH_INVERT_IMAGE = "fish_and_invert.png"
FISH_INVERT_CSV = "fish_and_invert.csv"
FISH_INVERT_EXCEL = "fish_and_invert.xlsx"

if "fish_dataframe" not in st.session_state:
    st.session_state.fish_dataframe = False

if "fish_invert_df" not in st.session_state:
    st.session_state.fish_invert_df = None

if "fish_invert_image" not in st.session_state:
    st.session_state.fish_invert_image = None

if "fish_invert_button" not in st.session_state:
    st.session_state.fish_invert_button = False


def interacting_editable_df():
    st.session_state.fish_dataframe = True

def off_interacting_editable_df():
    st.session_state.fish_dataframe = False
    st.session_state.fish_invert_image = None

def save_button():
    st.session_state.fish_invert_button = True

def save_uploaded_image(image, target_name):
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')
    img_byte_arr = img_byte_arr.getvalue()
    image.save(target_name)

def fish_invert_slate():
    if not st.experimental_user.is_logged_in:
        st.error("Please log in to access this page.")
        return
    
    st.header("Fish and Invert Slate")
    
    uploaded_fish_invert = st.file_uploader(
        "Upload Fish and Invert Image",
        type=["jpg", "jpeg", "png"],
        key="fish_invert_uploader",
        on_change=off_interacting_editable_df
    )
    
    if uploaded_fish_invert is not None:
        if not st.session_state.fish_dataframe and not st.session_state.fish_invert_button:
            image = handle_image_orientation(Image.open(uploaded_fish_invert))
            st.session_state.fish_invert_image = image
            save_uploaded_image(image, FISH_INVERT_IMAGE)
            
            with st.spinner("Generating Fish and Invert Labels", show_time=True):
                fish_and_invert_labels = image_label_generator_fish_invert(FISH_INVERT_IMAGE)
                st.toast("Fish and Invert Labels Generated")
                fish_and_invert_df = create_fish_slate_dataframe(fish_and_invert_labels.model_dump(), FISH_INVERT_CSV)
                st.session_state.fish_invert_df = fish_and_invert_df
        # add the image to the sidebar
        st.sidebar.image(st.session_state.fish_invert_image, caption="Uploaded Fish and Invert Image")
        # editable df 
        edited_df = st.data_editor(st.session_state.fish_invert_df, on_change=interacting_editable_df)
        if st.button("Save Files", on_click=save_button):
            with st.spinner("Saving Files", show_time=True):
                # initiate excel creation and file saving
                fish_response = fish_excel_data_extractor(edited_df)
                fish_slate_excel_creation(fish_response, FISH_INVERT_EXCEL)
                # create the data id
                data_id = str(uuid.uuid4())
                # save files
                # save the excel
                upload_to_s3(FISH_INVERT_EXCEL, upload_bucket_path(st.experimental_user['name'], st.experimental_user['sub'], 'excel', 'fish_and_invert', data_id))
                st.toast(f"Excel Uploaded")
                # save the image
                upload_to_s3(FISH_INVERT_IMAGE, upload_bucket_path(st.experimental_user['name'], st.experimental_user['sub'], 'image', 'fish_and_invert', data_id))
                st.toast(f"Image Uploaded")
                # download the excel file
            st.download_button(
                label="Download as Excel",
                data=load_and_prepare_excel_for_fish_slate(FISH_INVERT_EXCEL),
                file_name='fish_and_invert_data.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                on_click='ignore'
            )

if __name__ == "__main__":
    fish_invert_slate()
