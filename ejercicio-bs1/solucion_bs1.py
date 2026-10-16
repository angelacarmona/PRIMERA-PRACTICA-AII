#encoding:utf-8
from bs4 import BeautifulSoup
import urllib.request
from tkinter import *
from tkinter import messagebox
import sqlite3
import lxml
from datetime import datetime
# lineas para evitar error SSL
import os, ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
    getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

def cargar():
    respuesta = messagebox.askyesno(title="Confirmar",message="Esta seguro que quiere recargar los datos. \nEsta operación puede ser lenta")
    if respuesta:
        almacenar_bd()


def extraer_elementos():
    elementos = []

    for i in range(0,3):
        url = "https://www.vinissimus.com/es/vinos/tinto/index.html?cursor=" + str(i*36)
        page = urllib.request.urlopen(url)
        soup = BeautifulSoup(page, 'lxml')
        lista_vinos = soup.find_all("div", class_=["product-list-item"])
        elementos.extend(lista_vinos)

    return elementos


def almacenar_bd():
    conn = sqlite3.connect('vinos.db')
    conn.text_factory = str
    conn.execute("DROP TABLE IF EXISTS VINO")
    conn.execute('''CREATE TABLE VINO
    (NOMBRE TEXT NOT NULL,
    PRECIO REAL,
    DENOMINACION TEXT,
    BODEGA TEXT,
    TIPO_UVAS TEXT);''')

    lista_vinos = extraer_elementos()

    for vino in lista_vinos:
        datos = vino.find("div",class_=["details"]) #dentro de cada vino
        #dentro de datos tenemos el nombre, bodega, denominacion y uvas:
        nombre = datos.a.h2.string.strip() #no es un div, es una etiqueta "a" con otra etiqueta "h2" dentro
        bodega = datos.find("div", class_=["cellar-name"]).string.strip()
        denominacion = datos.find("div",class_=["region"]).string.strip()
        uvas = "".join(datos.find("div",class_=["tags"]).stripped_strings) #es un div con varias etiquetas "span" dentro, que contienen el texto de las uvas (si hay varias, se separan por "/")
        precio = list(vino.find("p",class_=["price"]).stripped_strings)[0] #lista porque es precio + $, y luego nos quedamos con el primer elemento de la lista, que es el precio
        #si tiene descuento el prcio es el del descuento
        dto = vino.find("p",class_=["price"]).find_next_sibling("p",class_="dto") # el dto viene en un <p> seguido del <p> del precio, y con la clase "dto"
        if dto:
            precio = list(dto.stripped_strings)[0]

        conn.execute("""INSERT INTO VINO (NOMBRE, PRECIO, DENOMINACION, BODEGA, TIPO_UVAS) VALUES (?,?,?,?,?)""", (nombre, float(precio.replace(',','.')), denominacion, bodega, uvas))
    conn.commit()
   
    cursor = conn.execute("SELECT COUNT(*) FROM VINO")
    messagebox.showinfo("Base Datos",
    "Base de datos creada correctamente \nHay " + str(cursor.fetchone()[0]) + " vinos")
    conn.close()


def listar_vinos():
    conn = sqlite3.connect('vinos.db')
    conn.text_factory = str
    cursor = conn.execute("SELECT NOMBRE, PRECIO, BODEGA, DENOMINACION FROM VINO")
    lista_de_vinos(cursor)
    conn.close()


def buscar_por_denominacion():
    def listar(event):
        conn = sqlite3.connect('vinos.db')
        conn.text_factory = str
        cursor = conn.execute("SELECT NOMBRE, PRECIO, BODEGA, DENOMINACION FROM VINO WHERE DENOMINACION LIKE '%" + str(entry.get()) + "%'")
        lista_de_vinos(cursor)
        conn.close()

    conn = sqlite3.connect('vinos.db')
    conn.text_factory = str
    cursor = conn.execute("SELECT DISTINCT DENOMINACION FROM VINO")
    denominaciones = [row[0] for row in cursor]

    v = Toplevel() #crea una ventana secundaria
    label = Label(v, text="Seleccione una denominación:")
    label.pack(side=LEFT)
    entry = Spinbox(v, width=50, values=denominaciones)
    entry.bind("<Return>", listar) 
    entry.pack(side=LEFT)

    conn.close()


