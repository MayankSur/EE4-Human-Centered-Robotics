#!/usr/bin/env python
import rospy
import sys
from std_msgs.msg import String
from geometry_msgs.msg import PoseStamped
import sqlite3
import tf 

speech_pub = rospy.Publisher("speech_out", String, queue_size=10)
waypoint_pub = rospy.Publisher('/waypoint',PoseStamped,queue_size=10)


#The main node of the system, responsible for the connecting all the nodes accordingly to create a control flow through the system.
#The main node will get inputs from Speech and will provide outputs to movements, speech and UI.
#Vision nodes will be contacted directly from the vision nodes

def incoming_command_callback(data):
    global speech_pub
    rospy.sleep(2)
    if data.data == 'book': 
        speech_pub.publish("Hello There! I think you want a book")
    if data.data == 'hello':
        speech_pub.publish("Hello There! I hope you're well")
    if data.data == 'bottle':
        speech_pub.publish("Hello There! I think you would like some water")
    if data.data == 'bear' or data.data == 'teddy':
        speech_pub.publish("Hello There! I think you would like the teddy bear")

    location = db_function(data.data)
    publish_waypoint(location)
    # height = location[3] - Future extension 

def main():
    rospy.init_node('CentralNode', anonymous=True)
    #Speech Input
    rospy.Subscriber("nlp_out", String, incoming_command_callback)
    # Create a publisher to be able to send to other nodes
    

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

def db_function(command):
    conn = sqlite3.connect('/home/prl1/Documents/EE4-Human-Centered-Robotics/src/main/src/world.db')
    # Aim of the function is to fetch the correct information 
    c = conn.cursor()

    t = (command,)
    #use a query like this to extract the target coordinates for an item
    c.execute('SELECT pos_x,pos_y,pos_theta,height FROM items NATURAL JOIN locations WHERE item_id=?', t)
    test2 = c.fetchone()
    item_location = test2 # Get the item information
    print('Item Location: ')
    print (item_location)
    return item_location # return tuple of values


def publish_waypoint(location_tuple):
        # stuff here
    global waypoint_pub
    pose = PoseStamped()
    pose.header.seq = 1
    pose.header.stamp = rospy.Time.now()
    pose.header.frame_id = "odom"
    pose.pose.position.x = location_tuple[0] # x position
    pose.pose.position.y = location_tuple[1] # y position
    pose.pose.position.z = 0

    quaternion = tf.transformations.quaternion_from_euler(0, 0, location_tuple[2]) # angle
    pose.pose.orientation.x = quaternion[0]
    pose.pose.orientation.y = quaternion[1]
    pose.pose.orientation.z = quaternion[2]
    pose.pose.orientation.w = quaternion[3]

    rospy.loginfo(pose)
    #rospy.Rate(5).sleep()
    waypoint_pub.publish(pose)

if __name__ == '__main__':
    print(('Starting the Main Node'))
    rospy.loginfo('Starting the Main Node')
    rospy.sleep(2)
    main()