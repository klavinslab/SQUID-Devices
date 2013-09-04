#!/usr/bin/env python
import barcode
from barcode.writer import ImageWriter
from LabelWriter import LabelWriter
from Label import Label
"""
writer = ImageWriter()
writer.dpi=410
writer.module_height = 25
writer.module_width = .557
writer.font_size = 20
ean13 = barcode.get('ean13','123456789101', writer)
filename = ean13.save('ean13')
print filename
print writer.dpi



writer2 = LabelWriter(55, 30, "testing123testing")
ean132 = barcode.get('ean13', '123456789101', writer2)
filename = ean132.save('ean123')
"""
def mm2px(mm, dpi=410):
    return (mm * dpi) / 25.4

width = int(mm2px(55))
height = int(mm2px(30))
mylabel = Label((width,height), 'ALL YOUR LABELS SHALL BE ASSIMILATED', '123456789101', '101987654321')
