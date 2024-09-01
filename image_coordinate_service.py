from PIL import Image
from pprint import pprint
import piexif
import webbrowser

codec = 'ISO-8859-1'

def exif_to_tag(exif_dict):
    exif_tag_dict = {}
    thumbnail = exif_dict.pop('thumbnail', None)
    
    if thumbnail:
        exif_tag_dict['thumbnail'] = thumbnail.decode(codec)
    
    for ifd in exif_dict:
        exif_tag_dict[ifd] = {}
        for tag in exif_dict[ifd]:
            try:
                element = exif_dict[ifd][tag].decode(codec)
            except AttributeError:
                element = exif_dict[ifd][tag]
            except UnicodeDecodeError:
                element = exif_dict[ifd][tag]
            exif_tag_dict[ifd][piexif.TAGS[ifd][tag]["name"]] = element

    return exif_tag_dict

def get_decimal_from_dms(dms, ref):
    """
    Converts GPS coordinates in DMS (Degrees, Minutes, Seconds) format to decimal format.
    """
    degrees = dms[0][0] / dms[0][1]
    minutes = dms[1][0] / dms[1][1] / 60.0
    seconds = dms[2][0] / dms[2][1] / 3600.0
    if ref in ['S', 'W']:
        degrees = -degrees
        minutes = -minutes
        seconds = -seconds
    return round(degrees + minutes + seconds, 6)

def open_location_in_map(lat, lon):
    """
    Opens a browser window to display the location on Google Maps.
    """
    google_maps_url = f"https://www.google.com/maps?q={lat},{lon}"
    webbrowser.open(google_maps_url)

def find_maps_image_location(filename):
    try:
        im = Image.open(filename)
    except (FileNotFoundError, IOError) as e:
        print(f"Error opening the image: {e}")
        return
    
    exif_data = im.info.get('exif')

    if not exif_data:
        print("No EXIF data found.")
        return

    exif_dict = piexif.load(exif_data)
    exif_dict = exif_to_tag(exif_dict)

    if 'GPS' in exif_dict:
        gps_info = exif_dict['GPS']
        pprint(gps_info)
        # Extract GPS coordinates
        try:
            gps_latitude = gps_info['GPSLatitude']
            gps_latitude_ref = gps_info['GPSLatitudeRef']
            gps_longitude = gps_info['GPSLongitude']
            gps_longitude_ref = gps_info['GPSLongitudeRef']
            
            # Convert to decimal format
            lat = get_decimal_from_dms(gps_latitude, gps_latitude_ref)
            lon = get_decimal_from_dms(gps_longitude, gps_longitude_ref)
            
            print(f"Latitude: {lat}, Longitude: {lon}")
            
            # Open the location in Google Maps
            open_location_in_map(lat, lon)
        
        except KeyError:
            print("GPS data is incomplete or missing.")
    else:
        print("No GPS data found.")
