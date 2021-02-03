from PIL import Image, ImageOps, ImageDraw
import glob, os

def draw_ellipse(image, bounds, width=1, outline='black', antialias=4):
    """Improved ellipse drawing function, based on PIL.ImageDraw."""

    # Use a single channel image (mode='L') as mask.
    # The size of the mask can be increased relative to the imput image
    # to get smoother looking results. 
    mask = Image.new(
        size=[int(dim * antialias) for dim in image.size],
        mode='L', color='black')
    draw = ImageDraw.Draw(mask)

    # draw outer shape in white (color) and inner shape in black (transparent)
    for offset, fill in (width/-2.0, 'white'), (width/2.0, 'black'):
        left, top = [(value + offset) * antialias for value in bounds[:2]]
        right, bottom = [(value - offset) * antialias for value in bounds[2:]]
        draw.ellipse([left, top, right, bottom], fill=fill)

    # downsample the mask using PIL.Image.LANCZOS 
    # (a high-quality downsampling filter).
    mask = mask.resize(image.size, Image.LANCZOS)
    # paste outline color to input image through the mask
    image.paste(outline, mask=mask)


size = 40, 30

mask = Image.open('iconmask.png').convert('L')

for infile in glob.glob("./testicons/*.png"):
    file, ext = os.path.splitext(infile)
    filename=file[-2:]
    
    im = Image.open(infile)
    
    #im = im.resize(size,resample=0,box=None,reducing_gap=10)

    output = ImageOps.fit(im, mask.size, centering=(0.5, 0.5))
    output = output.convert('RGB')
    output.putalpha(mask)
    
    outputWidth, outputHeight = output.size

    ellipse_box = [3, 3, outputWidth-3, outputHeight-3]
    draw_ellipse(output, ellipse_box, width=5)
    #drawtest.ellipse((0,0,outputWidth, outputHeight), fill=(0,0,0), outline=(0,0,0))

    output.save(file + "drawmask" + ext, "PNG")
    #im.save(file + "resized" + ext, "PNG")
