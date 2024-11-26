from tests.utils import singleton_mock_setup, singleton_mock_teardown

if __name__ == "__main__":
    import unittest
    from unittest.mock import MagicMock

    class F:
        pass

    class SingletonMockTestCase(unittest.TestCase):
        def setUp(self):
            self.mock = MagicMock()
            self.func_mock = MagicMock()
            self.mock.func = self.func_mock

            self.origin = singleton_mock_setup(F, self.mock, globals())

        def tearDown(self):
            singleton_mock_teardown(self.origin, globals())

        def test_case(self):
            F.func()
            self.assertEqual(len(self.func_mock.mock_calls), 1)

    unittest.main()
