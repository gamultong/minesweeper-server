from .testdata.base_payload_testdata import \
    ExamplePayload, ExampleWrapperPayload, EXCEPTION_TEST_CASES, EXAMPLE_PAYLOAD_DICT, EXAMPLE_PAYLOAD_WRAPPED_DICT
from message.payload import InvalidFieldException, MissingFieldException
from tests.utils import cases

import unittest


class BasePayloadTestCase(unittest.TestCase):
    def test_from_dict(self):
        payload = ExamplePayload._from_dict(dict=EXAMPLE_PAYLOAD_DICT)

        assert payload.foo == "foo"
        assert payload.bar == "bar"

    def test_from_dict_wrapped(self):
        payload = ExampleWrapperPayload._from_dict(dict=EXAMPLE_PAYLOAD_WRAPPED_DICT)

        assert payload.a == 1
        assert payload.b == "b"

        assert payload.wrapped.foo == "foo"
        assert payload.wrapped.bar == "bar"

    @cases(EXCEPTION_TEST_CASES)
    def test_from_dict_wrongs(self, dict, payload, exp, msg):
        with self.assertRaises(exp) as cm:
            payload._from_dict(dict=dict)

        assert cm.exception.msg == msg


if __name__ == "__main__":
    unittest.main()
