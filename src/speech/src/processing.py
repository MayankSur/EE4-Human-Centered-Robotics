#!/usr/bin/env python
import rospy
import sys
import spacy
from spacy.matcher import PhraseMatcher
from std_msgs.msg import String
from std_msgs.msg import Bool
from std_msgs.msg import Int8


class speech_processor:

    def __init__(self):
        # Initilising the spacy library
        self.nlp = spacy.load("en_core_web_sm", disable=["ner"])
        self.matcher = PhraseMatcher(self.nlp.vocab, attr='LOWER')
        self.terms = ["Bottle".decode('utf-8'),
                 "Book".decode('utf-8') ,
                 "Hello".decode('utf-8'),
                 "Bear".decode('utf-8'),
                 "Teddy".decode('utf-8'),
                 "Thirsty".decode('utf-8'),
                 "Help".decode('utf-8'),
                 "Water".decode('utf-8'),
                 "What".decode('utf-8'),
                 "Name".decode('utf-8'),
                 "Nurse".decode('utf-8'),
                 "Remote".decode('utf-8'),
                 "TV".decode('utf-8'),
                 "Thank".decode('utf-8'),
                 "Anna".decode('utf-8'),
                 "Be".decode('utf-8'),
                 "Hey".decode('utf-8'),
                 "Quiet".decode('utf-8')]
        self.patterns = [self.nlp.make_doc(text) for text in self.terms]
        self.matcher.add("TerminologyList".decode('utf-8'), None, *self.patterns)
        rospy.sleep(0.5)
        #ROS node
        rospy.init_node('NLP')
        #NPL Input
        print('Starting the Subscriber')
        rospy.Subscriber("nlp_in", String, self.incoming_speech_callback)
        #NLP Output
        self.speech_pub = rospy.Publisher("nlp_out", String, queue_size=10)
        self.noun_pub = rospy.Publisher("noun_number", Int8, queue_size=10)

    def incoming_speech_callback(self, data):
        ## Collect the incoming data
        incoming_sentence = self.nlp(data.data.decode('utf-8'))
        print('Recieved: ', data.data.decode('utf-8'))

        matches = self.matcher(incoming_sentence)
        span_str = []
        nouns = 0

        for match_id, start, end in matches:
            span = incoming_sentence[start:end]
            if incoming_sentence[start].pos_ == 'NOUN':
                nouns += 1
            # Span wil contain words that it matches with
            # Converts it to the lower case
            # We can publish this response to the next nodes
            span_str.append(str(span).lower())

        # self.noun_pub.publish(nouns)
        # rospy.sleep(0.1)

        if len(span_str) == 0:
            self.speech_pub.publish("sorry")
        else:
            keywords = ""
            for word in span_str:
                keywords += word + " "
            self.speech_pub.publish(keywords)

# end of processor class


def main():
    # declare the processor object to initialise the NLP
    sp = speech_processor()
    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

if __name__ == '__main__':
    # error catching
    try:
        main()
    except rospy.ROSInterruptException:
        pass
    except KeyboardInterrupt:
        sys.exit(0)
