
import nose
from eidolon import getSceneMgr, asyncfunc,printFlush,timing

    
class TestModules(object):
    def __init__(self):
        pass
    
    @staticmethod
    def addTestFunc(func,args):
        proxy=lambda _:func(*args)
        proxy.__name__='test_'+func.__name__
        proxy.__doc__=func.__doc__
        
        setattr(TestModules,proxy.__name__,proxy)
        del proxy
    

mgr=getSceneMgr()
for pname in mgr.getPluginNames():
    plugin=mgr.getPlugin(pname)

    for testcase in plugin.getTests():
        TestModules.addTestFunc(testcase[0],testcase[1:])    


@asyncfunc
@timing
def _runtests():
    nose.runmodule()


#_runtests()
nose.runmodule()
