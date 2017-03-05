import PIL.Image
import PIL.ExifTags

img = PIL.Image.open('/Users/Cliff/Downloads/6390788212880572933.jpg')
exif_data = img._getexif()

#print (exif_data)

exif = {
    PIL.ExifTags.TAGS[k]: v
    for k, v in img._getexif().items()
    if k in PIL.ExifTags.TAGS
}

#print ("#################")

for k, v in exif.items():
    #print(k, v)
    pass
