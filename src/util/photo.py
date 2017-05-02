import PIL.ExifTags
from PIL import Image
from PIL.ExifTags import GPSTAGS, TAGS
from PIL import Image
import piexif


### http://eran.sandler.co.il/2011/05/20/extract-gps-latitude-and-longitude-data-from-exif-using-python-imaging-library-pil/
#from src.albums.util.time import get_datetime_by_string
from src.ccfam import settings


def get_exif_data_by_image_path(image_path):
    image = Image.open(image_path)
    return get_exif_data(image)


def get_exif_data(image):
    """Returns a dictionary from the exif data of an PIL Image item. Also converts the GPS Tags"""
    exif_data = {}
    info = image._getexif()
    if info:
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            if decoded == "GPSInfo":
                gps_data = {}
                for t in value:
                    sub_decoded = GPSTAGS.get(t, t)
                    gps_data[sub_decoded] = value[t]

                exif_data[decoded] = gps_data
            else:
                exif_data[decoded] = value

    return exif_data


def _get_if_exist(data, key):
    if key in data:
        return data[key]

    return None


def _convert_to_degress(value):
    """Helper function to convert the GPS coordinates stored in the EXIF to degress in float format"""
    d0 = value[0][0]
    d1 = value[0][1]
    d = float(d0) / float(d1)

    m0 = value[1][0]
    m1 = value[1][1]
    m = float(m0) / float(m1)

    s0 = value[2][0]
    s1 = value[2][1]
    s = float(s0) / float(s1)

    return d + (m / 60.0) + (s / 3600.0)


def get_lat_lon(exif_data):
    """Returns the latitude and longitude, if available, from the provided exif_data (obtained through get_exif_data above)"""
    lat = None
    lon = None

    if "GPSInfo" in exif_data:
        gps_info = exif_data["GPSInfo"]

        gps_latitude = _get_if_exist(gps_info, "GPSLatitude")
        gps_latitude_ref = _get_if_exist(gps_info, 'GPSLatitudeRef')
        gps_longitude = _get_if_exist(gps_info, 'GPSLongitude')
        gps_longitude_ref = _get_if_exist(gps_info, 'GPSLongitudeRef')

        if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
            lat = _convert_to_degress(gps_latitude)
            if gps_latitude_ref != "N":
                lat = 0 - lat

            lon = _convert_to_degress(gps_longitude)
            if gps_longitude_ref != "E":
                lon = 0 - lon

    return lat, lon


###

def print_exif_data(image_path):
    image = Image.open(image_path)
    exif_data = get_exif_data(image)
    for k, v in exif_data.items():
        print(k, ':', v)


# http://stackoverflow.com/questions/22045882/modify-or-delete-exif-tag-orientation-in-python
# http://piexif.readthedocs.io/en/latest/sample.html?highlight=orientation
def rotate_and_compress_image(img, filename):

    #img = Image.open(filename)

    if "exif" in img.info:
        exif_dict = piexif.load(img.info["exif"])

        if piexif.ImageIFD.Orientation in exif_dict["0th"]:
            orientation = exif_dict["0th"].pop(piexif.ImageIFD.Orientation)

            if orientation == 2:
                img = img.transpose(Image.FLIP_LEFT_RIGHT)
            elif orientation == 3:
                img = img.rotate(180, expand=True)
            elif orientation == 4:
                img = img.rotate(180, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
            elif orientation == 5:
                img = img.rotate(-90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
            elif orientation == 6:
                img = img.rotate(-90, expand=True)
            elif orientation == 7:
                img = img.rotate(90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
            elif orientation == 8:
                img = img.rotate(90, expand=True)

            # exif_bytes = None
            # try:
            #     exif_bytes = piexif.dump(exif_dict)
            # except Exception as e:
            #     print('exception: ', e)
            #
            # if exif_bytes:
            #     img.save(filename.file.name, overwrite=True, optimize=True, quality=settings.IMAGE_QUALITY, exif=exif_bytes)
            # else:

            img.save(filename.file.name, overwrite=True, optimize=True, quality=settings.IMAGE_QUALITY)


# def is_jpeg(image_full_path):
#     return Image.open(image_full_path).format.lower() == 'jpeg'
def is_jpeg(image):
    return image.format.lower() == 'jpeg'


def get_image(image_path):
    print('settings.IMAGE_QUALITY', settings.IMAGE_QUALITY)
    print('settings.ENV', settings.ENV)
    if settings.ENV == 'dev':  # local
        image_full_path = settings.MEDIA_ROOT + "/" + image_path
        return Image.open(image_full_path)
    elif settings.ENV == 'prod':  # on s3
        # http://stackoverflow.com/questions/18729026/upload-images-to-amazon-s3-using-django
        from boto.s3.connection import S3Connection
        from boto.s3.key import Key

        conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)
        k = Key(bucket)
        k.key = 'media/' + image_path  # for example, 'images/bob/resized_image1.png'
        tmp_file_name = 'tmp.file'
        k.get_contents_to_filename(tmp_file_name)
        return Image.open(tmp_file_name)

# image_path = '/Users/Cliff/per/static/pictures/sample/Abstract_Shapes.jpg'
# img = PIL.Image.open(image_path)
# exif_data = get_exif_data(img)
# print(exif_data)
# print(is_jpeg(image_path))

#datetime_data = exif_data['DateTime']
# print (get_lat_lon(exif_data)[0] is None)
#   print (exif_data.get('Orientation'))
#
# print (get_datetime_by_string(exif_data.get('DateTime')))
#print_exif_data(image_path)

