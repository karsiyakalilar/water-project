# modified version of http://code.activestate.com/recipes/362879/
from PIL import Image, ImageEnhance
import random

def flip_horizontal(im): return im.transpose(Image.FLIP_LEFT_RIGHT)
def flip_vertical(im): return im.transpose(Image.FLIP_TOP_BOTTOM)
def rotate_180(im): return im.transpose(Image.ROTATE_180)
def rotate_90(im): return im.transpose(Image.ROTATE_90)
def rotate_270(im): return im.transpose(Image.ROTATE_270)
def transpose(im): return rotate_90(flip_horizontal(im))
def transverse(im): return rotate_90(flip_vertical(im))
orientation_funcs = [None,
                 lambda x: x,
                 flip_horizontal,
                 rotate_180,
                 flip_vertical,
                 transpose,
                 rotate_270,
                 transverse,
                 rotate_90
                ]
def apply_orientation(im):
    """
    Extract the oritentation EXIF tag from the image, which should be a PIL Image instance,
    and if there is an orientation tag that would rotate the image, apply that rotation to
    the Image instance given to do an in-place rotation.

    :param Image im: Image instance to inspect
    :return: A possibly transposed image instance
    """

    try:
        kOrientationEXIFTag = 0x0112
        if hasattr(im, '_getexif'): # only present in JPEGs
            e = im._getexif()       # returns None if no EXIF data
            if e is not None:
                print("exif found")
                orientation = e[kOrientationEXIFTag]
                f = orientation_funcs[orientation]
                return f(im)
            else:
                print("exif exists as a func but no value returned")
                return im
        else:
            print("no exif found")
            return im

    except:
        print("problem applying orientation to the image")
        return(im)

def reduce_opacity(im, opacity):
    """Returns an image with reduced opacity."""
    assert opacity >= 0 and opacity <= 1
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    else:
        im = im.copy()
    alpha = im.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    im.putalpha(alpha)
    return im

def watermark(im, mark, position, opacity=1):
    """
        Adds a watermark to an image.
        change opacity
        apply orientation
        resize image
        apply watermark
    """
    # change opacity
    if opacity < 1:
        mark = reduce_opacity(mark, opacity)

    # if im.mode != 'RGBA':
    #     im = im.convert('RGBA')

    # apply orientation
    im = apply_orientation(im)

    # resize image
    if max(im.size) > 1000:
        _aspect_ratio = float(im.size[0]) / float(im.size[1])
        if _aspect_ratio >= 1:
            new_width = 1000
            new_height = int(1000 / _aspect_ratio)
        else:
            new_height = 1000
            new_width = int(1000 * _aspect_ratio)

        im = im.resize((new_width, new_height), Image.ANTIALIAS)

    # apply watermark
    layer = Image.new('RGBA', im.size, (0,0,0,0))
    if position == 'tile':
        for y in range(0, im.size[1], mark.size[1]):
            for x in range(0, im.size[0], mark.size[0]):
                layer.paste(mark, (x, y))
    elif position == 'scale':
        # crop off extras
        # either diffs[0] or diffs[1] is 0
        diffs = (mark.size[0] - im.size[0], mark.size[1] - im.size[1])
        mark = mark.crop((0, 0, 
                        mark.size[0] - diffs[0], 
                        mark.size[1] - diffs[1]))
        layer.paste(mark, (0,0))
    else:
        layer.paste(mark, position)
    
    # composite the watermark with the layer
    print("generated image")
    return Image.composite(layer, im, layer)

def generate(img_path, out_path, watermark_path):
  print(img_path)
  print(out_path)
  print(watermark_path)
  im = Image.open(img_path)
  mark = Image.open(watermark_path)
  print("generating image")  
  watermark(im, mark,
            # position=(0,0),
            position="scale",
            opacity=0.5).save(out_path, 'JPEG')

def test():
    img_path = "./uploads/IMG_0014.JPG"
    out_path = "./target_images/wm_IMG_0014.JPG"
    watermark_path = "./assets/water.png"
    generate(img_path, out_path, watermark_path)

if __name__ == "__main__":
    test()
  # generate("./uploads/test2.jpg",
  #   "./targets/wm_test2.jpg",
  #   "./assets/water.png")
