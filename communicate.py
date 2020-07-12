from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import json
import os
from math import sin, cos, sqrt, atan2, radians

# approximate radius of earth in km
R = 6373.0

#Find distance between passed coordinates and the constant coordinates. Returns distance in KM.
def calc_distance(cord_lat, cord_long):
    lat1 = radians(float(cord_lat))
    lon1 = radians(float(cord_long))
    lat2 = radians(39.1222411)
    lon2 = radians(-77.13352991)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance


# Load the endpoint from file
with open('/home/ec2-user/environment/endpoint.json') as json_file:  
    data = json.load(json_file)

# Fetch the deviceName from the current folder name
deviceName = os.path.split(os.getcwd())[1]

# Set the destinationDeviceName depending on this deviceName
if deviceName == 'car1':
    destinationDeviceName = 'car2'
else:
    destinationDeviceName = 'car1'

device1 = 'car1'
device2 = 'car2'
device3 = 'car3'
device4 = 'car4'
device5 = 'car5'

# Build useful variable for code
dev1Topic = 'scalable/messaging/' + device1
dev2Topic = 'scalable/messaging/' + device2
dev3Topic = 'scalable/messaging/' + device3
dev4Topic = 'scalable/messaging/' + device4
dev5Topic = 'scalable/messaging/' + device5

alertTopic = 'scalable/alerting' 
fleetTopic = 'scalable/fleet' 
keyPath = 'private.pem.key'
certPath = 'certificate.pem.crt'
caPath = '/home/ec2-user/environment/root-CA.crt'
clientId = deviceName
host = data['endpointAddress']
port = 8883
fleet = {}

myAWSIoTMQTTClient = AWSIoTMQTTClient(deviceName)
myAWSIoTMQTTClient.configureEndpoint(host, port)
myAWSIoTMQTTClient.configureCredentials(caPath, keyPath, certPath)
myAWSIoTMQTTClient.connect()


# Callback function for fleet topic
def onFLeetMessageCallback(client, userdata, message):
    input_split = message.payload.split("|")
    message_received = input_split[0]
    pubTopic = input_split[2]
    print("Message received on topic " + message.topic + ": " + message_received)
    message_split = message_received.split(":",1)
    if message_split[0] == 'FleetInfo':
        data_1 = json.loads(message_split[1])
        fleet.update(data_1)

# Function to subscribe to IoT topic
def subscribeIoTTopic(topic, funcName):
    myAWSIoTMQTTClient.subscribe(topic, 1, funcName)


# Function to publish payload to IoT topic
def publishToIoTTopic(topic, payload):
    # TODO 4: Implement function to publish to specified IoT topic using device object
    #         that you will create
    myAWSIoTMQTTClient.publish(topic, payload, 1)

def onMessageCallback(client, userdata, message):
    input_split = message.payload.split("|")
    message_received = input_split[0]
    pubTopic = input_split[2]
    print("Message received on topic " + message.topic + ": " + message_received)
    message_split = message_received.split(":",1)
    if message_split[0] == 'GPS':
        coord_latitude = message_split[1].split(",")[0]
        coord_longitude = message_split[1].split(",")[1]
        print('Received longitude: ', coord_longitude , ', and latitude:', coord_latitude)
        dist = calc_distance(coord_latitude, coord_longitude)
        print('Distance is: ',dist, 'KM')
        if dist < 0.001:
            print('DANGER: Distance less than 1 Meters')
        elif dist < 0.01:
            print('ALERT: Distance is less than 10 Meters')
    elif message_split[0] == 'SOS':
        alert_message = message_split[1]
        print('Received Alert Message: ', alert_message)
        data = {}
        data['device'] = deviceName
        data['longitude'] = '-77.13352991'
        data['latitude'] = '39.1222411'
        data['message'] = alert_message
        alert_json_data = json.dumps(data)
        myAWSIoTMQTTClient.publish(alertTopic, alert_json_data, 0)
        print('Message Sent to Alert Channel')
    elif message_split[0] == 'JoinFleet':
        fleet_size = len(fleet)
        if fleet_size > 0:
            fleet_size = fleet_size-2
        print("fleet size is: ", fleet_size)
        if fleet_size == 0:
            print("Creating new fleet with ",  message_split[1])
            myAWSIoTMQTTClient.publish(pubTopic, 'FleetChannel:{0}|{1}|{2}'.format(fleetTopic,pubTopic,message.topic), 0)
            fleet[str(fleet_size)] = deviceName
            fleet[str(fleet_size+1)] = message_split[1]
            fleet['Leader'] = str(fleet_size)
            fleet['Fleet_Speed'] = '60 KMPH'
            myAWSIoTMQTTClient.publish(pubTopic, 'FleetInfo:{0}|{1}|{2}'.format(json.dumps(fleet),pubTopic,message.topic), 0)
            myAWSIoTMQTTClient.publish(fleetTopic, 'FleetInfo:{0}|{1}|{2}'.format(json.dumps(fleet),fleetTopic,message.topic), 0)
        elif fleet_size < 3:
            print('Joining ',  message_split[1], ' to fleet. Using fleet channel ', fleetTopic , ' for communication')
            myAWSIoTMQTTClient.publish(pubTopic, 'FleetChannel:{0}|{1}|{2}'.format(fleetTopic,pubTopic,message.topic), 0)
            fleet[str(fleet_size+1)] = message_split[1]
            myAWSIoTMQTTClient.publish(pubTopic, 'FleetInfo:{0}|{1}|{2}'.format(json.dumps(fleet),pubTopic,message.topic), 0)
            myAWSIoTMQTTClient.publish(fleetTopic, 'FleetInfo:{0}|{1}|{2}'.format(json.dumps(fleet),fleetTopic,message.topic), 0)
        else:
            #publishToIoTTopic(pubTopic, 'Fleet Size is full')
            myAWSIoTMQTTClient.publish(pubTopic, 'Fleet Size is full|{0}|{1}'.format(pubTopic,message.topic), 0)
    #elif message_split[0] == 'FleetChannel':
    #    myAWSIoTMQTTClient.publish(fleetTopic, 'Connected to {0}|{1}|{2}'.format(fleetTopic,pubTopic,message.topic), 0)
    elif message_split[0] == 'FleetInfo':
        data_1 = json.loads(message_split[1])
        fleet.update(data_1)

myAWSIoTMQTTClient.subscribe(dev1Topic, 1, onMessageCallback)
myAWSIoTMQTTClient.subscribe(fleetTopic, 1, onFLeetMessageCallback)


# Infinite loop reading console input and publishing what it finds
while True:
    #message = raw_input('Enter a message on the next line to send to ' + pubTopic + ':\r\n')
    message = raw_input('Enter a message on the next line to send topic in format <Message|PublishTopic|ReceiverTopic> '+ ':\r\n')
    input_split = message.split("|")
    topic_name = input_split[1]
    # Calling function to publish to IoT Topic
    publishToIoTTopic(topic_name, message)
