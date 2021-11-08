import sys, subprocess, pkg_resources
from PyPDF2 import PdfFileReader, PdfFileWriter
import logging
import os, sys
import requests
from lxml import html
from bs4 import BeautifulSoup
from PIL.ExifTags import TAGS, GPSTAGS
from PIL import Image
from decimal import Context
import smtplib, ssl
import getpass
import pathlib
import socket
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64
import subprocess
import sys
from pathlib import Path

#Formato de loggins
log_format = (
    '[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s')

logging.basicConfig(
    level=logging.DEBUG,
    format=log_format,
    filename=('app.log'))


#Uso de pireq

def pireq():
    logging.info("Se busca si esta instalado pipreqs")
    try:
        required = {"pipreqs"}
        installed = {pkg.key for pkg in pkg_resources.working_set}
        missing = required - installed
        if missing:
            python = sys.executable
            subprocess.check_call(
            [python, "-m", "pip", "install", *required], stdout=subprocess.DEVNULL
            )
            subprocess.check_call(
            [python, '-m', "pip", "install", "-r", "requirements.txt"]
            )
            logging.info("Se instalo pipreqs")
        else:
            print("PIPREQS INSTALADO")
            print("Modulos en requirements instalados")
            logging.info("Pipreqs ya estaba instalado")
    except:
        print("Modulo pipreqs no encontrado")
        logging.debug("No se encontró pipreqs, pero ya es posible volver a correr el codigo ya que se instaló automáticamente" )

#WebScrapping
class Scraping:
    def scrapingImages(self, url):
        print("\nObteniendo imagenes de la url:" + url)

        try:
            response = requests.get(url)
            parsed_body = html.fromstring(response.text)

            # expresion regular para obtener imagenes
            images = parsed_body.xpath("//img/@src")

            print("Imagenes %s encontradas" % len(images))

            # create directory for save images
            os.system("mkdir images")
            logging.info("Se creó un folder para imagenes")

            for image in images:
                if image.startswith("http") == False:
                    download = url + image
                else:
                    download = image
                print(download)
                # download images in images directory
                r = requests.get(download)
                f = open("images/%s" % download.split("/")[-1], "wb")
                f.write(r.content)
                logging.info("Se descargo imagen con dirreccion al folder creado")
                f.close()

        except Exception as e:
            print(e)
            print("Error conexion con " + url)
            logging.warning("Hubo error de conexion con la url")
            pass

    def scrapingPDF(self, url):
        print("\nObteniendo pdfs de la url:" + url)

        try:
            response = requests.get(url)
            parsed_body = html.fromstring(response.text)

            # expresion regular para obtener pdf
            pdfs = parsed_body.xpath('//a[@href[contains(., ".pdf")]]/@href')

            # create directory for save pdfs
            if len(pdfs) > 0:
                os.system("mkdir pdfs")

            print("Encontrados %s pdf" % len(pdfs))
            logging.info("Se creo un folder para los pdfs")

            for pdf in pdfs:
                if pdf.startswith("http") == False:
                    download = url + pdf
                else:
                    download = pdf
                print(download)

                # descarga pdfs
                r = requests.get(download)
                f = open("pdfs/%s" % download.split("/")[-1], "wb")
                logging.info("se agregó pdf encontrado")
                f.write(r.content)
                f.close()

        except Exception as e:
            print(e)
            print("Error conexion con " + url)
            logging.warning("Hubo error de conexion con la url")
            pass


# bloque de obtencion de metadata
#Formato a Extración de Datos
def decode_gps_info(exif): #exif = 
    gpsinfo = {}
    if "GPSInfo" in exif:
        # Parse geo references.
        Nsec = exif["GPSInfo"][2][2]
        Nmin = exif["GPSInfo"][2][1]
        Ndeg = exif["GPSInfo"][2][0]
        Wsec = exif["GPSInfo"][4][2]
        Wmin = exif["GPSInfo"][4][1]
        Wdeg = exif["GPSInfo"][4][0]
        if exif["GPSInfo"][1] == "N":
            Nmult = 1
        else:
            Nmult = -1
        if exif["GPSInfo"][1] == "E":
            Wmult = 1
        else:
            Wmult = -1
        Lat = Nmult * (Ndeg + (Nmin + Nsec / 60.0) / 60.0)
        Lng = Wmult * (Wdeg + (Wmin + Wsec / 60.0) / 60.0)
        exif["GPSInfo"] = {"Lat": Lat, "Lng": Lng}
        input()


def get_exif_metadata(image_path): #image_path ruta de la imagen con nombre /carpeta/imagen.jpg
    ret = {}
    image = Image.open(image_path)
    if hasattr(image, "_getexif"):
        exifinfo = image._getexif()
        if exifinfo is not None:
            for tag, value in exifinfo.items():
                decoded = TAGS.get(tag, tag)
                ret[decoded] = value
    decode_gps_info(ret)
    return ret


