################################ IMPORTS & GLOBALS ################################

import gdsfactory as gf 
from gdsfactory.layers import lyp_to_dataclass

exec(lyp_to_dataclass("/Users/ryanwans/umich/gds_macros/tests/sky130.lyp"))

from structures import *

PATH_TO_PAD_GDSII = "/Users/ryanwans/umich/gds_macros/inductors/umich_pad.gds"

def arr(pads, pitch):
    for i in range(len(pads)):
        pads[i].movex(i*pitch)

################################ DRAWING ########################################

c = gf.Component("InductorTestStructure1")

inductor_width = 250
inductor_padding = 80
pad_width = 40
pad_pitch = 120

calc_pad_length = (pad_pitch*2) + (pad_width)

# Create Inductor
inductor = square_inductor(0, 0, 9.6, 4.1, inductor_width, 25)
inductor = c << inductor
inductor.rotate(270)
inductor.move(((inductor_padding + pad_width), inductor_width+((calc_pad_length-inductor_width)/2)))

# Create Pad Arrays (sphagetti code incoming)
gsg1 = gf.Component("GSGProbePadArray1")
gsg1_pad = [ ]
for i in range(3):
    pad = gf.import_gds(PATH_TO_PAD_GDSII)
    pad.add_port(
        name=f"io_{i}", center=[40, 20], width=40, orientation=0, layer=LAYER.met5drawing
    )
    pad = gsg1 << pad
    pad.movey(pad_pitch*i)
    gsg1_pad.append(pad)

gsg1 = c << gsg1

gsg2 = gf.Component("GSGProbePadArray2")
gsg2_pad = [ ]
for i in range(3):
    pad = gf.import_gds(PATH_TO_PAD_GDSII)
    pad.add_port(
        name=f"io_{i+3}", center=[0, 20], width=40, orientation=180, layer=LAYER.met5drawing
    )
    pad = gsg2 << pad
    pad.movey(pad_pitch*i)
    pad.movex(pad_width + (2*inductor_padding) + inductor_width)
    gsg2_pad.append(pad)

gsg2 = c << gsg2

# Routing
routeInput = gf.routing.get_route_electrical(
    inductor.ports["in"], gsg1_pad[1].ports["io_1"], layer=LAYER.met5drawing, bend="wire_corner", width = 9.6
)
c.add(routeInput.references)
routeOutput = gf.routing.get_route_electrical(
    inductor.ports["out"], gsg2_pad[1].ports["io_4"], layer=LAYER.met4drawing, bend="wire_corner", width = 9.6
)
c.add(routeOutput.references)

c.show()