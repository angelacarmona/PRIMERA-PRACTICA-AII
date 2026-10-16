from bs4 import BeautifulSoup  
import urllib.request 
from tkinter import * 
from tkinter import messagebox 
import sqlite3 
import lxml 
import re

import datetime

import os, ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context
    
def ventana_principal():
    raiz = Tk()

    menu = Menu(raiz)

    #DATOS
    menudatos = Menu(menu, tearoff=0)
    menudatos.add_command(label="Salir", command=raiz.quit)
    menu.add_cascade(label="Datos", menu=menudatos)
    
    #LISTAR
    menulistar = Menu(menu, tearoff=0)
    menu.add_cascade(label="Listar", menu=menulistar)

    #BUSCAR
    menubuscar = Menu(menu, tearoff=0)
    menu.add_cascade(label="Buscar", menu=menubuscar)

    raiz.config(menu=menu)

    raiz.mainloop()



if __name__ == "__main__":
    ventana_principal()


