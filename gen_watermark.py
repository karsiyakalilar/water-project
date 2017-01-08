# modified version of http://code.activestate.com/recipes/362879/
from PIL import Image, ImageEnhance
import random

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
    """Adds a watermark to an image."""
    if opacity < 1:
        mark = reduce_opacity(mark, opacity)
    if im.mode != 'RGBA':
        im = im.convert('RGBA')

    if max(im.size) > 1000:
        _aspect_ratio = float(im.size[0]) / float(im.size[1])
        if _aspect_ratio >= 1:
            new_width = 1000
            new_height = int(1000 / _aspect_ratio)
        else:
            new_height = 1000
            new_width = int(1000 * _aspect_ratio)

        im = im.resize((new_width, new_height), Image.ANTIALIAS)

    # create a transparent layer the size of the image and draw the
    # watermark in that layer.
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
    img_path = "./uploads/a_syrian_in_istanbul_by_canankk-d7zppui.jpg"
    out_path = "./target_images/wm_a_syrian_in_istanbul_by_canankk-d7zppui.jpg"
    watermark_path = "./assets/water.png"
    generate(img_path, out_path, watermark_path)

if __name__ == "__main__":
    test()
  # generate("./uploads/test2.jpg",
  #   "./targets/wm_test2.jpg",
  #   "./assets/water.png")
