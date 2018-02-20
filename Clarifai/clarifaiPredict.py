from Clarifai import rest
from clarifai.rest import ClarifaiApp
from clarifai.rest import Image as ClImage
import os


app = ClarifaiApp(api_key = 'fb45dd17e3b24d3c84d012cc8f53941d')
model = app.models.get('newMaterials')

image = ClImage(file_obj=open('20170909_122423.jpg', 'rb'))
train =  model.predict([image])
tuplist = []
for key in train["outputs"][0]["data"]["concepts"]:
    for elem in key:
        if elem == "name":
            nameList = key
            #print nameList
            tup = (nameList["value"], nameList["name"])
            tuplist.append(tup)
#print tuplist

answer = tuplist[0][1]
print answer
