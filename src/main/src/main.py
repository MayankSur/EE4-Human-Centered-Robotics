#!/usr/bin/env python
import rospy
import rospkg
import sys
from std_msgs.msg import String
from std_msgs.msg import Int8
from geometry_msgs.msg import PoseStamped
import sqlite3
import tf
from random import randrange

speech_pub = rospy.Publisher("speech_out", String, queue_size=10)
face_pub = rospy.Publisher("file_out", String, queue_size=10)
# emotions = rospy.Publisher("facial_expression_command", String, queue_size=10)
waypoint_pub = rospy.Publisher('/waypoint',PoseStamped,queue_size=10)
# arm_commander_pub = rospy.Publisher('/arm_commander',String,queue_size=10)
#pose_estimate_request_pub = rospy.Publisher('/pose_estimate_request',String,queue_size=10)

# Feeling we're going to need flags to make sure there's traciblity of where the robot is
onRoute = False
locations = []

# awake flag
awake = False
# Number of matching nouns said in current input
nouns = 0
most_recent_pose = ""

rospack = rospkg.RosPack()
main_path = rospack.get_path('main')

#The main node of the system, responsible for the connecting all the nodes accordingly to create a control flow through the system.
#The main node will get inputs from Speech and will provide outputs to movements, speech and UI.
#Vision nodes will be contacted directly from the vision nodes
base_movement = None

def update_pose_estimate_callback(pose_estimate):
    global most_recent_pose
    most_recent_pose = pose_estimate.data

def noun_callback(data):
    global nouns
    nouns = data.data

def incoming_command_callback(data):
    global speech_pub
    global locations
    global awake
    global nouns
    base_movement = base_movement_manager()
    global most_recent_pose
    global pose

    words = data.data.split(" ")

    print(words)

# WHY IS THE SLEEP DELETED????
# Check if awake
    # if "anna" in words or "ayana" in words:
    #     awake = True
    #     emotions.publish("waking")
    #     emotions.publish("idle")
    # else:
    #     emotions.publish("sleeping")
    #     # return

    # if awake == True:

    # if nouns > 1:
    #     select = randrange(3)
    #     if select == 0:
    #         speech_pub.publish("Okay, I'll get all those things")
    #         # face_pub.publish("many1.mp4")
    #         emotions.publish("approval")
    #     elif select == 1:
    #         speech_pub.publish("That's a lot of stuff you want")
    #         # face_pub.publish("many2.mp4")
    #         emotions.publish("idle")
    #     elif select == 2:
    #         speech_pub.publish("I'll be one minute")
    #         # face_pub.publish("many3.mp4")
    #         emotions.publish("approval")

    if "name" in words and "what" in words:
        speech_pub.publish("My name is Anna")
        face_pub.publish("sorry1.mp4")
        # emotions.publish("approval")

    elif "be" in words and "quiet" in words:
        speech_pub.publish("Okay, I'll leave you for a bit")
        face_pub.publish("sorry1.mp4")
        # emotions.publish("sleeping")
        awake = False

    # elif 'that' in words and 'there' in words:
    #     location = base_movement.get_location(most_recent_pose)
    #     # base_movement.publish_waypoint(location)
    # elif 'help' in words or 'nurse' in words:
    #     speech_pub.publish("Calling the nurse, please wait")
    #     # face_pub.publish("help.mp4")
    #     emotions.publish("happiness")
    # elif 'book' in words:
    #     speech_pub.publish("Sure, I'll get you a book")
    #     # face_pub.publish("book.mp4")
    #     #item_loc = base_movement.get_item_location('book')
    #     emotions.publish("happiness")
    #
    elif "thank" in words:
        speech_pub.publish("You're welcome!")

    elif 'remote' in words or 'TV' in words:
        speech_pub.publish("Okay, I'll grab the remote")
        print('Grabbing Remote')
        #key = 'bottle'
        face_pub.publish("water.mp4")
        # emotions.publish("happiness")
        base_movement.publish_waypoint_from_item('remote')
    elif 'bear' in words or 'teddy' in words:
        speech_pub.publish("One teddy bear coming right up")
        print('Grabbing Teddy')
        face_pub.publish("bear.mp4")
        # emotions.publish("happiness")
        base_movement.publish_waypoint_from_item('teddy')
    elif 'hello' in words or 'hey' in words:
        speech_pub.publish("Hello There! I hope you're well")
        print('Hello There')
        face_pub.publish("hello.mp4")
        # emotions.publish("approval")

    else:
        select = randrange(3)
        if select == 0:
            speech_pub.publish("Sorry, I didn't understand that")
        elif select == 1:
            speech_pub.publish("What was that?")
        elif select == 2:
            speech_pub.publish("I couldn't quite catch that")
        # emotions.publish("confusion")


    rospy.sleep(0.5)


