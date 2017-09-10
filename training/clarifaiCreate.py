from clarifai import rest
from clarifai.rest import ClarifaiApp
from clarifai.rest import Image as ClImage
import os

#app = ClarifaiApp(api_key='f3c29ad5fe7e43adbd734a1c88479244')
#app = ClarifaiApp(api_key = 'fb45dd17e3b24d3c84d012cc8f53941d')
app = ClarifaiApp(api_key = 'e59b78f56ed64e12b496009fdbbe5fd0')

#model = app.models.get('general-v1.3')
#image = ClImage(url='https://samples.clarifai.com/metro-north.jpg')
#train  = model.predict([image])


#app.inputs.create_image_from_url(url="https://samples.clarifai.com/puppy.jpeg", concepts=['boscoe'])
#app.inputs.create_image_from_filename("paper/103257504204.jpg")


# loop through all files of every folder and put path along with labeling it by the materials

# plastic

for dir, subdir, files in os.walk("paper"):
    for file in files:
        newpath = os.path.join(dir, file)
        print newpath
        try :
            app.inputs.create_image_from_filename(newpath,  concepts=['paper'])
        except :
            continue

for dir, subdir, files in os.walk("plastic"):
    for file in files:
        newpath = os.path.join(dir, file)
        print newpath
        try :
            app.inputs.create_image_from_filename(newpath,  concepts=['plastic'])
        except :
            continue

for dir, subdir, files in os.walk("metal"):
    for file in files:
        newpath = os.path.join(dir, file)
        print newpath
        try :
            app.inputs.create_image_from_filename(newpath, concepts=['metal'])
        except :
            continue


model = app.models.create('recyclables', concepts=['paper', 'plastic', 'metal'])


"""
for key in train["outputs"][0]["data"]["concepts"]:
    for elem in key:
        if elem == "name":
            nameList = key["name"]
            print key["name"]
"""
