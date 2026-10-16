from bs4 import BeautifulSoup
import urllib.request
from tkinter import *
from tkinter import messagebox
import sqlite3
import lxml
import re

import datetime

import os
import ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
        getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

def extraer_elementos():
    url = "https://www.universal-comics.com/comics.html"
    content = urllib.request.urlopen(url)
    dom = BeautifulSoup(content, "lxml")
    dom_comics = dom.find_all("div", class_="producto")
    lista_comics = []
    for comic in dom_comics:
        titulo = comic.find("h4", class_="titulo").a.string.strip()
        disponibilidad = comic.find(
            "span", class_="disponibilidad").string.strip()
        p_anterior = comic.find("span", class_="precio-anterior")
        if (p_anterior is None):
            p_original = float(comic.find("span", class_="precio").string.strip().split(" ")[
                0].replace(",", "."))
            p_descuento = p_original
        else:
            p_original = float(p_anterior.string.strip().split(" ")[
                0].replace(",", "."))
            p_descuento = float(comic.find("span", class_="precio").string.strip().split(" ")[
                0].replace(",", "."))
        indiv_url = comic.find("h4", class_="titulo").a['href']
        indiv_content = urllib.request.urlopen(
            "https://www.universal-comics.com"+indiv_url)
        indiv_dom = BeautifulSoup(indiv_content, "lxml")
        encuadernacion = indiv_dom.find("li", class_="encuadernacion").find(
            "span", class_="valor-propiedad").string.strip()
        fecha_edicion = indiv_dom.find("li", class_="fechaedicion").find(
            "span", class_="valor-propiedad").string.strip().split("/")
        fecha_edicion_def = fecha_edicion[2] + \
            "-"+fecha_edicion[1]+"-"+fecha_edicion[0]
        autor = indiv_dom.find("li", class_="autores").find(
            "span", class_="valor-propiedad").string.strip()
        coleccion = indiv_dom.find("li", class_="coleccion").find(
            "span", class_="valor-propiedad").string.strip()
        descuento = int(indiv_dom.find(
            "span", class_="descuento").string.strip()[:-1])
        lista_comics.append((titulo, disponibilidad, p_original, p_descuento,
                            encuadernacion, fecha_edicion_def, autor, coleccion, descuento))
    return lista_comics



#-----------------------------------------------------------------------------------------------------

'''def cargar():
    ultima_carga = "nunca"
    try:
        conn = sqlite3.connect('comics.db')
        cursor = conn.execute("SELECT FECHA_ULTIMA_CARGA FROM INFO_CARGA")
        fila = cursor.fetchone()
        if fila:
            ultima_carga = fila[0]
        conn.close()
    except sqlite3.OperationalError:
        pass

    mensaje = (f"¿Está seguro que quiere recargar los datos?\n Esta operación puede ser lenta.\n Última carga: {ultima_carga}")

    respuesta = messagebox.askyesno(title="Confirmar", message=mensaje)
    if respuesta:
        almacenar_bd()'''

def cargar():
    respuesta = messagebox.askyesno(title="Confirmar",message="Esta seguro que quiere recargar los datos. \nEsta operación puede ser lenta")
    if respuesta:
        almacenar_bd()


def almacenar_bd():
    conn = sqlite3.connect('comics.db')
    conn.text_factory = str
    conn.execute("DROP TABLE IF EXISTS COMIC")
    conn.execute('''CREATE TABLE COMIC
    (TITULO TEXT NOT NULL,
    DISPONIBILIDAD TEXT ,
    PRECIO_ORIGINAL REAL,
    PRECIO_DESCUENTO REAL,
    ENCUADERNACION TEXT,
    FECHA_EDICION DATE,
    AUTORES TEXT,
    COLECCION TEXT,
    DESCUENTO INT);''')

    lista_comics = extraer_elementos()
    
    for comic in lista_comics:
        titulo = comic[0]
        disponibilidad = comic[1]
        precio_original = comic[2]
        precio_descuento = comic[3]
        encuadernacion = comic[4]
        fecha_edicion = comic[5]
        autores = comic[6]
        coleccion = comic[7]
        descuento = comic[8]

        conn.execute("""INSERT INTO COMIC (TITULO, DISPONIBILIDAD, PRECIO_ORIGINAL, PRECIO_DESCUENTO, ENCUADERNACION, FECHA_EDICION, AUTORES, COLECCION, DESCUENTO) VALUES (?,?,?,?,?,?,?,?,?)""", (titulo, disponibilidad, precio_original, precio_descuento, encuadernacion, fecha_edicion, autores, coleccion, descuento))
    conn.commit()
    
    cursor = conn.execute("SELECT COUNT(*) FROM COMIC")
    messagebox.showinfo("Base Datos",
    "Base de datos creada correctamente \nHay " + str(cursor.fetchone()[0]) + " comics")
    conn.close()


#-----------------------------------------------------------------------------------------------------

def ventana_principal():
    raiz = Tk()

    menu = Menu(raiz)

    # DATOS
    menudatos = Menu(menu, tearoff=0)
    menudatos.add_command(label="Salir", command=raiz.quit)
    menudatos.add_command(label="Cargar", command=cargar)
    menu.add_cascade(label="Datos", menu=menudatos)

    # LISTAR
    menulistar = Menu(menu, tearoff=0)
    #menulistar.add_command(label="Todos los comics", command=listar_todos_comics)
    #menulistar.add_command(label="Comics con más descuento", command=listar_5_mas_descuento)
    menu.add_cascade(label="Listar", menu=menulistar)

    # BUSCAR
    menubuscar = Menu(menu, tearoff=0)
    #menubuscar.add_command(label="Comics por autor", command=buscar_por_autor)
    #menubuscar.add_command(label="Comics por fecha", command=buscar_por_fecha)
    #menubuscar.add_command(label="Comics por título o colección", command=buscar_titulo_coleccion)
    menu.add_cascade(label="Buscar", menu=menubuscar)

    raiz.config(menu=menu)

    raiz.mainloop()


if __name__ == "__main__":
    ventana_principal()
