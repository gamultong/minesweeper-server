import unittest
import uuid

from unittest.mock import MagicMock
from conn import Conn
from conn.manager import ConnectionManager
from message import Message
from message.payload import TilesPayload
from event import EventBroker
from conn.test.fixtures import create_connection_mock

class ConnectionManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.con = create_connection_mock()

    def tearDown(self):
        ConnectionManager.conns = {}

    def test_add(self):
        con_obj = ConnectionManager.add(self.con)
        assert type(con_obj) == Conn

        assert ConnectionManager.get_conn(con_obj.id).id == con_obj.id
    
    def test_get_conn(self):
        valid_id = "abc"
        invalid_id = "abcdef"
        ConnectionManager.conns[valid_id] = Conn(valid_id, create_connection_mock())

        assert ConnectionManager.get_conn(valid_id) is not None
        assert ConnectionManager.get_conn(invalid_id) is None

    def test_generate_conn_id(self):
        n_conns = 5

        conns = [create_connection_mock() for _ in range(n_conns)]
        conn_ids = [None] * n_conns
        
        for idx, conn in enumerate(conns):
            conn_obj = ConnectionManager.add(conn=conn)
            conn_ids[idx] = conn_obj.id
            
        for id in conn_ids:
            assert conn_ids.count(id) == 1
            # UUID 포맷인지 확인. 아니면 ValueError
            uuid.UUID(id)

    def test_receive_tiles_event(self):
        _ = ConnectionManager.add(self.con)
        
        message = Message(event="tiles", payload=TilesPayload(
            0,0,0,0,"abcdefg"
        ))
        
        EventBroker.publish(message)

        self.assertEqual(len(self.con.send_text.mock_calls), 1)
        
        mock_call = self.con.send_text.mock_calls[0]
        self.assertEqual(mock_call.args[0], message.to_str())

    def test_handle_message(self):
        mock = MagicMock()
        EventBroker.add_receiver("example")(mock)
        
        message = Message(event="example", payload=TilesPayload(
            0,0,0,0,"abcdefg"
        ))
          
        ConnectionManager.handle_message(message=message)

        self.assertEqual(len(mock.mock_calls), 1)
        self.assertEqual(mock.mock_calls[0].args[0].to_str(), message.to_str())

if __name__ == "__main__":
    unittest.main()