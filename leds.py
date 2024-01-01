from machine import Pin
from neopixel import NeoPixel
from time import sleep
import uasyncio

# L1     5 2 1
#        4 3 0

# L2     5 2 1
#        4 3 0

# L3     5 2 1
#        4 3 0

# L4     4 3 0
#        5 2 1

white = (255,255,255)
red   = (255,0,0)
blue  = (0,255,0)
green = (0,0,255)
pink  = (64,128,0)
yellow = (255,0,150)
black = (0,0,0)
all = (1024,1024,1024)

all_on = 0
rotate_left = 1
rotate_right = 2
blink = 2
fade = 3




class LedGlobe46:
    def __init__(self, gpioA, gpioB, gpioC, gpioD):
        self.np = []
        self.np.append(NeoPixel(Pin(gpioA, Pin.OUT), 6))
        self.np.append(NeoPixel(Pin(gpioB, Pin.OUT), 6))
        self.np.append(NeoPixel(Pin(gpioC, Pin.OUT), 6))
        self.np.append(NeoPixel(Pin(gpioD, Pin.OUT), 6))

        self.order_lower = [(0,1), (0,2), (0,5),
                            (1,1), (1,2), (1,5),
                            (2,1), (2,2), (2,5),
                            (3,4), (3,3), (3,0), 
                            ]

        self.order_upper = [(0,0), (0,3), (0,4),
                            (1,0), (1,3), (1,4),
                            (2,0), (2,3), (2,4),
                            (3,5), (3,2), (3,1), 
                            ]


        self.animation_delay = 64
        self.mode = fade

        self.blank()

    def __len__(self):
        return 24
    
    def __getitem__(self, x):
        if x >= (len(self) / 2):
            i , j = self.order_upper[x-12]
        else:
            i , j = self.order_lower[x]
        return self.np[i][j]

    def __setitem__(self, x, val):
        if x >= (len(self) / 2):
            i , j = self.order_upper[x-12]
        else:
            i , j = self.order_lower[x]
        # print("i = {0}, j={1}, val={2}".format(i,j,val))
        self.np[i][j] = val
        self.write()
        
    def write(self):
        for i in range(len(self.np)):
            self.np[i].write()
            
    async def blank(self):
        for i in range(len(self.np)):
            for j in range(len(self.np[0])):
                self.np[i][j] = (0,0,0)
            self.np[i].write()

    # Animations
    async def rotate_on(self, color):
        print("rotate_on: {0}".format(color))
        for x in range(len(self)):
            self[x] = color
            await uasyncio.sleep_ms(self.animation_delay)

    async def rotate(self, color):
        self.all_on(black)
        for x in range(len(self)):
            self[x] = color
            if x > 0: 
                self[x-1] = black
            await uasyncio.sleep_ms(self.animation_delay)
        self.all_on(black)

    async def all_on(self, color):
        print("all_on: {0}".format(color))
        for x in range(len(self)):
            self[x] = color

    async def fade_on(self, color):
        print("fade_on: {0}".format(color))
        for x in range(0, 100, 4):
            color_faded = [int(i * x * 0.01) for i in color]
            await self.all_on(color_faded)
            await uasyncio.sleep_ms(self.animation_delay)
        for x in range(100, 0, -4):
            color_faded = [int(i * x * 0.01) for i in color]
            await self.all_on(color_faded)
            await uasyncio.sleep_ms(self.animation_delay)
            
    async def test_rotate_all(self):
        #while True:
        await self.rotate_on(red)
        await self.rotate_on(blue)
        await self.rotate_on(yellow)
        await self.rotate_on(pink)
        await self.rotate_on(green)
        await self.rotate_on(blue)
        await self.rotate_on(pink)
        # await self.all_on(black)


    async def test_fade_all(self):
        await self.fade_on(red)
        await self.fade_on(blue)
        await self.fade_on(yellow)
        await self.fade_on(pink)
        await self.fade_on(green)
        await self.fade_on(blue)
        await self.fade_on(pink)

# external API

    def faster(self):
        if self.animation_delay >= 2:
            self.animation_delay = int(self.animation_delay / 2)
        else:
            self.animation_delay = 2
            
    def slower(self):
        if self.animation_delay >= 2:
            self.animation_delay = int(self.animation_delay * 2)
        else:
            self.animation_delay = 2

    async def test(self):
        if self.mode == all_on:
            await self.all_on(red)
        elif self.mode == rotate_left:
            await self.test_rotate_all()
        elif self.mode == fade:
            await self.test_fade_all()
#        elif self.mode = blink:
#            await self.test_blink_all()
        
#    async def interprete(self, commands):
#commands='1a2b3c4d'
#>>> for x in range(int(len(commands)/2)):
#...     chunk = commands[(x*2):(x*2+2)]
#...     mode = chunk[0]
#...     color = chunk[1]
#...     print(mode, color)
#... 
            
