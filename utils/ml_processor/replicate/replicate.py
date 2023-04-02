from settings import REPLICATE_API_TOKEN
from utils.file_upload.s3 import upload_image
from utils.ml_processor.ml_interface import MachineLearningProcessor
import replicate
import os
import requests as r
import json

from utils.ml_processor.replicate.constants import REPLICATE_MODEL, ReplicateModel


class ReplicateProcessor(MachineLearningProcessor):
    def __init__(self):
        os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN
        self._set_urls()

    def _set_urls(self):
        self.dreambooth_training_url = "https://dreambooth-api-experimental.replicate.com/v1/trainings"
        self.training_data_upload_url = "https://dreambooth-api-experimental.replicate.com/v1/upload/data.zip"

    def get_model(self, input_model: ReplicateModel):
        model = replicate.models.get(input_model.name)
        model_version = model.versions.get(input_model.version) if input_model.version else model
        return model_version
    
    def get_model_by_name(self, model_name, model_version=None):
        model = replicate.models.get(model_name)
        model_version = model.versions.get(model_version) if model_version else model
        return model_version
    
    def predict_model_output(self, model: ReplicateModel, **kwargs):
        model_version = self.get_model(model)
        output = model_version.predict(**kwargs)
        return output

    def inpainting(self, video_name, input_image, prompt, negative_prompt):
        model = self.get_model(REPLICATE_MODEL.andreas_sd_inpainting)
        
        mask = "mask.png"
        mask = upload_image("mask.png")
            
        if not input_image.startswith("http"):        
            input_image = open(input_image, "rb")

        output = model.predict(mask=mask, image=input_image,prompt=prompt, invert_mask=True, negative_prompt=negative_prompt,num_inference_steps=25)    

        return output[0]
    
    def upload_training_data(self, file_path):
        headers = {
            "Authorization": "Token " + os.environ.get("REPLICATE_API_TOKEN"),
            "Content-Type": "application/zip"
        }
        response = r.post(self.training_data_upload_url, headers=headers)
        data = response.json()

        with open(file_path, 'rb') as f:
            r.put(data['upload_url'], data=f, headers=headers)
        
        return data['upload_url'], data['serving_url']
    
    def dreambooth_training(self, training_file_url, instance_prompt, class_prompt, max_train_steps, model_name):
        headers = {
            "Authorization": "Token " + os.environ.get("REPLICATE_API_TOKEN"),
            "Content-Type": "application/json"
        }
        payload = {
            "input": {
                "instance_prompt": instance_prompt,
                "class_prompt": class_prompt,
                "instance_data": training_file_url,
                "max_train_steps": max_train_steps
            },
            "model": "peter942/" + str(model_name),
            "trainer_version": "cd3f925f7ab21afaef7d45224790eedbb837eeac40d22e8fefe015489ab644aa",
            "webhook_completed": "https://example.com/dreambooth-webhook"
        }

        response = r.post(self.dreambooth_training_url, headers=headers, data=json.dumps(payload))
        response = (response.json())
        return response
    
    def remove_background(self, project_name, input_image):
        if not input_image.startswith("http"):        
            input_image = open(input_image, "rb")

        model = self.get_model(REPLICATE_MODEL.pollination_modnet)
        output = model.predict(image=input_image)
        return output