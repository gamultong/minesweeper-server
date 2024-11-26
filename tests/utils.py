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
