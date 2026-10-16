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

def cargar():
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
        almacenar_bd()


def almacenar_bd():
    conn = sqlite3.connect('comics.db')
    conn.text_factory = str
    conn.execute("DROP TABLE IF EXISTS COMIC")
    conn.execute("DROP TABLE IF EXISTS INFO_CARGA")
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
    conn.execute('''CREATE TABLE INFO_CARGA
    (FECHA_ULTIMA_CARGA DATE);''')

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

    ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("INSERT INTO INFO_CARGA (FECHA_ULTIMA_CARGA) VALUES (?)", (ahora,))
    
    conn.commit()
    
    cursor = conn.execute("SELECT COUNT(*) FROM COMIC")
    messagebox.showinfo("Base Datos",
    "Base de datos creada correctamente \nHay " + str(cursor.fetchone()[0]) + " comics")
    conn.close()


#-----------------------------------------------------------------------------------------------------
def listar_comics_especificos(cursor):
    v = Toplevel()
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, width=150, yscrollcommand=sc.set)
    for row in cursor:
        s = 'TITULO: ' + str(row[0])
        lb.insert(END, s)
        lb.insert(END, "-----------------------------------------------------")    
        # Convertimos row[2] y row[3] a str() porque en la BD son REAL (float)
        s = "     DISPONIBILIDAD: " + str(row[1]) + "   |   PRECIO ORIGINAL: " + str(row[2]) + "    |    PRECIO DESCUENTO: " + str(row[3]) 
        lb.insert(END, s)
        s = "     ENCUADERNACIÓN: " + str(row[4]) + "   |   FECHA DE EDICIÓN: " + str(row[5]) + "    |    AUTOR: " + str(row[6]) + "    |    COLECCIÓN: " + str(row[7]) 
        lb.insert(END, s)
        lb.insert(END, "\n\n")
    lb.pack(side=LEFT, fill=BOTH)
    sc.config(command=lb.yview)
    
def listar_todos_comics():
    conn = sqlite3.connect('comics.db')
    conn.text_factory = str
    cursor = conn.execute("SELECT * FROM COMIC")
    listar_comics_especificos(cursor)
    conn.close()

def listar_5_mas_descuento():
    conn = sqlite3.connect('comics.db')
    conn.text_factory = str
    cursor = conn.execute("SELECT * FROM COMIC ORDER BY DESCUENTO DESC LIMIT 5")
    listar_comics_especificos(cursor)
    conn.close()
#-----------------------------------------------------------------------------------------------------

def buscar_por_autor():
    def listar(event):
        conn = sqlite3.connect('comics.db')
        conn.text_factory = str
        cursor = conn.execute("SELECT TITULO, DISPONIBILIDAD, PRECIO_ORIGINAL, PRECIO_DESCUENTO, ENCUADERNACION, FECHA_EDICION, AUTORES, COLECCION FROM COMIC WHERE AUTORES LIKE '%" + str(entry.get()) + "%'")
        listar_comics_especificos(cursor)
        conn.close()

    conn = sqlite3.connect('comics.db')
    conn.text_factory = str
    cursor = conn.execute("SELECT DISTINCT AUTORES FROM COMIC")
    autores = set()
    for row in cursor:
        cadena_autores = row[0]
        for autor in cadena_autores.split("-"):
            autor_limpio = autor.strip()
            if autor_limpio:
                autores.add(autor_limpio)
    conn.close()

    autores = sorted(list(autores))  

    v = Toplevel() #crea una ventana secundaria
    label = Label(v, text="Seleccione un autor:")
    label.pack(side=LEFT)
    entry = Spinbox(v, width=50, values=autores)
    entry.bind("<Return>", listar)
    entry.pack(side=LEFT)

def buscar_por_fecha():
    def listar(event):
        conn = sqlite3.connect('comics.db')
        conn.text_factory = str
        fec = re.match(r"\d\d/\d\d/\d{4}",entry.get().strip())
        if fec:
            fecha = datetime.datetime.strptime(entry.get().strip(),"%d/%m/%Y")
            cursor = conn.execute("SELECT TITULO, DISPONIBILIDAD, PRECIO_ORIGINAL, PRECIO_DESCUENTO, ENCUADERNACION, FECHA_EDICION, AUTORES, COLECCION FROM COMIC WHERE FECHA_EDICION < ?", (fecha,))
            listar_comics_especificos(cursor)
            conn.close()
        else:
            messagebox.showerror("Error", "Formato de fecha incorrecto")

    v = Toplevel()
    label = Label(v,text="Escriba la fecha (dd/mm/aaaa): ")
    label.pack(side=LEFT)
    entry = Entry(v)
    entry.bind("<Return>", listar)
    entry.pack(side=LEFT)

def buscar_titulo_coleccion():
    def listar():
        palabra = en.get().strip()
        
        # Comprobamos que haya escrito una sola palabra (sin espacios y que no esté vacio)
        if not palabra or " " in palabra:
            messagebox.showerror("Error", "Debe introducir una única palabra y sin espacios")
            return
            
        conn = sqlite3.connect('comics.db')
        conn.text_factory = str
        
        # Elegimos la consulta según los checkbuttons seleccionados
        if var_titulo.get() == 1 and var_coleccion.get() == 1:
            cursor = conn.execute("SELECT * FROM COMIC WHERE TITULO LIKE '%" + palabra + "%' OR COLECCION LIKE '%" + palabra + "%'")
        elif var_titulo.get() == 1:
            cursor = conn.execute("SELECT * FROM COMIC WHERE TITULO LIKE '%" + palabra + "%'")
        elif var_coleccion.get() == 1:
            cursor = conn.execute("SELECT * FROM COMIC WHERE COLECCION LIKE '%" + palabra + "%'")
        else:
            messagebox.showerror("Error", "Seleccione al menos una opción (Título y/o Colección)")
            conn.close()
            return
            
        listar_comics_especificos(cursor)
        conn.close()

    v = Toplevel()
    var_titulo = IntVar()
    var_coleccion = IntVar()
    
    cb1 = Checkbutton(v, text="Título", variable=var_titulo)
    cb2 = Checkbutton(v, text="Colección", variable=var_coleccion)
    en = Entry(v)
    b = Button(v, text="Buscar", command=listar)
    
    cb1.pack(side=LEFT)
    cb2.pack(side=LEFT)
    en.pack(side=LEFT)
    b.pack(side=LEFT)
    


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
    menulistar.add_command(label="Todos los comics", command=listar_todos_comics)
    menulistar.add_command(label="Comics con más descuento", command=listar_5_mas_descuento)
    menu.add_cascade(label="Listar", menu=menulistar)

    # BUSCAR
    menubuscar = Menu(menu, tearoff=0)
    menubuscar.add_command(label="Comics por autor", command=buscar_por_autor)
    menubuscar.add_command(label="Comics por fecha", command=buscar_por_fecha)
    menubuscar.add_command(label="Comics por título o colección", command=buscar_titulo_coleccion)
    menu.add_cascade(label="Buscar", menu=menubuscar)

    raiz.config(menu=menu)

    raiz.mainloop()

if __name__ == "__main__":
    ventana_principal()
