# coding=utf-8
from PIL import Image, ImageFilter, ImageEnhance
import time
import numpy


def segment(im):
    s = 3   # start position of first character
    w = 13  # width of character
    t = 0   # start position of top
    h = 22  # end position from top
    im_new = []
    for i in range(4):
        im1 = im.crop((s + w * i, t, s + w * (i + 1), h))
        im_new.append(im1)
    return im_new


def img_transfer(f_name):
    im = Image.open(f_name)
    im = im.convert('L')
    im = im.filter(ImageFilter.MedianFilter())
    enhancer = ImageEnhance.Contrast(im)
    im = enhancer.enhance(1)
    return im


# 图像二值化，黑色像素点标记成1，白色像素点标记成0
def get_binary_pix(im):
    # im = Image.open(im)
    img = numpy.array(im)
    rows, cols = img.shape
    for i in range(rows):
        for j in range(cols):
            if img[i, j] <= 128:
                img[i, j] = 0
            else:
                img[i, j] = 1
    binpix = numpy.ravel(img)
    return binpix


# 加载预测
def loadPreidict(img):
    im = img_transfer(img)
    pics = segment(im)
    rs = []
    for pic in pics:
        pixs = get_binary_pix(pic)
        rs.append(pixs)
    return rs


# 切割验证码
def cut_pictures(img):
    im = img_transfer(img)
    pics = segment(im)
    for pic in pics:
        # 存储路径
        pic.save('f:/code_cut/%s.jpg' % (int(time.time() * 1000000)), 'jpeg')

# for i in range(1000):
#   cut_pictures('f:/code/'+str(i)+'.jpg')
