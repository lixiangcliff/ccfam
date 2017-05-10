from io import BytesIO

import PIL.ExifTags
from PIL import Image
from PIL.ExifTags import GPSTAGS, TAGS
from PIL import Image
import piexif

### http://eran.sandler.co.il/2011/05/20/extract-gps-latitude-and-longitude-data-from-exif-using-python-imaging-library-pil/
# from src.albums.util.time import get_datetime_by_string
from boto.s3.connection import S3Connection
from boto.s3.key import Key

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
# https://gist.github.com/rigoneri/4716919

def rotate_and_compress_image(img, photo_obj):
    # rotate
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

    # https://jargonsummary.wordpress.com/2011/01/08/how-to-resize-images-with-python/
    # resize
    orig_width = img.size[0]
    orig_height = img.size[1]
    resized_width, resized_height = get_resized_width_and_height(img.size[0], img.size[1])
    if orig_width != resized_width or orig_height != resized_width:
        img = img.resize((resized_width, resized_height), PIL.Image.ANTIALIAS)
    photo_obj.width = resized_width
    photo_obj.height = resized_height

    # compress and write back
    if settings.ENV == 'dev':  # local
        img.save(photo_obj.image.file.name, overwrite=True, optimize=True,
                 quality=settings.IMAGE_QUALITY) # photo_obj.image.file.name is a full path of local file
        photo_obj.size = photo_obj.image.size
    elif settings.ENV == 'prod':  # on s3
        key = get_s3_image_file_key(photo_obj.image_path)

        tmp = BytesIO()
        img.save(tmp, 'JPEG', quality=settings.IMAGE_QUALITY)
        tmp.seek(0)
        output_data = tmp.getvalue()

        photo_obj.size = tmp.tell()

        headers = dict()
        headers['Content-Type'] = 'image/jpeg'
        headers['Content-Length'] = str(len(output_data))
        key.set_contents_from_string(output_data, headers=headers, policy='public-read')

        tmp.close()



def get_resized_width_and_height(width, height):
    larger_dimension = width if width >= height else height
    smaller_dimension = width if width <= height else height
    if larger_dimension <= settings.IMAGE_LARGER_DIMENSION_PIXEL_COUNT: # do not need to resize
        return width, height
    resize_ratio = float(settings.IMAGE_LARGER_DIMENSION_PIXEL_COUNT) / float(larger_dimension)
    print('resize_ratio:', resize_ratio)
    resized_larger_dimension = settings.IMAGE_LARGER_DIMENSION_PIXEL_COUNT
    resized_smaller_dimension = int((float(smaller_dimension) * float(resize_ratio)))

    if width >= height:
        return resized_larger_dimension, resized_smaller_dimension
    else:
        return resized_smaller_dimension, resized_larger_dimension


def is_jpeg(image):
    return image.format.lower() == 'jpeg'


def get_image(image_path):
    if settings.ENV == 'dev':  # local
        image_full_path = settings.MEDIA_ROOT + "/" + image_path
        return Image.open(image_full_path)
    elif settings.ENV == 'prod':  # on s3
        key = get_s3_image_file_key(image_path)
        image_string = key.get_contents_as_string()
        return Image.open(BytesIO(image_string))


def get_s3_image_file_key(image_path):
    conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
    bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)
    key = Key(bucket)
    key.key = 'media/' + image_path
    return key

# image_path = '/Users/Cliff/per/static/pictures/sample/Abstract_Shapes.jpg'
# img = PIL.Image.open(image_path)
# exif_data = get_exif_data(img)
# print(exif_data)
# print(is_jpeg(image_path))

# datetime_data = exif_data['DateTime']
# print (get_lat_lon(exif_data)[0] is None)
#   print (exif_data.get('Orientation'))
#
# print (get_datetime_by_string(exif_data.get('DateTime')))
# print_exif_data(image_path)
