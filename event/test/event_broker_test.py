import unittest
from unittest.mock import MagicMock

from message import Message
from event import EventPublisher, NoMatchingHandlerException

class EventPublisherTestCase(unittest.TestCase):
    def setUp(self):
        self.handler = MagicMock()
        EventPublisher.add_handler("example")(self.handler)

    def tearDown(self):
        EventPublisher.remove_handler("example")
                
    def test_add_handler(self):
        assert "example" in EventPublisher.handler_dict

    def test_remove_handler(self):
        assert "example" in EventPublisher.handler_dict
        EventPublisher.remove_handler("example")
        assert not "example" in EventPublisher.handler_dict
        
    def test_publish(self):
        message = Message(event="example", payload=None)
        
        EventPublisher.publish(message=message)

        assert len(self.handler.mock_calls) == 1
        mock_message = self.handler.mock_calls[0].args[0]               
        assert mock_message.event == message.event
        assert mock_message.payload == message.payload
    
        

    def test_publish_no_handler(self):
        message = Message(event="invaild_event", payload=None)

        with self.assertRaises(NoMatchingHandlerException) as cm:
            EventPublisher.publish(message=message)
        self.assertEqual(cm.exception.msg, "no matching handler for 'invaild_event'")


if __name__ == "__main__":
    unittest.main()