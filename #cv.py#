from clarifai import rest
from clarifai.rest import ClarifaiApp
import json

app = ClarifaiApp(api_key='fb45dd17e3b24d3c84d012cc8f53941d')
model = app.models.get('general-v1.3')

with open('categories.json') as categories_file:
    categories = json.load(categories_file)


def predict(filename):
    response = model.predict_by_filename(filename)
    # check if response was ok
    if response['status']['code'] != 10000:
        # exit out
        return 'error'

    # get tags
    tags = []
    for output in response['outputs']:
        for concept in output['data']['concepts']:
            tags.append(concept['name'])

    print tags
    # determine category
    for category in categories:
        intersection = set(category['keywords']).intersection(set(tags))
        if len(intersection) > 0:
            return category['name']
    # no intersections
    return 'none'

files = ['lays.jpg', 'motor.jpg', 'soylent.jpg', 'coke.jpg', 'bottle.jpg', 'set.jpg', 'plastic_wrapper.jpg', 'knife.jpg', 'fork.jpg', 'utensils.jpg', 'sap.jpg', 'napkin.jpg', 'styrofoam.jpg', 'paper.jpg']

for f in files:
    print f + ": " + predict('img/' + f)
