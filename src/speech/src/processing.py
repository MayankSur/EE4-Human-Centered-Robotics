#!/usr/bin/env python
import rospy
import sys
import spacy
from spacy.matcher import PhraseMatcher
from std_msgs.msg import String

def incoming_speech_callback(data):
    rospy.loginfo(rospy.get_caller_id() + "I heard %s", data.data)
    ## Collect the incoming data
    incoming_sentence = nlp(data.data.decode('utf-8'))

    matches = matcher(incoming_sentence)

    for match_id, start, end in matches:
        span = incoming_sentence[start:end]
        # Span wil contain words that it matches with
        # Converts it to the lower case
        # We can publish this response to the next nodes
        span_str = str(span).lower()

        speech_pub.publish(span_str)
    rospy.sleep(1)

def main():

    rospy.init_node('NLP', anonymous=True)
    #Speech Input
    
    print('Starting the Subscriber')
    rospy.Subscriber("nlp_in", String, incoming_speech_callback)
    
    #Speech Output
    speech_pub = rospy.Publisher("nlp_out", String, queue_size=10)


    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

if __name__ == '__main__':
    # Initilising the spacy library 
    nlp = spacy.load("en_core_web_sm")
    matcher = PhraseMatcher(nlp.vocab, attr='LOWER')
    terms = ["Water".decode('utf-8'), "Book".decode('utf-8') , "Hello".decode('utf-8')]
    patterns = [nlp.make_doc(text) for text in terms]
    matcher.add("TerminologyList".decode('utf-8'), None, *patterns)
    main()