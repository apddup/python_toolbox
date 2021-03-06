# Copyright 2009-2013 Ram Rachum.
# This program is distributed under the MIT license.

'''Testing module for `python_toolbox.monkeypatching_tools`.'''


import sys
import uuid
import types

import nose

from python_toolbox import cute_inspect
from python_toolbox import cute_testing

from python_toolbox import monkeypatching_tools
from python_toolbox import caching


def test():
    '''Test basic workings of `monkeypatch_method`.'''
    
    class A(object):
        pass

    @monkeypatching_tools.monkeypatch_method(A)
    def meow(a):
        return 1
    
    a = A()
    
    assert a.meow() == meow(a) == 1
    
    @monkeypatching_tools.monkeypatch_method(A, 'roar')
    def woof(a):
        return 2
    
    assert a.roar() == woof(a) == 2
    
    assert not hasattr(a, 'woof')
    
    del meow, woof
    
    
def test_monkeypatch_cached_property():

    class A(object):
        pass

    @monkeypatching_tools.monkeypatch_method(A)
    @caching.CachedProperty
    def meow(a):
        return (type(a), uuid.uuid4().hex)
    
    a0 = A()
    assert a0.meow == a0.meow == a0.meow == a0.meow
    
    a1 = A()
    assert a1.meow == a1.meow == a1.meow == a1.meow
    
    assert a0.meow != a1.meow
    assert a0.meow[0] == a1.meow[0] == A
    
    
    
def test_helpful_message_when_forgetting_parentheses():
    '''Test user gets a helpful exception when when forgetting parentheses.'''

    def confusedly_forget_parentheses():
        @monkeypatching_tools.monkeypatch_method
        def f(): pass
        
    with cute_testing.RaiseAssertor(
        TypeError,
        'It seems that you forgot to add parentheses after '
        '`@monkeypatch_method` when decorating the `f` function.'
    ):
        
        confusedly_forget_parentheses()
        

def test_monkeypatch_staticmethod():

    class A(object):
        @staticmethod
        def my_static_method(x):
            raise 'Flow should never reach here.'
        
    @monkeypatching_tools.monkeypatch_method(A)
    @staticmethod
    def my_static_method(x):
        return 'Success'
    
    assert isinstance(cute_inspect.getattr_static(A, 'my_static_method'),
                      staticmethod)
    assert isinstance(A.my_static_method, types.FunctionType)
    
    assert A.my_static_method(3) == A.my_static_method('Whatever') == \
                                                                      'Success'
    
    a0 = A()
    assert a0.my_static_method(3) == a0.my_static_method('Whatever') == \
                                                                      'Success'
    
    
def test_monkeypatch_classmethod():

    class A(object):
        @classmethod
        def my_class_method(cls):
            raise 'Flow should never reach here.'
        
    @monkeypatching_tools.monkeypatch_method(A)
    @classmethod
    def my_class_method(cls):
        return cls

    assert isinstance(cute_inspect.getattr_static(A, 'my_class_method'),
                      classmethod)
    assert isinstance(A.my_class_method, types.MethodType)
    
    assert A.my_class_method() == A
    
    a0 = A()
    assert a0.my_class_method() == A
        
        
        
def test_monkeypatch_classmethod_subclass():
    '''
    Test `monkeypatch_method` on a subclass of `classmethod`.
    
    This is useful in Django, that uses its own `classmethod` subclass.
    '''

    class FunkyClassMethod(classmethod):
        is_funky = True

    class A(object):
        @FunkyClassMethod
        def my_funky_class_method(cls):
            raise 'Flow should never reach here.'
        
    @monkeypatching_tools.monkeypatch_method(A)
    @FunkyClassMethod
    def my_funky_class_method(cls):
        return cls

    assert isinstance(cute_inspect.getattr_static(A, 'my_funky_class_method'),
                      FunkyClassMethod)
    assert cute_inspect.getattr_static(A, 'my_funky_class_method').is_funky
    assert isinstance(A.my_funky_class_method, types.MethodType)
    
    assert A.my_funky_class_method() == A
    
    a0 = A()
    assert a0.my_funky_class_method() == A
        

def test_directly_on_object():
    
    class A(object):
        def woof(self):
            return 'woof'

    a0 = A()
    a1 = A()

    @monkeypatching_tools.monkeypatch_method(a0)
    def meow(a):
        return 'not meow'
    
    @monkeypatching_tools.monkeypatch_method(a0)
    def woof(a):
        return 'not woof'
    
    assert a0.meow() == 'not meow'
    assert a0.woof() == 'not woof'
    
    assert a1.woof() == 'woof'
    
    with cute_testing.RaiseAssertor(AttributeError):
        A.meow()
    with cute_testing.RaiseAssertor(AttributeError):
        a1.meow()
        
    assert A.woof(a0) == 'woof'
    
