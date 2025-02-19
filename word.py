import cv2
import numpy as np
import pyautogui
from PIL import ImageGrab,Image
from time import sleep
#import pyttsx3
import pytesseract
#from pytesseract import image_to_string
from pynput.mouse import Controller,Button
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
tex=''
mouse=Controller()
def getpoint(word,cap,cordinate,nword,nword2):
    text=pytesseract.image_to_boxes(cap)
    text=text.split(' 0\n')
    print(1)

    st=''
    for i in text[:-1:]:
        st+=i[0]
    st=st.lower()
    print(st)
    try:
        ind=-1
        nind=-1
        nind2=-1
        x=0
        while ind<=nind or ind==nind2:
            #print(x)
            ind=st.index(word.lower(),ind+1)
            try:
                nind=st.index(nword.lower())
            except:
                nind=-1
            try:
                nind2=st.index(nword2.lower())
            except:
                nind2=-1
            print(ind,nind)
            
            x += nind+1
        print(ind)
        s=text[ind].split()
        e=text[ind+len(word)-1].split()
        point=(int(s[1])+int(e[3]))/2,(cordinate[3] -int(s[2])+cordinate[3]-int(e[4]))/2
        return point
    
    except Exception as e:
        print(e)
    #return False
def mouseclick(word,cordinate=[40, 41, 1891, 989],t=True,nword='1313241425',nword2='13132414275'):
    cap=ImageGrab.grab(bbox=cordinate)
    cap= np.array(cap)
    cap=cv2.cvtColor(cap, cv2.COLORMAP_HOT)
    try:
        cx,cy=getpoint(word,cap,cordinate,nword,nword2)
        x,y=mouse.position
        mouse.move(cordinate[0]+cx-x,cy-y)
        if t:
            mouse.click(Button.left,1)
            cv2.imshow('',cap)
            sleep(5)
        return True
    
    except Exception as e:
        cv2.imshow('',cap)
        print(2,e)
        #sleep(5)
    
        
        #print('No such word')
    #sleep(1)
    #cv2.destroyAllWindows()
