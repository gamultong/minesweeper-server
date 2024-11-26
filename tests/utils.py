def cases(case_list):
    def wrapper(func):
        def func_wrapper(*arg, **kwargs):
            for i in case_list:
                kwargs.update(i)
                func(*arg, **kwargs)
        return func_wrapper
    return wrapper


def singleton_mock_setup(singleton_obj, mock, globals):
    origin_object = singleton_obj
    globals[singleton_obj.__name__] = mock
    return origin_object


def singleton_mock_teardown(origin_object, globals):
    globals[origin_object.__name__] = origin_object


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