def printMeta():
    informe = open("Reporte_Imagenes.txt", "w+")
    logging.info("Se creo un informe con los metadatos obtenidos de las imagenes")
    ruta = "images"

    os.chdir(ruta)
    for root, dirs, files in os.walk(".", topdown=False):
        for name in files:
            informe.write("nombre: " + (name))
            informe.write("\n")
            try:
                exifData = {}
                exif = get_exif_metadata(name)
                for metadata in exif:
                    informe.write("[+] %s - Value: %s " % (metadata, exif[metadata]))
                    informe.write("\n")

            except:
                import sys, traceback
                traceback.print_exc(file=sys.stdout)
            informe.write("\n\n")
    informe.close()
    print("La obtencion de metadatos ha sido exitosa \n listos en archivo Reporte.txt")

#PENDIENTE MetadataPDF
def printPDF():
    os.chdir(pathlib.Path(__file__).parent.absolute())
    Informe = open("Reporte_PDFs.txt", "w+")
    logging.info("Se creo un informe con los metadatos obtenidos de las imagenes")
    for dirpath, dirs, files in os.walk(".", topdown=False):
        for name in files:
            ext = name.lower().rsplit(".", 1)[-1]  # archivo.nombre.algo.pdf
            if ext in ["pdf"]:
                pdfFile = PdfFileReader(open(dirpath + os.path.sep + name, "rb"))

                docInfo = pdfFile.documentInfo
                Informe.write("Archivo: " + name.lower())
                Informe.write("\n")
                Informe.write(
                    "[+] Cantidad de paginas: " + str(pdfFile.numPages) + "\n"
                )
                Informe.write("[+] Encriptado: " + str(pdfFile.isEncrypted) + "\n")
                for metaItem in docInfo:
                    Informe.write(
                        "[+] " + str(metaItem) + ": " + str(docInfo[metaItem])
                    )
                    Informe.write("\n")
            Informe.write("\n\n")
    Informe.close()

def encode():
    os.chdir(pathlib.Path(__file__).parent.absolute())
    base64.encode(
        open("Reporte_Imagenes.txt", "rb"), open("ReporteB64_Imagenes.txt", "wb"))
    base64.encode(open("Reporte_PDFs.txt", "rb"), open("ReporteB64_PDFs.txt", "wb"))

def envioCorreos(rec):
    print("Se hará un envio de correo con los reportes obtenidos")
    try:
        logging.info("Se enviara un correo con los reportes obtenidos")
        body = "Reportes del Web Scraping"
        sender_email = "pc2021pia@gmail.com"
        receiver_email = rec

        msg = MIMEMultipart()
        msg["Subject"] = "[PIA 2021]"
        msg["From"] = sender_email
        msg["To"] = receiver_email

        msgText = MIMEText("<b>%s</b>" % (body), "html")
        msg.attach(msgText)

        # filename = "example.txt"
        # msg.attach(MIMEText(open(filename).read()))
        adjunto = MIMEBase("application", "octect-stream")
        adjunto.set_payload(open("ReporteB64_Imagenes.txt", "rb").read())
        adjunto.add_header(
            "content-Disposition", 'attachment; filename="Reporte_Imagenes.txt"'
        )
        msg.attach(adjunto)

        adjunto = MIMEBase("application", "octect-stream")
        adjunto.set_payload(open("ReporteB64_PDFs.txt", "rb").read())
        adjunto.add_header(
            "content-Disposition", 'attachment; filename="Reporte_PDFs.txt"'
        )
        msg.attach(adjunto)

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as smtpObj:
                smtpObj.ehlo()
                smtpObj.starttls()
                smtpObj.login("pc2021pia@gmail.com", "PC06102021")
                smtpObj.sendmail(sender_email, receiver_email, msg.as_string())
                logging.info("Se envió el correo con los reportes obtenidos")
        except Exception as e:
            print(e)

    except FileNotFoundError:
        print("Archivo Reporte_imagenes.txt no encontrado")
        logging.info("No se encontraron los reportes para el envío")

def APImail(email, key):
    logging.info("Se hará uso de una Api de correos")
    url = "https://mailcheck.p.rapidapi.com/"
    querystring = {"disable_test_connection":"true","domain":email}
    headers = {
        'x-rapidapi-host': "mailcheck.p.rapidapi.com",
        'x-rapidapi-key': key
        }
    response = requests.request("GET", url, headers=headers, params=querystring)
    print(response.text)

def Fdqn():
    logging.info("Se buscará el nombre de dominio completo del equipo")
    fqdn = socket.getfqdn()
    print("Fully qualified domain name of this computer is:");
    print(fqdn)
    
def ReglasPS():
    fpath = Path("powershellpia.ps1").absolute()
    p = subprocess.Popen(["powershell.exe", fpath], stdout=sys.stdout)
    print(fpath)
    




    
    