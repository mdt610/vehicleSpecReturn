import sys
from edmunds.edmunds import Edmunds
from pprint import pprint
import json

DEBUG = False

#api = Edmunds('examplekey', True)  # Add True for api debug mode

print "The purpose of this program is to return the specs of a new car you're interested in"

key = raw_input("First, I will need you to enter your own Edmunds.com API Key: ")

api = Edmunds(key)

# Check api key
test = api.make_call('/api/vehicle/v2/makes/count')
if 'errorType' in test:
    print "Sorry, the api key you've entered is not valid"
    print "\nThe program will now exit.\n"
    sys.exit()

print "Lets get started by giving you the list of makes to choose from."

all_makes = api.make_call('/api/vehicle/v2/makes?state=new')  # get makes that have new cars available

for makes in all_makes["makes"]:
    print makes["niceName"]  # prints make names in the response
car = {}

if DEBUG:  # for when I want to read the output to a file without needing to give it input
    car['make'] = 'honda'
else: 
    car['make'] = raw_input("Select one of the makes from the list shown above: ").lower().strip()

models = api.make_call('/api/vehicle/v2/{0}/models?state=new'.format(car['make']))  # gets the models for the make specified

if models['modelsCount'] > 0:
    print "\nHere are the models we found for {0}".format(car['make'])
    for model in models["models"]:
        print model["niceName"]  # prints the model names found
else:
    print "\nSorry, no models were found using the given make\n"
    print "The program will now exit.\n"
    sys.exit()

if DEBUG:
    car['model'] = 'accord'
else:
    # ask for desired model
    car['model'] = raw_input("\nSelect one of the models from the list shown above: ").lower().strip()

mk_mdls = api.make_call('/api/vehicle/v2/{0}/{1}?state=new'.format(car['make'], car['model']))

if 'errorType' in mk_mdls:
    print "\nI'm sorry but you have entered an invalid selection.\n{0}\n".format(mk_mdls['message'])
    print "The program will now exit.\n"
    sys.exit()
elif mk_mdls['years']:
    print "\nThe following years are available for the {0} {1}".format(car['make'], car['model'])
    for y in mk_mdls['years']:
        print y['year']  # prints the available years for the make and model specified

if DEBUG:
    car['year'] = '2014'
else: 
    car['year'] = raw_input("Enter one of the 4 digit years shown above: ").strip()
    if int(car['year']) < 1990 or int(car['year']) > 2016:
        print "You did not enter a valid 4 digit year."
        print "\nThe program will now exit.\n"
        sys.exit()

mk_mdl_yr = api.make_call('/api/vehicle/v2/{0}/{1}/{2}?state=new'.format(car['make'], car['model'], car['year']))

def get_style_id():
    for style in mk_mdl_yr['styles']:
        print "\n*** {0} {1} {2} {3} ***".format(car['year'], car['make'], car['model'], style['name'])
        x = raw_input("Is this the car you are looking for? (Y) or (N): ").lower().strip()
        if 'y' in x:
	    return style['id'], style['trim']
        else:
            continue

if not mk_mdl_yr['styles']:
    print "Sorry, but the year you chose did not return any vehicles for the {0} {1}\n".format(car['make'], car['model'])
    print "The program will now exit."
    sys.exit()

#car['styleid'], car['trim'] = get_style_id()

print "***** %s ******" % car

while 'styleid' not in car:
    try:
        car['styleid'], car['trim'] = get_style_id()
    except TypeError:
        print "\n******************************************************"
        print "*** Sorry, but you need to pick a trim to continue ***"
        print "******************************************************\n"

# Now that we finally have the style id, we can ask the api for the engine and transmission specs
print "\nBased on your selection of the car {0} {1} {2} {3}\nThe specs are as follows:\n".format(car['year'], car['make'], car['model'], car['trim'])
engine = api.make_call('/api/vehicle/v2/styles/{0}/engines?availability=standard'.format(car['styleid']))
trans = api.make_call('/api/vehicle/v2/styles/{0}/transmissions?availability=standard'.format(car['styleid']))
for e in engine['engines']:
    print "Cylinders: {0}".format(e['cylinder'])
    print "Horsepower: {0} hp".format(e['horsepower'])
    print "Torque: {0} pounds-feet".format(e['torque'])
    print "Engine Displacement: {0} cc and {1} L".format(e['displacement'], e['size'])
    print "Fuel Type: {0}".format(e['fuelType'])
for t in trans['transmissions']:
    print "{0} speed {1} Transmission comes standard".format(t['numberOfSpeeds'], t['transmissionType'])

print "\nThank you for using the vehicle spec return! :-D\n"
