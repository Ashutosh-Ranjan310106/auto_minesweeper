
import tkinter
from pynput.mouse import *
#import mouse
mouse=Controller()
f=[(-1,-1)]
x=0
def point(a,b,c,d):
    global x
    if f[-1]!=(a,b):
        f.append((a,b))
        x+=1    
    if x>=2:
        x=0
        return False
def get_cordinate():
    with Listener(on_scroll = point) as listener:
        listener.join()
    p,q=f[-2]#.split()
    r,s=f[-1]#.split()
    return [p,q,r,s]