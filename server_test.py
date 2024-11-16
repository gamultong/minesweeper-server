import unittest
import uuid

from unittest.mock import MagicMock
from server import ConnectionManager, Conn

def create_connection_mock():
    con = MagicMock()
    func_accept = MagicMock()
    func_receive_text = MagicMock()
    func_send_text = MagicMock()
    func_close = MagicMock()

    con.accept = func_accept
    con.receive_text = func_receive_text
    con.send_text = func_send_text
    con.close = func_close

    return con

class ConnectionManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.con = create_connection_mock()

    def test_add(self):
        con_obj = ConnectionManager.add(self.con)
        assert type(con_obj) == Conn

        assert ConnectionManager.get_conn(con_obj.id).id == con_obj.id
    
    def test_get_conn(self):
        valid_id = "abc"
        invalid_id = "abcdef"
        ConnectionManager.conns[id] = Conn()

        assert ConnectionManager.get_conn(valid_id) is not None
        assert ConnectionManager.get_conn(invalid_id) is None

    def test_generate_conn_id(self):
        n_conns = 5

        conns = [create_connection_mock() for _ in range(n_conns)]
        conn_ids = [] * n_conns
        
        for idx, conn in enumerate(conns):
            conn_obj = ConnectionManager.add(conn=conn)
            conn_ids[idx] = conn_obj.id
            
        for id in conn_ids:
            assert conn_ids.count(id) == 1
            # UUID 포맷인지 확인. 아니면 ValueError
            uuid.UUID(id)


if __name__ == "__main__":
    unittest.main()