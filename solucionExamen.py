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


def ventana_principal():
    raiz = Tk()

    menu = Menu(raiz)

    # DATOS
    menudatos = Menu(menu, tearoff=0)
    menudatos.add_command(label="Salir", command=raiz.quit)
    menu.add_cascade(label="Datos", menu=menudatos)

    # LISTAR
    menulistar = Menu(menu, tearoff=0)
    menu.add_cascade(label="Listar", menu=menulistar)

    # BUSCAR
    menubuscar = Menu(menu, tearoff=0)
    menu.add_cascade(label="Buscar", menu=menubuscar)

    raiz.config(menu=menu)

    raiz.mainloop()


if __name__ == "__main__":
    ventana_principal()
