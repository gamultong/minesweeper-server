from message_object import *
import unittest
import json

FETCH_TILES_EXAMPLE = \
"""
{
	"event": "fetch-tiles",
	"data": {
		"start_x": 0,
		"start_y": 0,
		"end_x": 0,
		"end_y": 0
	}
}
"""

TILES_EXAMPLE = \
"""
{
	"event": "tiles",
	"data": {
		"start_x": 0,
		"start_y": 0,
		"end_x": 4,
		"end_y": 4,
		"tiles": "CCCCCCCCCCC111CC1F1CC111C"
	}
}
"""

class FetchTilesDataTestCase(unittest.TestCase):
    def test_from_str(self):
        socket_msg = FETCH_TILES_EXAMPLE
        message:Message[FetchTilesData] = Message.from_str(socket_msg)

        assert message.event == "fetch-tiles"
        assert issubclass(type(message.data), MessageData)
        assert message.data.start_x == 0
        assert message.data.start_y == 0
        assert message.data.end_x == 0
        assert message.data.end_y == 0

    def test_from_str_invalid(self):
        socket_msg = FETCH_TILES_EXAMPLE

        data = json.loads(socket_msg)

        for key in data["data"]:
            original = data["data"][key]
            data["data"][key] = "invalid value"
            socket_msg = json.dumps(data)
            data["data"][key] = original

            with self.assertRaises(InvalidDataException) as cm:
                Message.from_str(socket_msg)

            assert cm.exception.msg.find(key) != -1
    
    
class TilesDataTestCase(unittest.TestCase):
    def test_from_str(self):
        socket_msg = TILES_EXAMPLE
        message:Message[TilesData] = Message.from_str(socket_msg)

        assert message.event == "tiles"
        assert issubclass(type(message.data), MessageData)
        assert message.data.start_x == 0
        assert message.data.start_y == 0
        assert message.data.end_x == 4
        assert message.data.end_y == 4
        assert message.data.tiles == "CCCCCCCCCCC111CC1F1CC111C"

    def test_to_str(self):        
        message: Message[TilesData] = Message(
            event = "tiles",
            data = TilesData(
                start_x=0,
                start_y=0,
                end_x=4,
                end_y=4,
                tiles="CCCCCCCCCCC111CC1F1CC111C"
	        ) 
        )

        msg_str = message.to_str()

        assert json.loads(msg_str) == json.loads(TILES_EXAMPLE)
           
    
    

unittest.main()