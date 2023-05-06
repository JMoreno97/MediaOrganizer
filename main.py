import json
import pathlib
import sys
from urllib.request import urlopen

from PIL.ExifTags import TAGS
from exif import Image
from geopy import Nominatim


def getPlace(lat, lon):
    lat = getDecimalType(lat)
    lon = getDecimalType(lon)
    locator = Nominatim(user_agent="myGeocoder")
    coordinates = str(lat) + ", " + str(lon)
    location = locator.reverse(coordinates)
    print(location.raw)
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
            for tag in img.list_all():
                print("Tag: ", tag, " - Value: ", img.get(tag))
                metadata[tag] = img.get(tag)
        else:
            print(src.name + " has no EXIF data")
    return metadata


imageExtensions = (".jpg", ".jpeg", ".png", ".gif", ".tiff", ".bmp")
videoExtensions = (".mp4", ".avi", ".mov", ".wmv", ".flv", ".mkv")

if __name__ == '__main__':
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
                        lon = info['gps_longitude']
                        place = getPlace(lat, lon)
                    else:
                        print("No GPS data")
                elif item.suffix in videoExtensions:
                    # Get metadata from videos
                    getVideoMetadata(item.absolute())

    else:
        print("Script must receive one argument (path)")
