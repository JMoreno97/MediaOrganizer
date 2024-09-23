import os.path
import pathlib
import shutil
import sys
import tkinter as tk

from exif import Image
from geopy import Nominatim
from tkinter import filedialog
from tkinter import messagebox

window = tk.Tk()

def getPlace(lat, lon, latRef, lonRef):
    lat = getDecimalType(lat)
    lon = getDecimalType(lon)
    lat, lon = getSignedLatLon(lat, lon, latRef, lonRef)
    locator = Nominatim(user_agent="media-organizer")
    coordinates = str(lat) + ", " + str(lon)
    location = locator.reverse(coordinates)
    return location.raw


def getDecimalType(coords):
    degrees = coords[0]
    minutes = coords[1]
    seconds = coords[2]

    return degrees + minutes / 60 + seconds / 3600


def getVideoMetadata(path):
    print("Getting metadata from video...")


def getImageMetadata(path):
    metadata = {}
    print("Getting metadata from image...")
    with open(path, 'rb') as src:
        img = Image(src)
        if img.has_exif:
            print(src.name + " has EXIF version " + img.exif_version)
            print("EXIF data: ")
            print("==================================")
            for tag in img.list_all():
                print("Tag: ", tag, " - Value: ", img.get(tag))
                metadata[tag] = img.get(tag)
            print("==================================")
        else:
            print(src.name + " has no EXIF data")
    return metadata


def getSignedLatLon(lat, lon, latRef, lonRef):
    if latRef.lower() == 's':
        lat = -lat
    if lonRef.lower() == 'w':
        lon = -lon

    return lat, lon


def createNewFolders(path, country, city):
    folderPath = path + "/" + country + "/" + city
    print(folderPath)
    if not os.path.exists(folderPath):
        os.makedirs(folderPath, exist_ok=True)
        print("Created new folder: " + folderPath)


def copyMedia(item, path, country, city):
    folderPath = path + "/" + country + "/" + city
    shutil.copy(item, folderPath)
    print("Copy successful")


def createGUI():
    tk.Button(text="Carpeta origen", command=selectOriginDirectory).pack()
    tk.Button(text="Carpeta destino", command=selectDestinationDirectory).pack()
    tk.Button(text="Confirmar", command=start).pack()


originDirectory = tk.StringVar()


def selectOriginDirectory():
    directory = filedialog.askdirectory()
    if directory:
        originDirectory.set(directory)
    print("Selected origin directory: " + originDirectory.get())


destinationDirectory = tk.StringVar()


def selectDestinationDirectory():
    directory = filedialog.askdirectory()
    if directory:
        destinationDirectory.set(directory)
    print("Selected destinarion directory: " + destinationDirectory.get())


def start():
    print(originDirectory.get())
    print(destinationDirectory.get())
    if originDirectory.get() != "" and destinationDirectory.get() != "":
        rootFolder = pathlib.Path(originDirectory.get())
        for item in rootFolder.iterdir():
            if item.is_file():
                print("Processing file: ", item)
                # Check if folders have images or videos
                if item.suffix in imageExtensions:
                    # Get metadata from images
                    info = getImageMetadata(item.absolute())
                    if info['gps_latitude'] and info['gps_longitude']:
                        lat = info['gps_latitude']
                        latitude_ref = info['gps_latitude_ref']
                        lon = info['gps_longitude']
                        longitude_ref = info['gps_longitude_ref']
                        place = getPlace(lat, lon, latitude_ref, longitude_ref)
                        print(place)
                        print(place['address']['country'])
                        print(place['address']['village'])
                        createNewFolders(destinationDirectory.get(), place['address']['country'], place['address']['village'])
                        copyMedia(item, destinationDirectory.get(), place['address']['country'], place['address']['village'])
                    else:
                        print("No GPS data: " + item.name)
                elif item.suffix in videoExtensions:
                    # Get metadata from videos
                    getVideoMetadata(item.absolute())
    else:
        messagebox.showerror("ERROR", "No has seleccionado una carpeta de origen o de destino")


imageExtensions = (".jpg", ".jpeg", ".png", ".gif", ".tiff", ".bmp")
videoExtensions = (".mp4", ".avi", ".mov", ".wmv", ".flv", ".mkv")

if __name__ == '__main__':
    createGUI()
    print(sys.argv)
    if len(sys.argv) == 2:
        path = sys.argv[1]
        # Get folders in path
        rootFolder = pathlib.Path(path)
        for item in rootFolder.iterdir():
            if item.is_file():
                print("Processing file: ", item)
                # Check if folders have images or videos
                if item.suffix in imageExtensions:
                    # Get metadata from images
                    info = getImageMetadata(item.absolute())
                    if info['gps_latitude'] and info['gps_longitude']:
                        lat = info['gps_latitude']
                        latitude_ref = info['gps_latitude_ref']
                        lon = info['gps_longitude']
                        longitude_ref = info['gps_longitude_ref']
                        place = getPlace(lat, lon, latitude_ref, longitude_ref)
                        print(place)
                        print(place['address']['country'])
                        print(place['address']['village'])
                        createNewFolders(path, place['address']['country'], place['address']['village'])
                        copyMedia(item, path, place['address']['country'], place['address']['village'])
                    else:
                        print("No GPS data: " + item.name)
                elif item.suffix in videoExtensions:
                    # Get metadata from videos
                    getVideoMetadata(item.absolute())

    else:
        print("Script must receive one argument (path)")

    window.mainloop()

