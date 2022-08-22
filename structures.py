################################ IMPORTS & GLOBALS ################################

import gdsfactory as gf 
from gdsfactory.layers import lyp_to_dataclass

exec(lyp_to_dataclass("/Users/ryanwans/umich/gds_macros/tests/sky130.lyp"))

PATH_TO_PAD_GDSII = "/Users/ryanwans/umich/gds_macros/inductors/umich_pad.gds"

################################ CELLS ########################################

@gf.cell
def pad(length=100):
    PAD = gf.Component(f"pad_{length}")
    PAD.add_polygon([(0,0), (length, 0), (length, length), (0, length)], layer=LAYER.met5drawing)
    PAD.add_polygon([(0,0), (length, 0), (length, length), (0, length)], layer=LAYER.paddrawing)
    PAD.add_port(
        name="io", center=[length/2, length], width=length, orientation=90, layer=LAYER.met5drawing
    )
    return PAD

@gf.cell
def square_inductor(originx, originy, width, inspace, outwidth, linseg):
    INDUCTOR = gf.Component(f"square_inductor_{width}")
    direction = 1
    linedel = 0
    x = originx
    y = originy
    # Define some basic functionality
    def create_matrix(corner, origin, width):
        output = [ ] 
        dy = 0
        dx = 0
        if corner == "tl":
            for i in range(width * width):
                output.append(((origin[0] + (1.6 * dx)), (origin[1] - (1.6 * dy))))
                dx += 1 
                if (dx == width):
                    dx = 0
                    dy += 1
        elif corner == "tr":
            for i in range(width * width):
                output.append(((origin[0] - (1.6 * dx)), (origin[1] - (1.6 * dy))))
                dx += 1 
                if (dx == width):
                    dx = 0
                    dy += 1
        elif corner == "bl":
            for i in range(width * width):
                output.append(((origin[0] + (1.6 * dx)), (origin[1] + (1.6 * dy))))
                dx += 1 
                if (dx == width):
                    dx = 0
                    dy += 1
        elif corner == "br":
            for i in range(width * width):
                output.append(((origin[0] - (1.6 * dx)), (origin[1] + (1.6 * dy))))
                dx += 1 
                if (dx == width):
                    dx = 0
                    dy += 1
        else:
            raise Exception("corner not supported")
        return output
    def rect(w,l,ox,oy,m,d):
        d.add_polygon([(ox, oy), (ox+w, oy), (ox+w, oy+l), (ox, oy+l)], layer=m)
    def calclinedel(it, w, s):
        if (it == 0):
            return w
        elif (it%2 == 0):
            return w+s
        else:
            return 0
    i = 0
    p = 0
    savedx = originx
    savedy = originy
    operation = 1
    # Draw the inductor
    while i < linseg:
        # print(f"i = {i} and p = {p} and operation = {operation}")
        if direction:
            rect(width, operation*(outwidth - linedel), x, y, LAYER.met5drawing, INDUCTOR)
            if operation == -1:
                y = y - (outwidth - linedel)
            else:
                y = y + (outwidth - linedel - width)
                x = x + (width)
            direction = 0
            linedel = linedel + calclinedel(i, width, inspace)
        else:
            rect(operation*(outwidth - linedel), width, x, y, LAYER.met5drawing, INDUCTOR)
            if operation == -1:
                y = y + (width)
                x = x + ((outwidth - linedel - width))
            else:
                y = y
                x = x + ((outwidth - linedel - width))
            if (p == 3):
                x = savedx + width + inspace
                if (i == 3):
                    y = savedy + width
                else:
                    y = savedy + width + inspace
                savedy = y
                savedx = x
            direction = 1
            linedel = linedel + calclinedel(i, width, inspace)
        i = i + 1
        p = p + 1
        x = round(x, 2)
        y = round(y, 2)
        if(p == 2):
            operation = -1
        elif(p == 4):
            p = 0
            operation = 1
    grid = int((width+0.01)/1.6)
    print(p, (x, y))
    cen = (x, y)
    orie = 0
    if (grid < 1):
        raise Exception("width must be larger than 1.6 microns")
    if (p==1):
        cord = create_matrix("br", (x, y), grid)
        for i in range(len(cord)):
            via = gf.components.via(size=[0.8, 0.8], spacing=[1.6, 1.6], enclosure=0.4, layer=LAYER.via4drawing, bbox_offset=0)
            via = INDUCTOR << via
            via.move((round((cord[i][0]-0.8), 2), round((cord[i][1]+0.8), 2)))
            cen = ((x-(width/2)), y)
    elif (p==0):
        cord = create_matrix("tl", (x, y), grid)
        for i in range(len(cord)):
            via = gf.components.via(size=[0.8, 0.8], spacing=[1.6, 1.6], enclosure=0.4, layer=LAYER.via4drawing, bbox_offset=0)
            via = INDUCTOR << via
            via.move((round((cord[i][0]+0.8), 2), round((cord[i][1]-0.8), 2)))
            cen = (x+width, (y-(width/2)))
    elif (p==2):
        cord = create_matrix("bl", (x, y), grid)
        for i in range(len(cord)):
            via = gf.components.via(size=[0.8, 0.8], spacing=[1.6, 1.6], enclosure=0.4, layer=LAYER.via4drawing, bbox_offset=0)
            via = INDUCTOR << via
            via.move((round((cord[i][0]+0.8), 2), round((cord[i][1]+0.8), 2)))
            cen = (x+width, (y+(width/2)))
    elif (p==3):
        cord = create_matrix("bl", (x, y), grid)
        for i in range(len(cord)):
            via = gf.components.via(size=[0.8, 0.8], spacing=[1.6, 1.6], enclosure=0.4, layer=LAYER.via4drawing, bbox_offset=0)
            via = INDUCTOR << via
            via.move((round((cord[i][0]+0.8), 2), round((cord[i][1]+0.8), 2)))
            cen = ((x+(width/2)), y+width)
    INDUCTOR.add_port(
        name="in", center=[width/2,originy], width=width, orientation=270, layer=LAYER.met5drawing
    )
    INDUCTOR.add_port(
        name="out", center=[cen[0], cen[1]], width=width, orientation=90, layer=LAYER.met4drawing
    )
    return INDUCTOR

@gf.cell
def umich_pad():
    PAD = gf.Component("PAD")
    GDS = gf.import_gds(gdspath=PATH_TO_PAD_GDSII)
    GDS.add_port(
        name="io", center=[20, 40], width=40, orientation=90, layer=LAYER.met5drawing
    )
    GDS = PAD << GDS 
    return PAD