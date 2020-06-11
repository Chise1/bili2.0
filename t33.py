# -*- encoding: utf-8 -*-
"""
@File    : t33.py
@Time    : 2020/6/11 10:24
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :
"""
import inspect
from pydantic import BaseModel
class TestModel(BaseModel):
    x:int=0

def add(x:int,y:int,z:TestModel )->int:
    return x+y
sig =  inspect.signature(add)
print(sig)
y=add.__annotations__
z=y['z'](x=1)
print(z)

print(y)
import fastapi
x=fastapi.FastAPI()
def ca(*args,**kwargs):
    """

    :param args:
    :param kwargs:
    :return:
    """
    pass
@ca
def cb(test):
    print(test)

c=cb("123")