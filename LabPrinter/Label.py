#!/usr/bin/env python
from PIL import Image, ImageFont, ImageDraw
import qrcode
import barcode
from barcode.writer import ImageWriter
from CustomWriter import CustomWriter

class Label():
    
    def __init__(self, (width, height), text = None, barcode = None, qrcode = None):
        self.images = {}
        print (width, height)
        if text != None:
            text_image = make_text(text, width, height)
            text_image.save("text_image", "PNG")
            self.images.update({"text image" : text_image})
        if barcode != None:
            bar_image = make_bar_image(barcode, int(15*width/24), int(width//3))
            bar_size = (int(15*width/24), int(width//3))
            bar_image = bar_image.resize(bar_size)
            bar_image.save("bar_image", "PNG")
            self.images.update({"bar image" : bar_image})
        if qrcode != None:
            qr_image = make_qr_image(qrcode)
            qr_size = (int(width//4), int(width//4))
            print qr_size
            qr_image = qr_image.resize(qr_size, Image.NEAREST)
            qr_image.save("qr_image", "PNG")
            self.images.update({"qr image" : qr_image})
        
        image = text_image
        qr_pos = (int(width//24), int(width//24))
        image.paste(qr_image, qr_pos)
        bar_pos = (int(9*width//24), int(width//24))
        image.paste(bar_image, bar_pos)
        image.save('composite', 'PNG')
        
        
    
        
def make_text(text, width, height):
    """ Draw a box with text in it in a crude way"""
    """
        text : string to be drawn
        size : tuple of pixel dimensions (width, height) for the box
    """

    image = Image.new("RGB", (width, height), "white")
    usr_font = ImageFont.truetype("/home/bioturk/SQUID-Devices/LabPrinter/DejaVuSansMono.ttf", 25)
    textbox = ImageDraw.Draw(image)
    color = (0,0,0)
    textbox.text((int(width//6),int(9*height//12)), text, fill = color, font=usr_font)
    del textbox
    return image
    
def make_bar_image(code, width, height):
    #writer = CustomWriter(width, height)
    ean = barcode.get('ean13', code, ImageWriter())
    return ean.render()
    
def make_qr_image(code):
    #need to return the image
    qr = qrcode.QRCode(
        version = 2,
        error_correction = qrcode.constants.ERROR_CORRECT_L,
        box_size = 10,
        border = 0
    )
    qr.add_data(code)
    qr.make(fit = True)
    img = qr.make_image()
    return img
        
    

