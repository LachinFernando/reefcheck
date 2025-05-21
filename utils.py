from collections import defaultdict
import pandas as pd
from io import BytesIO
import xlsxwriter
from openpyxl import load_workbook
from PIL import Image, ExifTags


# Image utilities
def handle_image_orientation(image: Image.Image) -> Image.Image:
    """
    Handle image orientation based on EXIF data.
    
    Args:
        image: PIL Image object
        
    Returns:
        PIL Image object with correct orientation
    """
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = dict(image._getexif().items())

        if exif[orientation] == 3:
            image = image.rotate(180, expand=True)
        elif exif[orientation] == 6:
            image = image.rotate(270, expand=True)
        elif exif[orientation] == 8:
            image = image.rotate(90, expand=True)
    except (AttributeError, KeyError, IndexError):
        # cases: image don't have exif data
        pass
    
    return image

# substrate analysis
def generate_keys(key_list, multiplier = 3):
    new_list = []

    for label in key_list:
        new_list.extend([label]*multiplier)

    return new_list


def create_substrate_dataframe(response_data: dict, csv_name: str) -> pd.DataFrame:
    segment_distances = ["0 - 19.5m", "25 - 44.5m", "50 - 65.5m", "75 - 94.5m"]

    # get unique keys
    response_keys = list(response_data.keys())
    # create dataframes
    df = pd.concat([pd.DataFrame.from_dict(response_data[key]) for key in list(response_data.keys())], axis = 1)

    # create unique column names
    column_names = []
    for num in range(len(list(response_data.keys()))):
        column_names.extend([f"distance_{num}", f"label_{num}", f"clear_{num}"])
    # set column names
    df.columns = column_names

    # generate multi-level index
    segment_list = generate_keys(list(response_data.keys()))
    merge_list = generate_keys(segment_distances)

    # create multi index
    arrays = [
        segment_list,
        merge_list,
        column_names
    ]
    columns = pd.MultiIndex.from_arrays(arrays)
    # create a dataframe
    df = pd.DataFrame(df.iloc[:,:].values, columns=columns)  

    # save the dataframe to a csv file
    df.to_csv(csv_name, index=False)

    return df


def extract_details(info: dict) -> list:

    return [info["distance"], info["label"], info["label_status"]]


def extract_single_attributes(selected_set: list, index_val: int) -> list:
    sub_segments = []
    # first segment
    first_set = selected_set[index_val]
    second_set = selected_set[index_val + 20]
    sub_segments.extend(extract_details(first_set))
    sub_segments.extend(extract_details(second_set))

    return sub_segments


def substrate_excel_creation(response_data: dict, excel_name: str):
    selected_set_one = response_data["segment_one"]
    selected_set_two = response_data["segment_two"]
    selected_set_three = response_data["segment_three"]
    selected_set_four = response_data["segment_four"]


    final_segments = []
    for index in range(20):
        sub_set_segments = []
        # first segment
        sub_set_segments.extend(extract_single_attributes(selected_set_one, index))
        # seconds segment
        sub_set_segments.extend(extract_single_attributes(selected_set_two, index))
        # seconds segment
        sub_set_segments.extend(extract_single_attributes(selected_set_three, index))
        # seconds segment
        sub_set_segments.extend(extract_single_attributes(selected_set_four, index))
        # append the segment
        final_segments.append(sub_set_segments)

    # Create a workbook and add a worksheet.
    workbook = xlsxwriter.Workbook(excel_name)
    worksheet = workbook.add_worksheet()

    # Add a bold format to use to highlight cells.
    bold = workbook.add_format({'bold': True, 'center_across': True, 'border': True})

    # Add a border
    border = workbook.add_format({'border': True})

    # Add a number format for cells with money.
    not_clear = workbook.add_format({'bold': True, 'bg_color': 'red', 'border': True})

    # Write some data headers.
    worksheet.merge_range("A1:P1", "Substrate Analysis", bold)
    worksheet.merge_range("A2:D2", "Segment One", bold)
    worksheet.merge_range("E2:H2", "Segment Two", bold)
    worksheet.merge_range("I2:L2", "Segment Three", bold)
    worksheet.merge_range("M2:P2", "Segment Four", bold)

    # distances
    worksheet.merge_range("A3:D3", "0 - 19.5m", bold)
    worksheet.merge_range("E3:H3", "25 - 44.5m", bold)
    worksheet.merge_range("I3:L3", "50 - 69.5m", bold)
    worksheet.merge_range("M3:P3", "75 - 94.5", bold)


    row = 3
    # adding records
    for diff_segments in final_segments:
        col = 0
        for range_index in range(0, 24, 3):
            worksheet.write(row, col, diff_segments[range_index], border)
            col += 1
            worksheet.write(row, col, diff_segments[range_index +1], not_clear if not diff_segments[range_index +2] else border)
            col += 1
        row += 1


    workbook.close()


