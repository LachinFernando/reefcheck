import cv2
import os
import json
import numpy as np
import logging

from paddleocr import LayoutDetection
from paddlex import create_model


class LayoutDetector:
    def __init__(self, model):
        self.model = model
        self.logger = logging.getLogger(self.__class__.__name__)

    def detect(self, image_path):
        print(f"====== Running layout detection on {image_path} ======")
        
        output = self.model.predict(
            image_path, 
            batch_size=1, 
            layout_nms=True, 
            threshold={0:0.5, 1:0.5, 2:0.5, 6:0.5, 8:0.5}   
        )
        
        if output and len(output) > 0:
            print(f"First result keys: {output[0].keys() if isinstance(output[0], dict) else 'Not a dict'}")
            if isinstance(output[0], dict) and "boxes" in output[0]:
                print(f"Number of boxes detected: {len(output[0]['boxes'])}")
        
        print("Layout detection completed")
        return output
    

class ImageCropper:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def crop_image(self, coordinates, output_path='./ocr_outputs/cropped.png'):
        print("====== Cropping detected region ======")
        
        # Validate input
        if not coordinates or len(coordinates) == 0:
            raise ValueError("No layout detected! The coordinates list is empty. Try lowering detection thresholds.")
        
        print(f"Number of detected regions: {len(coordinates)}")
        
        # Check if the first result has boxes
        if "boxes" not in coordinates[0]:
            raise ValueError(f"Expected 'boxes' key in coordinates. Got keys: {coordinates[0].keys()}")
        
        if len(coordinates[0]["boxes"]) == 0:
            raise ValueError("No boxes found in the detected layout. Try lowering detection thresholds.")
        
        print(f"Number of boxes in first region: {len(coordinates[0]['boxes'])}")
        
        # Get image
        img = coordinates[0]["input_img"]
        print(f"Image shape: {img.shape}")
        
        # Get coordinates of the first box (usually the table)
        x1, y1, x2, y2 = coordinates[0]["boxes"][0]["coordinate"]
        print(f"Cropping box: x1={x1}, y1={y1}, x2={x2}, y2={y2}")
        
        # Convert to int
        x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
        
        # Validate coordinates
        if x2 <= x1 or y2 <= y1:
            raise ValueError(f"Invalid box coordinates: ({x1}, {y1}, {x2}, {y2})")
        
        # Crop (NumPy uses [y1:y2, x1:x2])
        cropped = img[y1:y2, x1:x2]
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        cv2.imwrite(output_path, cropped)
        print(f"Cropped image saved to {output_path}")
        
        return output_path


class CellPredictor:
    def __init__(self, model):
        self.model = model
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def capture_cells(self, image_path, output_dir='./ocr_outputs'):
        print(f"====== Running table recognition on {image_path} ======")
        cell_output = self.model.predict(image_path, threshold=0.1, batch_size=1)
        
        json_path = os.path.join(output_dir, 'response.json')

        for res in cell_output:
            res.save_to_img(output_dir)
            res.save_to_json(json_path)
        
        with open(json_path, "r") as f:
            data = json.load(f)
        
        coordinates = data.get('boxes', [])
        
        if not coordinates:
            raise ValueError("No table cells detected!")
        
        print(f"Number of cells detected: {len(coordinates)}")

        list_a = []
        for cap in coordinates:
            list_a.append(cap.get('coordinate'))
        
        # Sort by row (y1) then column (x1)
        avected_sort = sorted(list_a, key=lambda box: (box[1], box[0]))

        print("Table cell recognition completed")
        return avected_sort


class DocumentPipeline:
    def __init__(self, layoutdetector, cropper, cellpredictor):
        self.layoutdetector = layoutdetector
        self.cropper = cropper
        self.cellpredictor = cellpredictor
        self.logger = logging.getLogger(self.__class__.__name__)

    def run(self, image_path):
        self.logger.info(f"Starting pipeline for {image_path}")
        print(f"====== Starting pipeline for {image_path} ======")
        
        # Step 1: Detect table layout
        table = self.layoutdetector.detect(image_path)
        
        # Step 2: Crop the table region
        cropped_image_path = self.cropper.crop_image(table)
        
        # Step 3: Detect individual cells
        box_coordinates = self.cellpredictor.capture_cells(cropped_image_path)

        self.logger.info(f"Pipeline completed for {image_path}")
        print(f"Pipeline completed for {image_path}")
        return box_coordinates


def ocr_pipe(IMAGE_PATH):
    model_1 = LayoutDetection(model_name="PP-DocLayout_plus-L")
    model_2 = create_model(model_name="RT-DETR-L_wired_table_cell_det")

    ocr_pipeline = DocumentPipeline(
        LayoutDetector(model_1),
        ImageCropper(),
        CellPredictor(model_2)
    )

    try:
        box_coordinates = ocr_pipeline.run(IMAGE_PATH)
        print("====== All Coordinates are printed ======")
        return box_coordinates

    except Exception as e:
        print(f"Error in pipeline: {e}")
        import traceback
        traceback.print_exc()
        raise