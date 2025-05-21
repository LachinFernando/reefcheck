import streamlit as st
import os
import uuid
from PIL import Image
import io

from utils import handle_image_orientation
from llm import image_label_generator, image_label_generator_fish_invert
from utils import create_substrate_dataframe, substrate_excel_creation, load_and_prepare_excel_for_substrate, create_fish_slate_dataframe, fish_slate_excel_creation, load_and_prepare_excel_for_fish_slate
from firebase import upload_file


# constants
SUBSTRATE_IMAGE = "substrate.png"
FISH_INVERT_IMAGE = "fish_and_invert.png"
SUBSTRATE_CSV = "substrate.csv"
SUBSTRATE_EXCEL = "substrate.xlsx"
FISH_INVERT_CSV = "fish_and_invert.csv"
FISH_INVERT_EXCEL = "fish_and_invert.xlsx"


if 'file_uploader_one' not in st.session_state:
    st.session_state['file_uploader_one'] = None
if 'file_uploader_two' not in st.session_state:
    st.session_state['file_uploader_two'] = None


def on_file_one_uploaded():
    st.session_state['file_uploader_one'] = False


def on_file_two_uploaded():
    st.session_state['file_uploader_two'] = False


def upload_bucket_path(user_name: str, user_id:str, type_: str, slate_type: str, data_id: str) -> str:

    user_names = user_name.split(" ")
    user_name_ = "_".join(user_names)

    if type_ == 'image':
        st.toast(f"Image Uploaded")
        return f"data/{slate_type}/{user_name_}_{user_id}/images/{data_id}.png"
    elif type_ == 'excel':
        st.toast(f"Excel Uploaded")
        return f"data/{slate_type}/{user_name_}_{user_id}/excel/{data_id}.xlsx"



def save_uploaded_image(image, target_name):
    # Save the image in memory using BytesIO
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')  # Specify the format you'd like
    img_byte_arr = img_byte_arr.getvalue()

    # save the corrected image to disk
    image.save(target_name)


def reef_analyser():
    # Create two tabs
    substrate_tab, fish_invert_tab = st.tabs(["Substrate Slate", "Fish and Invert Slate"])

    # Substrate Slate tab
    with substrate_tab:
        st.header("Substrate Slate")
        uploaded_substrate = st.file_uploader(
            "Upload Substrate Image",
            type=["jpg", "jpeg", "png"],
            key="substrate_uploader",
            on_change=on_file_one_uploaded
        )
        if uploaded_substrate is not None and not st.session_state['file_uploader_one']:
            image = handle_image_orientation(Image.open(uploaded_substrate))
            st.sidebar.image(image, caption="Uploaded Substrate Image")
            # save the uploaded image
            save_uploaded_image(image, SUBSTRATE_IMAGE)
            # label generating
            with st.spinner("Generating Substrate Labels", show_time = True):
                substrate_labels = image_label_generator(SUBSTRATE_IMAGE)
                st.toast("Substrate Labels Generated")
                # dataframe generation
                substrate_df = create_substrate_dataframe(substrate_labels.model_dump(), SUBSTRATE_CSV)
                substrate_excel_creation(substrate_labels.model_dump(), SUBSTRATE_EXCEL)
                # upload the file
                data_id = str(uuid.uuid4())
                upload_file(SUBSTRATE_EXCEL, upload_bucket_path(st.experimental_user['name'], st.experimental_user['sub'], 'excel', 'substrate', data_id))
                upload_file(SUBSTRATE_IMAGE, upload_bucket_path(st.experimental_user['name'], st.experimental_user['sub'], 'image', 'substrate', data_id))
                st.dataframe(substrate_df)
                st.session_state['file_uploader_one'] = True
                # download button
                st.download_button(
                    label="Download as Excel",
                    data=load_and_prepare_excel_for_substrate(SUBSTRATE_EXCEL),
                    file_name='substrate_data.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    on_click='ignore'
                )

    # Fish and Invert Slate tab
    with fish_invert_tab:
        st.header("Fish and Invert Slate")
        uploaded_fish_invert = st.file_uploader(
            "Upload Fish and Invert Image",
            type=["jpg", "jpeg", "png"],
            key="fish_invert_uploader",
            on_change=on_file_two_uploaded
        )
        if uploaded_fish_invert is not None and not st.session_state['file_uploader_two']:
            image = handle_image_orientation(Image.open(uploaded_fish_invert))
            st.sidebar.image(image, caption="Uploaded Fish and Invert Image")
            # save the uploaded image
            save_uploaded_image(image, FISH_INVERT_IMAGE)
            # label generating
            with st.spinner("Generating Fish and Invert Labels", show_time = True):
                fish_and_invert_labels = image_label_generator_fish_invert(FISH_INVERT_IMAGE)
                st.toast("Fish and Invert Labels Generated")
                # dataframe generation
                fish_and_invert_df = create_fish_slate_dataframe(fish_and_invert_labels.model_dump(), FISH_INVERT_CSV)
                fish_slate_excel_creation(fish_and_invert_labels.model_dump(), FISH_INVERT_EXCEL)
                # upload the file
                data_id = str(uuid.uuid4())
                upload_file(FISH_INVERT_EXCEL, upload_bucket_path(st.experimental_user['name'], st.experimental_user['sub'], 'excel', 'fish_and_invert', data_id))
                upload_file(FISH_INVERT_IMAGE, upload_bucket_path(st.experimental_user['name'], st.experimental_user['sub'], 'image', 'fish_and_invert', data_id))
                st.dataframe(fish_and_invert_df)
                st.session_state['file_uploader_two'] = True
                # download button
                st.download_button(
                    label="Download as Excel",
                    data=load_and_prepare_excel_for_fish_slate(FISH_INVERT_EXCEL),
                    file_name='fish_and_invert_data.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    on_click='ignore'
                )

if __name__ == "__main__":
    reef_analyser()