def load_and_prepare_excel_for_substrate(excel_name: str):
    # Load the workbook and select the active sheet
    workbook = load_workbook(excel_name)
    with BytesIO() as buffer:
        workbook.save(buffer)
        buffer.seek(0)
        return buffer.getvalue()


def create_fish_slate_dataframe(response_data: dict, csv_name: str) -> pd.DataFrame:
    # distances are constants
    distances = ["0 - 20m", "25 - 45m", "50 - 75m", "75 - 95m"]

    main_keys = list(response_data.keys())

    info_df = pd.concat([pd.DataFrame.from_dict(response_data[key_]) for key_ in main_keys])
    
    new_columns = []
    new_columns.append("name")
    for distance_index in range(len(distances)):
        new_columns.extend([distances[distance_index], "set_{}_clear".format(distance_index)])

    info_df.columns = new_columns

    # save the dataframe to a csv file
    info_df.to_csv(csv_name, index=False)

    return info_df


def fish_slate_excel_creation(response_data: dict, excel_name: str):

    data_list = []

    for key_ in list(response_data.keys()):
        data_list.extend(response_data[key_])


    distances = ["0 - 20m", "25 - 45m", "50 - 75m", "75 - 95m"]
    # Create a workbook and add a worksheet.
    workbook = xlsxwriter.Workbook(excel_name)
    worksheet = workbook.add_worksheet()

    # Add a bold format to use to highlight cells.
    bold = workbook.add_format({'bold': True, 'center_across': True, 'border': True})

    # sub category
    sub_format = workbook.add_format({'bold': True, 'center_across': True, 'border': True, 'bg_color': 'green'})

    # Add a border
    border = workbook.add_format({'border': True})

    # Add a number format for cells with money.
    not_clear = workbook.add_format({'bold': True, 'bg_color': 'red', 'border': True})

    worksheet.merge_range("A1:E1", "Fish Slate Analysis", bold)
    worksheet.write(1, 0, "Type", bold)
    worksheet.set_column('A:A', 30)
    # distances
    for index in range(len(distances)):
        worksheet.write(1, index + 1, distances[index] , bold)

    row = 2
    col = 0
    for key_ in list(response_data.keys()):
        worksheet.write(row, col, key_, sub_format)
        row +=1 
        for data_dict in response_data[key_]:
            worksheet.write(row, col, data_dict["name"], border)
            worksheet.write(row, col+1, data_dict["distance_one"], not_clear if not data_dict["distance_one_clear"] else border)
            worksheet.write(row, col+2, data_dict["distance_two"], not_clear if not data_dict["distance_two_clear"] else border)
            worksheet.write(row, col+3, data_dict["distance_three"], not_clear if not data_dict["distance_three_clear"] else border)
            worksheet.write(row, col+4, data_dict["distance_four"], not_clear if not data_dict["distance_four_clear"] else border)
            row += 1


    workbook.close()


def load_and_prepare_excel_for_fish_slate(excel_name: str):
    # Load the workbook and select the active sheet
    workbook = load_workbook(excel_name)
    with BytesIO() as buffer:
        workbook.save(buffer)
        buffer.seek(0)
        return buffer.getvalue()