def buscar_por_precio():
    def listar(evento):
        conn = sqlite3.connect('vinos.db')
        conn.text_factory = str
        cursor = conn.execute("SELECT NOMBRE, PRECIO, BODEGA, DENOMINACION FROM VINO WHERE PRECIO <= ? ORDER BY PRECIO", (str(entry.get()),))
        lista_de_vinos(cursor)
        conn.close()

    v = Toplevel() #crea una ventana secundaria
    label = Label(v, text="Ingrese un precio máximo:")
    label.pack(side=LEFT)
    entry = Entry(v)
    entry.bind("<Return>", listar)
    entry.pack(side=LEFT)

def buscar_por_uvas():
    def listar(event):
        conn = sqlite3.connect('vinos.db')
        conn.text_factory = str
        cursor = conn.execute("SELECT NOMBRE, TIPO_UVAS FROM VINO WHERE TIPO_UVAS LIKE '%" + str(entry.get()) + "%'")
        listar_por_uvas(cursor)
        conn.close()

    conn = sqlite3.connect('vinos.db')
    conn.text_factory = str
    cursor = conn.execute("SELECT DISTINCT TIPO_UVAS FROM VINO")
    uvas = set()
    for row in cursor:
        cadena_uvas = row[0]
        for uva in cadena_uvas.split("/"):
            uva_limpia = uva.strip()
            if uva_limpia:
                uvas.add(uva_limpia)
    conn.close()

    tipos_de_uvas = sorted(list(uvas))  

    v = Toplevel() #crea una ventana secundaria
    label = Label(v, text="Seleccione un tipo de uva:")
    label.pack(side=LEFT)
    entry = Spinbox(v, width=50, values=tipos_de_uvas)
    entry.bind("<Return>", listar)
    entry.pack(side=LEFT)


#--------------------------------------------------------------------------------------------------------------------------------------------------------------
def ventana_principal():
    raiz = Tk() #crea la ventana principal
    menu = Menu(raiz) #crea la barra del menú vacía  y la asocia a la ventana principal

    #DATOS--------------------------------------------------------------------------------------------
    menudatos = Menu(menu, tearoff=0) #crea un submenu desplegable y lo asocia al menú principal
    menudatos.add_command(label="Cargar", command=cargar)
    menudatos.add_command(label="Listar", command=listar_vinos)
    menudatos.add_command(label="Salir", command=raiz.quit)
    menu.add_cascade(label="Datos", menu=menudatos) #añade el botón "datos" al menú principal y lo asocia al submenu desplegable
    #BUSCAR--------------------------------------------------------------------------------------------
    menubuscar = Menu(menu, tearoff=0)
    menubuscar.add_command(label="Denominación", command=buscar_por_denominacion)
    menubuscar.add_command(label="Precio", command=buscar_por_precio)
    menubuscar.add_command(label="Uvas", command=buscar_por_uvas)
    menu.add_cascade(label="Buscar", menu=menubuscar)

    #--------------------------------------------------------------------------------------------------
    raiz.config(menu=menu) #asocia el menú principal a la ventana principal
    raiz.mainloop() #inicial el bucle de la interfaz gráfica, que espera a que el usuario haga algo (clic, escribir, etc) y llama a la función correspondiente


def lista_de_vinos(cursor):
    v = Toplevel() #crea una ventana secundaria
    scrollbar = Scrollbar(v) #crea una barra de desplazamiento
    scrollbar.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, width=150, yscrollcommand=scrollbar.set) #crea una lista y la asocia a la barra de desplazamiento
    for row in cursor:
        s = 'VINO: ' + row[0]
        lb.insert(END, s)
        lb.insert(END, "------------------------------------------------------------------------")
        s = " PRECIO: " + str(row[1]) + ' | BODEGA: ' + row[2]+ ' | DENOMINACION: ' + row[3]
        lb.insert(END, s)
        lb.insert(END,"\n\n")
    lb.pack(side=LEFT, fill=BOTH)
    scrollbar.config(command=lb.yview)


def listar_por_uvas(cursor):
    v = Toplevel() #crea una ventana secundaria
    scrollbar = Scrollbar(v) #crea una barra de desplazamiento
    scrollbar.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, width=150, yscrollcommand=scrollbar.set) #crea una lista y la asocia a la barra de desplazamiento
    for row in cursor:
        s = 'VINO: ' + row[0]
        lb.insert(END, s)
        lb.insert(END, "------------------------------------------------------------------------")
        s = " TIPO DE UVAS: " + str(row[1])
        lb.insert(END, s)
        lb.insert(END,"\n\n")
    lb.pack(side=LEFT, fill=BOTH)
    scrollbar.config(command=lb.yview)


if __name__ == "__main__":
    ventana_principal()