import inspect
from typing import List, Union

from boltons.funcutils import wraps
from fastapi import FastAPI
from injector import Injector
from starlette.requests import Request

from common.interceptor import Interceptor

from datetime import datetime
import calendar


class InspectUtils:
    @staticmethod
    def linenumber_of_member(m):
        try:
            return m[1].__code__.co_firstlineno
        except AttributeError:
            return -1


class ValidationUtils:
    @staticmethod
    def is_phone_number(phone: str):
        return phone.isnumeric() and (len(phone) == 10 or len(phone) == 11)


class InjectorUtils:
    @staticmethod
    def create_method_proxy(injector, fn, pointcut):
        @wraps(fn, injected=['self'])
        def proxy(*_args, **_kwargs):
            nonlocal fn
            if hasattr(fn, '__is_intercepted__'):
                return fn(*_args, **_kwargs)
            # List all interceptor belongs to this function
            interceptors: List[Interceptor] = [interceptor for interceptor in injector.get(List[Interceptor]) if
                                               interceptor.pointcut is pointcut]
            for interceptor in interceptors:
                fn = interceptor.wraps(fn)
            setattr(fn, '__is_intercepted__', True)
            return fn(*_args, **_kwargs)

        return proxy

    # Patch Injector to support Interceptor
    @staticmethod
    def patch_injector():
        def patch(call_with_injection):
            @wraps(call_with_injection)
            def wrapper(*args, **kwargs):
                if isinstance(args[0], Injector) and len(args) >= 3 and args[2] is not None:
                    _self = args[2]
                    injector = args[0]
                    members = inspect.getmembers(_self, lambda member: hasattr(member, '__pointcuts__'))
                    for (pointcut_fn_name, pointcut_fn) in members:
                        for pointcut in pointcut_fn.__pointcuts__:
                            proxy = InjectorUtils.create_method_proxy(injector, pointcut_fn, pointcut)
                            setattr(_self, pointcut_fn_name, proxy)
                return call_with_injection(*args, **kwargs)

            return wrapper

        Injector.call_with_injection = patch(Injector.call_with_injection)

    @classmethod
    def get_injector(cls, fast_api_or_request: Union[FastAPI, Request]):
        if isinstance(fast_api_or_request, Request):
            return InjectorUtils.get_injector(fast_api_or_request.app)
        elif isinstance(fast_api_or_request, FastAPI):
            return fast_api_or_request.__injector__
        raise ValueError('Can get Injector from obj')


def fullname(o):
    # o.__module__ + "." + o.__class__.__qualname__ is an example in
    # this context of H.L. Mencken's "neat, plausible, and wrong."
    # Python makes no guarantees as to whether the __module__ special
    # attribute is defined, so we take a more circumspect approach.
    # Alas, the module name is explicitly excluded from __qualname__
    # in Python 3.

    module = o.__module__
    if module is None or module == str.__module__:
        return o.__qualname__  # Avoid reporting __builtin__
    else:
        return module + '.' + o.__qualname__


def get_current_time():
    # current_date = datetime.now().date()
    # current_date = '2019-01-08'
    current_date = datetime(2019, 9, 23).date()
    current_year = current_date.year
    current_month = current_date.month
    last_day_of_month = int(calendar.monthrange(current_year, current_month)[1])
    current_month_from = datetime(current_year, current_month, 1).date()
    current_month_end = datetime(current_year, current_month, last_day_of_month).date()
    hour_from = ' 00:00:00'
    hour_end = ' 23:59:59'
    set_date_from = str(current_date) + hour_from
    set_date_end = str(current_date) + hour_end
    set_month_from = str(current_month_from) + hour_from
    set_month_end = str(current_month_end) + hour_end
    # timestamp
    time_from = int(datetime.strptime(set_date_from, '%Y-%m-%d %H:%M:%S').strftime('%s'))
    time_end = int(datetime.strptime(set_date_end, '%Y-%m-%d %H:%M:%S').strftime('%s'))
    month_from = int((datetime.strptime(set_month_from, '%Y-%m-%d %H:%M:%S')).strftime('%s'))
    month_end = int((datetime.strptime(set_month_end, '%Y-%m-%d %H:%M:%S')).strftime('%s'))
    created_at = int(datetime.strptime(set_date_end, '%Y-%m-%d %H:%M:%S').strftime('%s'))
    return [current_date, set_date_from, set_date_end, created_at, time_from, time_end, month_from, month_end]
