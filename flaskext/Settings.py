from os import getenv
from .variables import env_path
from dotenv import load_dotenv
import inspect

class Settings:

    def __init__(self, env_file = ''):
        if(env_file == ''):        
            load_dotenv(env_path)
        else:
            load_dotenv(env_file)
        props = self.props()
        res = {}
        for item, val in props:
            helper =  getenv(item)
            if(helper is not None):
                res[item] = helper
        self.__dict__.update(res)

    @classmethod
    def props(cls):
        attributes = inspect.getmembers(cls, lambda a:not(inspect.isroutine(a)))
        res = [a for a in attributes if not(a[0].startswith('__') and a[0].endswith('__'))]   
        return res