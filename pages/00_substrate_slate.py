import streamlit as st
import os
import uuid
from PIL import Image
import io
from openpyxl import load_workbook
from io import BytesIO
import pandas as pd

from utils import handle_image_orientation
from llm import image_label_generator
from utils import create_substrate_dataframe, substrate_excel_creation
from utils import substrate_excel_data_extractor, load_and_prepare_excel_for_substrate
from s3_utils import upload_to_s3, upload_bucket_path
from db_utils import add_record


# enivironment variables
os.environ["ENV"] = st.secrets["aws"]["ENV"]

# db table name
DB_TABLE_NAME = f"{os.environ['ENV']}-reefcheck"


# constants
SUBSTRATE_IMAGE = "substrate.png"
SUBSTRATE_CSV = "substrate.csv"


if "dataframe" not in st.session_state:
    st.session_state.dataframe = False

if "substrate_df" not in st.session_state:
    st.session_state.substrate_df = None

if "image" not in st.session_state:
    st.session_state.image = None

if "button" not in st.session_state:
    st.session_state.button = False

if "file_name" not in st.session_state:
    st.session_state.file_name = False


def interacting_editable_df():
    st.session_state.dataframe = True


def off_interacting_editable_df():
    st.session_state.dataframe = False
    st.session_state.image = None


def save_button():
    st.session_state.button = True


def file_name_input():
    st.session_state.file_name = True


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
        on_change=off_interacting_editable_df
    )
    
    if uploaded_substrate is not None:
        if not st.session_state.dataframe and not st.session_state.button and not st.session_state.file_name: 
            image = handle_image_orientation(Image.open(uploaded_substrate))
            st.session_state.image = image
            save_uploaded_image(image, SUBSTRATE_IMAGE)
            
            with st.spinner("Generating Substrate Labels", show_time=True):
                substrate_labels = image_label_generator(SUBSTRATE_IMAGE)
                st.toast("Substrate Labels Generated")
                substrate_df = create_substrate_dataframe(substrate_labels.model_dump(), SUBSTRATE_CSV)
                st.session_state.substrate_df = substrate_df
        # add the image to the sidebar
        try:
            st.sidebar.image(st.session_state.image, caption="Uploaded Substrate Image")
        except Exception as error:
            print(str(error))
            st.error(f"Upload got corrupted! Please refresh the page and try again!")
            st.stop()
        # editable df 
        edited_df = st.data_editor(st.session_state.substrate_df, on_change=interacting_editable_df)
        # add the text input
        file_name = st.text_input("File Name to be Saved", value=None, on_change = file_name_input)
        if not file_name:
            st.error("Please enter a file name to save the files.")
            st.stop()
        # set the image extension
        save_image_name = file_name + ".png"
        save_excel_name = file_name + ".xlsx"
        if st.button("Save Files", on_click=save_button):
            download_capability = True
            with st.spinner("Saving Files", show_time=True):
                # initiate excel creation and file saving
                substrate_response = substrate_excel_data_extractor(edited_df)
                substrate_excel_creation(substrate_response, save_excel_name)
                # create the data id
                data_id = str(uuid.uuid4())
                # save files
                # save the excel
                excel_url = upload_to_s3(save_excel_name, upload_bucket_path(st.experimental_user['name'], st.experimental_user['sub'], 'excel', 'substrate', f"{data_id}_{file_name}"))
                if excel_url:
                    st.toast(f"Excel Uploaded")
                else:
                    download_capability = False
                # save the image
                image_url = upload_to_s3(SUBSTRATE_IMAGE, upload_bucket_path(st.experimental_user['name'], st.experimental_user['sub'], 'image', 'substrate', f"{data_id}_{file_name}"))
                if image_url:
                    st.toast(f"Image Uploaded")
                else:
                    download_capability = False
                # add a record to the database
                if download_capability:
                    db_response = add_record(DB_TABLE_NAME, data_id, st.experimental_user['sub'], st.experimental_user['name'], image_url, excel_url)
                    print(db_response)
                    if db_response['success']:
                        st.toast(f"Record Saved")
                    else:
                        download_capability = False
            if not download_capability:
                st.error(f"Error saving files. Please contact support for assistance.")
                st.stop()
            # download the excel file
            st.download_button(
                label="Download as Excel",
                data=load_and_prepare_excel_for_substrate(save_excel_name),
                file_name=save_excel_name,
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                on_click='ignore'
            )

if __name__ == "__main__":
    substrate_slate()
