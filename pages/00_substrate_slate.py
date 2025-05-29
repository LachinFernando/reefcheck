import streamlit as st
import os
import uuid
from PIL import Image
import io

from utils import handle_image_orientation
from llm import image_label_generator
from utils import create_substrate_dataframe, substrate_excel_creation, load_and_prepare_excel_for_substrate
from s3_utils import upload_to_s3

# constants
SUBSTRATE_IMAGE = "substrate.png"
SUBSTRATE_CSV = "substrate.csv"
SUBSTRATE_EXCEL = "substrate.xlsx"


def upload_bucket_path(user_name: str, user_id:str, type_: str, slate_type: str, data_id: str) -> str:
    user_names = user_name.split(" ")
    user_name_ = "_".join(user_names)

    if type_ == 'image':
        st.toast(f"Image Uploaded")
        return f"reefcheck/data/{slate_type}/{user_name_}_{user_id}/images/{data_id}.png"
    elif type_ == 'excel':
        st.toast(f"Excel Uploaded")
        return f"reefcheck/data/{slate_type}/{user_name_}_{user_id}/excel/{data_id}.xlsx"

def save_uploaded_image(image, target_name):
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')
    img_byte_arr = img_byte_arr.getvalue()
    image.save(target_name)

def substrate_slate():
    if not st.experimental_user.is_logged_in:
        st.error("Please log in to access this page.")
        return
    
    st.header("Substrate Slate")
    
    uploaded_substrate = st.file_uploader(
        "Upload Substrate Image",
        type=["jpg", "jpeg", "png"],
        key="substrate_uploader",
    )
    
    if uploaded_substrate is not None:
        image = handle_image_orientation(Image.open(uploaded_substrate))
        st.sidebar.image(image, caption="Uploaded Substrate Image")
        save_uploaded_image(image, SUBSTRATE_IMAGE)
        
        with st.spinner("Generating Substrate Labels", show_time=True):
            substrate_labels = image_label_generator(SUBSTRATE_IMAGE)
            st.toast("Substrate Labels Generated")
            substrate_df = create_substrate_dataframe(substrate_labels.model_dump(), SUBSTRATE_CSV)
            substrate_excel_creation(substrate_labels.model_dump(), SUBSTRATE_EXCEL)
            data_id = str(uuid.uuid4())
            upload_to_s3(SUBSTRATE_EXCEL, upload_bucket_path(st.experimental_user['name'], st.experimental_user['sub'], 'excel', 'substrate', data_id))
            upload_to_s3(SUBSTRATE_IMAGE, upload_bucket_path(st.experimental_user['name'], st.experimental_user['sub'], 'image', 'substrate', data_id))
            
            st.download_button(
                label="Download as Excel",
                data=load_and_prepare_excel_for_substrate(SUBSTRATE_EXCEL),
                file_name='substrate_data.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                on_click='ignore'
            )

if __name__ == "__main__":
    substrate_slate()
