from PIL import Image


def resize(img_path, basewidth=400):
    img = Image.open(img_path)
    W, H = img.size
    wpercent = (basewidth / float(W))
    hsize = int((float(H) * float(wpercent)))
    return img.resize((basewidth, hsize), Image.ANTIALIAS)
