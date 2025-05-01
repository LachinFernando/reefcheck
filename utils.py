from collections import defaultdict
import pandas as pd
from io import BytesIO


def dataframe_creator(response: dict, csv_name: str) -> pd.DataFrame:
    # constants lists
    data_list = defaultdict(list)
    benchmarks = [0, 9.5, 19.5, 34.5, 44.5, 59.5, 69.5, 84.5, 94.5]
    merge_prefixes = ["0 - 19.5m", "25 - 44.5m", "50 - 65.5m", "75 - 94.5m"]
    final_labels = ["Distance", "Label", "Clear"]
    segment_list = []
    merge_list = []
    segment_count = 0
    segment_id = 1
    merge_index = 0

    for index in range(len(benchmarks)):
        if index == (len(benchmarks) -1):
            break
        if segment_count == 2:
            segment_count = 0
            segment_id += 1
        if index != 0 and index % 2 == 0:
            merge_index +=1
        for response_ in response.labels:
            distance = float(response_.distance)
            if index == 0 and distance >= benchmarks[index] and distance <= benchmarks[index + 1]:
                data_list[f"distance ({benchmarks[index]}-{benchmarks[index + 1]}m)"].append(distance)
                data_list[f"label ({benchmarks[index]}-{benchmarks[index + 1]}m)"].append(response_.label)
                data_list[f"label_status ({benchmarks[index]}-{benchmarks[index + 1]}m)"].append(response_.label_status)
            else:
                if distance > benchmarks[index] and distance <= benchmarks[index + 1]:
                    data_list[f"distance ({benchmarks[index]}-{benchmarks[index + 1]}m)"].append(distance)
                    data_list[f"label ({benchmarks[index]}-{benchmarks[index + 1]}m)"].append(response_.label)
                    data_list[f"label_status ({benchmarks[index]}-{benchmarks[index + 1]}m)"].append(response_.label_status)

        # create segment list
        segment_name = "Segment_{}".format(segment_id)
        merge_name = merge_prefixes[merge_index]
        segment_list.extend([segment_name]*3)
        merge_list.extend([merge_name]*3)
        #segment_list.extend([(segment_name,f"{merge_prefixes[merge_index]}", f"{prefix} ({benchmarks[index]}-{benchmarks[index + 1]}m)") for prefix in labels_prefix])
        segment_count += 1

    # create a dataframe
    df = pd.DataFrame.from_dict(data_list)
    df_columns = list(df.columns)

    # columns
    cols = []
    for val_ in range(8):
        cols.extend([f"distance_{val_}", f"label_{val_}", f"status_{val_}"])

    # create multi index
    arrays = [
        segment_list,
        merge_list,
        cols
    ]
    columns = pd.MultiIndex.from_arrays(arrays)
    # create a dataframe
    df = pd.DataFrame(df.iloc[:,:].values, columns=columns)  

    # save the dataframe to a csv file
    df.to_csv(csv_name, index=False)    

    return df


def convert_csv_to_excel(csv_path: str):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_path)

    # Write the DataFrame to a BytesIO stream as an Excel file
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
        output.seek(0)

    return output.getvalue()


def fish_and_invert_dataframe_creator(response: dict, csv_name: str) -> pd.DataFrame:
    main_keys = ["fish", "invertebrates", "impacts", "coral_disease", "rare_animals"]

    # list of dicts
    dict_list = []
    response_dict = response.model_dump()

    info_df = pd.concat([pd.DataFrame.from_dict(response_dict[key_]) for key_ in main_keys])
    # save the dataframe
    info_df.to_csv(csv_name, index=False)
    
    return info_df