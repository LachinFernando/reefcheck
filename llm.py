import os
from pydantic import BaseModel, Field
import streamlit as st
import google.generativeai as genai
import PIL.Image
from pydantic import BaseModel
from typing import TypedDict, Annotated, List, Dict


from prompts import SLATE_IMAGE_INSTRUCTIONS, FISH_INVERT_INSTRUCTIONS



os.environ["GEMINI_API_KEY"] = st.secrets["gemini"]["GEMINI_API_KEY"]


# constants
MODEL = "gemini-2.5-flash"

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

class LabelRecordings(BaseModel):
    distance: str
    label: str
    label_status: bool
    
class InfoRecordings(BaseModel):
  site_name: str
  country_island: str
  team_leader: str
  data_recorded_by: str
  depth: str
  date: str
  time: str
  

class SegmentationLabels(BaseModel):
  info_segment: List[InfoRecordings]
  segment_one: List[LabelRecordings]
  segment_two: List[LabelRecordings]
  segment_three: List[LabelRecordings]
  segment_four: List[LabelRecordings]


class LabelRecordingsFishInvert(BaseModel):
    name: str = Field(description = "Species Name")
    distance_one: int
    distance_one_clear: bool 
    distance_two: int 
    distance_two_clear: bool 
    distance_three: int 
    distance_three_clear: bool 
    distance_four: int 
    distance_four_clear: bool


class SegmentationLabelsFishInvert(BaseModel):
    fish: List[LabelRecordingsFishInvert]
    invertebrates: List[LabelRecordingsFishInvert]
    impacts: List[LabelRecordingsFishInvert]
    coral_disease: List[LabelRecordingsFishInvert]
    rare_animals: List[LabelRecordingsFishInvert]



def image_label_generator(image_path: str, prompt: str = SLATE_IMAGE_INSTRUCTIONS):
    img = PIL.Image.open(image_path)

    model = genai.GenerativeModel(
        model_name=MODEL,
        generation_config={
            "response_mime_type": "application/json",
            "response_schema": SegmentationLabels,
        }
    )

    response = model.generate_content([prompt, img])

    # Convert JSON string into validated Pydantic object
    structured_output = SegmentationLabels.model_validate_json(response.text)

    return structured_output



def image_label_generator_fish_invert(image_path: str, prompt: str = FISH_INVERT_INSTRUCTIONS):
    img = PIL.Image.open(image_path)

    model = genai.GenerativeModel(
        model_name=MODEL,
        generation_config={
            "response_mime_type": "application/json",
            "response_schema": SegmentationLabelsFishInvert,
        }
    )

    response = model.generate_content([prompt, img])

    # Convert JSON string into validated Pydantic object
    structured_output = SegmentationLabelsFishInvert.model_validate_json(response.text)

    return structured_output





# def encode_image(image_path):
#   with open(image_path, "rb") as image_file:
#     return base64.b64encode(image_file.read()).decode('utf-8')


# def image_label_generator(image_local_path: str, prompt: str = SLATE_IMAGE_INSTRUCTIONS):
#     image_data = encode_image(image_local_path)
#     # set up the message
#     message = HumanMessage(
#         content=[
#             {"type": "text", "text": prompt},
#             {
#                 "type": "image_url",
#                 "image_url": {"url": f"data:image/png;base64,{image_data}"},
#             },
#         ],
#     )
#     # create a structured output
#     structured_llm = llm.with_structured_output(SegmentationLabels)
#     # invoke the llm to generatr an query
#     invoke_image_query = structured_llm.invoke([message])

#     return invoke_image_query


# def image_label_generator_fish_invert(image_local_path: str, prompt: str = FISH_INVERT_INSTRUCTIONS):
#     image_data = encode_image(image_local_path)
#     # set up the message
#     message = HumanMessage(
#         content=[
#             {"type": "text", "text": prompt},
#             {
#                 "type": "image_url",
#                 "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
#             },
#         ],
#     )
#     # create a structured output
#     structured_llm = llm.with_structured_output(SegmentationLabelsFishInvert)
#     # invoke the llm to generatr an query
#     invoke_image_query = structured_llm.invoke([message])

#     return invoke_image_query