class base_movement_manager():
    def __init__(self):
        self.conn = sqlite3.connect(main_path + '/src/world.db')
        self.c = self.conn.cursor()

    def get_item_location(self,cmd):
        t = (cmd,)
        print "i am going to get item " + cmd
        self.c.execute('SELECT location_id FROM items NATURAL JOIN locations WHERE item_id=?', t)
        print "this is at location " + self.c.fetchone()[0]
        self.c.execute('SELECT pos_x,pos_y,z_ori,w_ori FROM items NATURAL JOIN locations WHERE item_id=?', t)
        item_location = self.c.fetchone() # Get the item information
        return item_location # return tuple of values

    def get_waypoint_location(self,cmd):
        t = (cmd,)
        print "I am going to move to location" + cmd
        self.c.execute('SELECT pos_x,pos_y,z_ori, w_ori FROM locations WHERE location_id=?', t)
        item_location = self.c.fetchone() # Get the item information
        return item_location # return tuple of values

    def publish_waypoint(self,location_tuple):
            # stuff here
        global waypoint_pub
        global arm_commander_pub
        pose = PoseStamped()
        pose.header.seq = 1
        pose.header.stamp = rospy.Time.now()
        pose.header.frame_id = "map"
        pose.pose.position.x = location_tuple[0] # x position
        pose.pose.position.y = location_tuple[1] # y position
        pose.pose.position.z = 0

        pose.pose.orientation.x = 0
        pose.pose.orientation.y = 0
        pose.pose.orientation.z = location_tuple[2]
        pose.pose.orientation.w = location_tuple[3]

        rospy.loginfo(pose)
        #rospy.Rate(5).sleep()
        waypoint_pub.publish(pose)

    def publish_waypoint_from_item(self,key):
        loc = self.get_item_location(key)
        print('Grabbing item: ', key)
        print('Location: ', loc)
        self.publish_waypoint(loc)

        raw_input('GOING TO THE ' + key)

        loc = self.get_waypoint_location('HOME')
        self.publish_waypoint(loc)

        raw_input('GOING TO THE HOME')


def main():
    rospy.init_node('CentralNode')
    #Speech Input
    rospy.Subscriber("noun_number", Int8, noun_callback)
    rospy.Subscriber("nlp_out", String, incoming_command_callback)
    rospy.Subscriber("pose_estimation",String, update_pose_estimate_callback)
    # Create a publisher to be able to send to other nodes

    #wp = base_movement.get_waypoint_location('A') #example get a waypoint
    #base_movement.publish_waypoint(wp)
    #item_loc = test.get_item_location('teddy') #example get an item location
    #test.publish_waypoint(item_loc)
    print('HERE WE GO!')
    # # spin() simply keeps python from exiting until this node is stopped
    # cmd = ''

    # # Start a loop that will run until the user enters 'quit'.
    # while cmd != 'quit':
    #     # Ask the user for a name.
    #     cmd = raw_input("Action: ")
    #     arm_commander_pub.publish(cmd)

    # print('Jokes m9')
    rospy.spin()


if __name__ == '__main__':
    base_movement = base_movement_manager()
    rospy.loginfo('Starting the Main Node')
    rospy.sleep(1)
    main()
