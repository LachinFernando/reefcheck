import streamlit as st
import os
import uuid

from llm import image_label_generator, image_label_generator_fish_invert
from utils import create_substrate_dataframe, substrate_excel_creation, load_and_prepare_excel_for_substrate, fish_and_invert_dataframe_creator
from firebase import upload_file


# constants
SUBSTRATE_IMAGE = "substrate.png"
FISH_INVERT_IMAGE = "fish_and_invert.png"
SUBSTRATE_CSV = "substrate.csv"
SUBSTRATE_EXCEL = "substrate.xlsx"
FISH_INVERT_CSV = "fish_and_invert.csv"


def upload_bucket_path(user_name: str, user_id:str, type_: str, slate_type: str, data_id: str) -> str:

    user_names = user_name.split(" ")
    user_name_ = "_".join(user_names)

    if type_ == 'image':
        st.toast(f"Image Uploaded")
        return f"data/{slate_type}/{user_name_}_{user_id}/images/{data_id}.png"
    elif type_ == 'csv':
        st.toast(f"CSV Uploaded")
        return f"data/{slate_type}/{user_name_}_{user_id}/csv/{data_id}.csv"



def save_uploaded_image(uploaded_file, target_name):
    if uploaded_file is not None:
        # Save the uploaded file to the workspace
        with open(target_name, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.toast(f"File saved as {target_name}")


def reef_analyser():
    # Create two tabs
    substrate_tab, fish_invert_tab = st.tabs(["Substrate Slate", "Fish and Invert Slate"])

    # Substrate Slate tab
    with substrate_tab:
        st.header("Substrate Slate")
        uploaded_substrate = st.file_uploader(
            "Upload Substrate Image",
            type=["jpg", "jpeg", "png"],
            key="substrate_uploader"
        )
        if uploaded_substrate is not None:
            st.sidebar.image(uploaded_substrate, caption="Uploaded Substrate Image")
            # save the uploaded image
            save_uploaded_image(uploaded_substrate, SUBSTRATE_IMAGE)
            # label generating
            with st.spinner("Generating Substrate Labels", show_time = True):
                substrate_labels = image_label_generator(SUBSTRATE_IMAGE)
                st.toast("Substrate Labels Generated")
                # dataframe generation
                substrate_df = create_substrate_dataframe(substrate_labels.model_dump(), SUBSTRATE_CSV)
                # upload the file
                data_id = str(uuid.uuid4())
                upload_file(SUBSTRATE_CSV, upload_bucket_path(st.experimental_user['name'], st.experimental_user['sub'], 'csv', 'substrate', data_id))
                upload_file(SUBSTRATE_IMAGE, upload_bucket_path(st.experimental_user['name'], st.experimental_user['sub'], 'image', 'substrate', data_id))
                st.dataframe(substrate_df)
                # download button
                st.download_button(
                    label="Download as Excel",
                    data=load_and_prepare_excel_for_substrate(substrate_labels.model_dump(), SUBSTRATE_EXCEL),
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
            key="fish_invert_uploader"
        )
        if uploaded_fish_invert is not None:
            st.sidebar.image(uploaded_fish_invert, caption="Uploaded Fish and Invert Image")
            # save the uploaded image
            save_uploaded_image(uploaded_fish_invert, FISH_INVERT_IMAGE)
            # label generating
            with st.spinner("Generating Fish and Invert Labels", show_time = True):
                fish_and_invert_labels = image_label_generator_fish_invert(FISH_INVERT_IMAGE)
                st.toast("Fish and Invert Labels Generated")
                # dataframe generation
                fish_and_invert_df = fish_and_invert_dataframe_creator(fish_and_invert_labels, FISH_INVERT_CSV)
                # upload the file
                data_id = str(uuid.uuid4())
                upload_file(FISH_INVERT_CSV, upload_bucket_path(st.experimental_user['name'], st.experimental_user['sub'], 'csv', 'fish_and_invert', data_id))
                upload_file(FISH_INVERT_IMAGE, upload_bucket_path(st.experimental_user['name'], st.experimental_user['sub'], 'image', 'fish_and_invert', data_id))
                st.dataframe(fish_and_invert_df)
                # download button
                st.download_button(
                    label="Download as Excel",
                    data=convert_csv_to_excel(FISH_INVERT_CSV),
                    file_name='fish_and_invert_data.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    on_click='ignore'
                )

if __name__ == "__main__":
    reef_analyser()
