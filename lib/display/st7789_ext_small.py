# This code is originally from https://github.com/devbis/st7789py_mpy
# It's under the MIT license as well.
#
# Rewritten by Salvatore Sanfilippo.
#
# Copyright (C) 2024 Salvatore Sanfilippo <antirez@gmail.com>
# All Rights Reserved
# All the changes released under the MIT license as the original code.

import display.st7789_base as st7789_base, framebuf, struct

class ST7789(st7789_base.ST7789_base):

    # Write an upscaled character. Slower, but allows for big characters
    # and to set the background color to None.
    def upscaled_char(self,x,y,char,fgcolor,bgcolor,upscaling):
        bitmap = bytearray(8) # 64 bits of total image data.
        fb = framebuf.FrameBuffer(bitmap,8,8,framebuf.MONO_HMSB)
        fb.text(char,0,0,fgcolor[1]<<8|fgcolor[0])
        charsize = 8*upscaling
        if bgcolor: self.rect(x,y,charsize,charsize,bgcolor,fill=True)
        for py in range(8):
            for px in range(8):
                if not (bitmap[py] & (1<<px)): continue # Background
                if upscaling > 1:
                    self.rect(x+px*upscaling,y+py*upscaling,upscaling,upscaling,fgcolor,fill=True)
                else:
                    self.pixel(x+px,y+py,fgcolor)

    def upscaled_text(self,x,y,txt,fgcolor,*,bgcolor=None,upscaling=2):
        for i in range(len(txt)):
            self.upscaled_char(x+i*(8*upscaling),y,txt[i],fgcolor,bgcolor,upscaling)

