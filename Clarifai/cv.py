import sys
import time
sys.argv

from Naked.toolshed.shell import execute_js, muterun_js

result = execute_js('set_status.js processing')

#if len(sys.argv) < 2:
    # error
#    print 0

#input_file = sys.argv[1]

input_file = ""

from Clarifai import rest
from clarifai.rest import ClarifaiApp
import json

#app = ClarifaiApp(api_key='fb45dd17e3b24d3c84d012cc8f53941d')
app = ClarifaiApp(api_key='e59b78f56ed64e12b496009fdbbe5fd0')
model = app.models.get('recyclables')
#model = app.models.get('aaa03c23b3724a16a56b629203edc62c')

CONFIDENCE_LEVEL = 0.7

with open('categories.json') as categories_file:
    categories = json.load(categories_file)


# 1 is everything else
    
def predict(filename):
    response = model.predict_by_filename(filename)
    # check if response was ok
    if response['status']['code'] != 10000:
        # exit out
        return 1

    # get tags
    tags = []
    for output in response['outputs']:
        for concept in output['data']['concepts']:
            print concept['name'] + ": " + str(concept['value'])
            if concept['value'] > CONFIDENCE_LEVEL:
                tags.append(concept['name'])

    # determine category
    for category in categories:
        intersection = set(category['keywords']).intersection(set(tags))
        if len(intersection) > 0:
#            result = execute_js('set_status.js ' + category['name'])
 #           result = execute_js('update.js ' + category['name'])
#            time.sleep(1)
#            result = execute_js('set_status.js waiting')
#            return 4
            return category['code']
    # no intersections
    #result = execute_js('set_status.js nonrecyclable')
    #result = execute_js('update.js ee')
    #time.sleep(1)
    #result = execute_js('set_status.js waiting')
    return 1


#predict(input_file)
