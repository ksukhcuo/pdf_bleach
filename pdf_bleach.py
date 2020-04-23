#%% import library
import os, sys
from pathlib import Path
from pdf2image import convert_from_path
import img2pdf
import numpy as np
import cv2

#%% function
def pil2cv(image):
    ''' PIL型 -> OpenCV型 '''
    new_image = np.array(image, dtype=np.uint8)
    if new_image.ndim == 2:  # monochrome
        pass
    elif new_image[:,:,:].shape[2] == 3:  # color
        new_image = new_image[:, :, ::-1]
    elif new_image.shape[2] == 4:  # transparent
        new_image = new_image[:, :, [2, 1, 0, 3]]
    return new_image

#%% convert pdf to image
def pdf2img(pdf_path, dpi=200):
    # addinig poppler\bin to PATH
    bin_path = "C:\\include\\poppler-0.68.0\\bin"
    os.environ['PATH'] = '{};{}'.format(os.environ['PATH'], bin_path)

    # convert PDF to Image
    pages = convert_from_path(str(pdf_path), dpi)

    # delete poppler\bin from PATH
    os.environ['PATH'].replace((';'+bin_path),'')

    return pages

#%% convert image to pdf
def img_to_pdf(imgs, fname):
    with open(fname, 'wb') as f:
        f.write( img2pdf.convert([str(i) for i in imgs]) )

#%% whitening backgrounds
def whitening(infile, outfile):
    # convert pdf file to image
    pages = pdf2img(str(infile), dpi=300)

    # from PIL  to OpenCV
    pages = [pil2cv(f) for f in pages]

    # gray scale
    imgs = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) for f in pages]

    # filter
    imgs_a = [cv2.GaussianBlur(f, (3, 3), 1) for f in imgs]

    # binarization
    imgs_a = [cv2.threshold(f, 200, 1, cv2.THRESH_BINARY_INV)[1] for f in imgs_a]

    # whitening background
    for i, img in enumerate(imgs):
        imgs[i] = cv2.bitwise_not( cv2.multiply(imgs_a[i], cv2.bitwise_not(img)) )

    # save image file
    imgf = []
    for i, img in enumerate(imgs):
        file_name = outfile.stem + "_{:03d}".format(i + 1) + ".jpg"
        imgf.append(outfile.parent / file_name)
        cv2.imwrite(str(imgf[i]), img)
    # convert image file into pdf file
    img_to_pdf(imgf, outfile)
    # remove image file
    for f in imgf:
        os.remove(f)

#%% main
if __name__ == '__main__':
    
    cwd = Path.cwd()
    in_dir = cwd / "input"
    out_dir = cwd / "output"

    files = in_dir.glob("*.pdf")
    
    for f in files:
        whitening(f, out_dir/f.name)

