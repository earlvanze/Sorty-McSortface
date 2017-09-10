from clarifai import rest
from clarifai.rest import ClarifaiApp
from clarifai.rest import Image as ClImage
import os

#app = ClarifaiApp(api_key='f3c29ad5fe7e43adbd734a1c88479244')
app = ClarifaiApp(api_key = 'fb45dd17e3b24d3c84d012cc8f53941d')

model = app.models.get('recyclables')
model.train()
