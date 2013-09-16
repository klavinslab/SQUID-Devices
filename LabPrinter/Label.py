#!/usr/bin/env python
from PIL import Image, ImageFont, ImageDraw
import qrcode
import barcode
from barcode.writer import ImageWriter
from CustomWriter import CustomWriter

"""
Joseph Sullivan
Research Assistant
ISTC PC

This class contructs a PNG image representing a label to be printed. The label is saved as 'label.png' in the folder containing this module.
Probably not the most well conceived class, it still works well. After instantiating an instance of Label it is prudent to delete it, since
the label image is saved to the hard disk as part of the construction of the label object.

Inputs:
data (dict) with the fields
{'width'   : integer (mm),
 'height'  : integer (mm),
 'text'    : string,
 'barcode' : twelve digit integer,
 'qrcode'  : character string,
 'fontsize': integer (point)}

None of the data keys are mandatory, however without one of the content keys (text, barcode, qrcode), there will be no label to construct.
"""

class Label():
    
    def __init__(self, data):
        """ Constructs a Label image using PIL
        Inputs
            (width,height)      tuple of dimensions of the label in pixels
            data                dictionary of data used to create the label
            
            {'barcode' = 12 digit integer string,
             'qrcode'  = string,
             'text'    = string}"""
             
        self.images = {}
        
        if data.has_key('width'):
            width = data['width']
        else:
            width = int(mm2px(100))
        if data.has_key('height'):
            height = data['height']
        else:
            height = int(mm2px(50))
        if data.has_key('fontsize'):
            font_size = int(fontsize)
        else:
            font_size = 25
            
        if data.has_key('text') & data.has_key('barcode') & data.has_key('qrcode'):
            """make a label with all three attributes"""
            text_image = make_text(data['text'],width,height, font_size)
            bar_size = (int(15*width/24), int(width//3))
            bar_image = make_bar_image(data['barcode'])
            bar_image = bar_image.resize(bar_size)
            qr_image = make_qr_image(data['qrcode'])
            qr_size = (int(width//4), int(width//4))
            qr_image = qr_image.resize(qr_size, Image.NEAREST)
            image = text_image
            qr_pos = (int(width//24), int(width//24))
            image.paste(qr_image, qr_pos)
            bar_pos = (int(9*width//24), int(width//24))
            image.paste(bar_image, bar_pos)
            image.save('label.png', 'PNG')
            
        if data.has_key('text') & data.has_key('qrcode') & (not data.has_key('barcode')):
            text_image = make_text(data['text'],width,height)
            qr_image = make_qr_image(data['qrcode'])
            qr_size = (int(width//4), int(width//4))
            qr_image = qr_image.resize(qr_size, Image.NEAREST)
            qr_pos = (int(width//24), int(width//24))
            image = text_image
            image.paste(qr_image, qr_pos)
            image.save('label.png', 'PNG')
        
        if data.has_key('text') & data.has_key('barcode') & (not data.has_key('qrcode')):
            text_image = make_text(data['text'],width,height)
            bar_size = (int(11*width/12), int(width//3))
            bar_image = make_bar_image(data['barcode'])
            bar_image = bar_image.resize(bar_size)
            bar_pos(int(width//24), int(width//24))
            image = text_image
            image.paste(bar_image, bar_pos)
            image.save('label.png', 'PNG')
            
        if data.has_key('qrcode') & (not data.has_key('text')) & (not data.has_key('barcode')):
            background = Image.new("RGB", (width, height), "white")
            qr_image = make_qr_image(data['qrcode'])
            qr_size = (int(width//4), int(width//4))
            qr_pos = (int(width//2 - width//8), int(height//2 - width//8))
            qr_image = qr_image.resize(qr_size)
            background.paste(qr_image, qr_pos)
            background.save('label.png', 'PNG')
            
        if data.has_key('barcode') & (not data.has_key('text')) & (not data.has_key('qrcode')):
            bar_image = make_bar_image(data['barcode'])
            bar_image.save('label.png', 'PNG')
        
        if data.has_key('text') & (not data.has_key('barcode')) & (not data.has_key('qrcode')):
            """Text only"""
            text = data['text']
            image = Image.new("RGB", (width, height), "white")
            usr_font = ImageFont.truetype("/home/bioturk/SQUID-Devices/LabPrinter/DejaVuSansMono.ttf", font_size)
            textbox = ImageDraw.Draw(image)            
            color = (0,0,0)
            font_size_px = textbox.textsize('W', font = usr_font)
            lines = breakup_lines(text, width, font_size_px[0])
            for i in range(len(lines)):
                pos = (int(width//24), int(2*width//24 + i*(font_size_px[1] + 2)))
                textbox.text(pos, lines[i], font = usr_font, fill = color)
            image.save('label.png', 'PNG')
           
def make_text(text, width, height, font_size):
    """ Draw a box with text in it in a crude way"""
    """
        text : string to be drawn
        size : tuple of pixel dimensions (width, height) for the box
    """
    print 'in make_text'
    print text
    image = Image.new("RGB", (width, height), "white")
    usr_font = ImageFont.truetype("/home/bioturk/SQUID-Devices/LabPrinter/DejaVuSansMono.ttf", font_size)
    textbox = ImageDraw.Draw(image)
    color = (0,0,0)
    font_size_px = textbox.textsize('W', font = usr_font)
    lines = breakup_lines(text, width, font_size_px[0])
    print lines
    for i in range(len(lines)):
        pos = (int(width//24), int(9*width//24 + i*(font_size_px[1] + 2)))
        textbox.text(pos, lines[i], font = usr_font, fill = color)
    return image
        
def breakup_lines(text, width, fontwidthpx):
    for i in range(len(text)):
        if text[-i] == ' ':
            if ( fontwidthpx*len(text[0:-(i+1)]) ) < int(11*width//12):
                lines = []
                lines.append(text[0:-i])
                print "block one:"
                print lines
                if ( fontwidthpx*len(text[-(i-1):]) ) < int(11*width//12):
                    lines.append(text[-(i-1):])
                    print "block two:"
                    print lines
                    return lines
                else:
                    print 'recursive call'
                    lines.extend(breakup_lines(text[-(i-1):], width, fontwidthpx))
                    return lines
                
def make_bar_image(code):
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
  
def mm2px(mm, dpi=203):
    return (mm * dpi) / 25.4        
    

