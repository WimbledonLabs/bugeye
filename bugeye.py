from PIL import Image
import argparse
from math import sqrt, sin, cos, pi

parser = argparse.ArgumentParser(description="Convert to grid of hexagons")
parser.add_argument("src_name", help="name of the source file")
parser.add_argument("dest_name", help="name of the destination file")
parser.add_argument("--count", type=float, default=20,
                    help="number of horizontal hexagons in output")
parser.add_argument("--angle", type=float, default=0,
                    help="clockwise angle adjustment of the output grid in "
                    "degrees")
parser.add_argument("--xOffset", type=int, default=0,
                    help="right shift of the output grid")
parser.add_argument("--yOffset", type=int, default=0,
                    help="down shift of the output grid")

# Algorithms used are explained at http://www.redblobgames.com/grids/hexagons/
def pixelToHex(x, y, size):
    q = x * 2.0/3.0
    r = (-x / 3.0 + sqrt(3.0)/3.0 * y)
    return cubeRound( axialToCube( (q/size, r/size) ) )

def axialToCube(qr):
    x = qr[0]
    z = qr[1]
    y = -x - z
    return (x, y, z)

def cubeRound(xyz):
    rx = round(xyz[0])
    ry = round(xyz[1])
    rz = round(xyz[2])

    xd = abs(rx - xyz[0])
    yd = abs(ry - xyz[1])
    zd = abs(rz - xyz[2])

    if xd > yd and xd > zd:
        rx = -ry - rz
    elif yd > zd:
        ry = -rx - rz
    else:
        rz = -rx - ry

    return (rx, ry, rz)

def convertToHexBitmap(im, args):
    px = im.load()
    hexSize = im.size[0] / float(args.count) / sqrt(3)
    angle = args.angle * pi / 180.0
    hexes = {}

    # Assign each src pixel to the correct hexagon
    for x in range(im.size[0]):
        for y in range(im.size[1]):
            dx = x - args.xOffset
            dy = y - args.yOffset
            hexNum = pixelToHex(dx*cos(angle) + dy*sin(angle),
                                dy*cos(angle) - dx*sin(angle),
                                hexSize)
            hexes.setdefault(hexNum, [])
            hexes[hexNum].append(px[x,y])

    # Average the pixel colors in each hexagon
    for hexNum, pixels in hexes.items():
        colorSum = [0,0,0]
        for p in pixels:
            # Is there a way to do this element-wise?
            colorSum[0] += p[0]
            colorSum[1] += p[1]
            colorSum[2] += p[2]

        colorSum[0] = round(colorSum[0] / len(pixels))
        colorSum[1] = round(colorSum[1] / len(pixels))
        colorSum[2] = round(colorSum[2] / len(pixels))

        hexes[hexNum] = colorSum

    # Assign the averaged color values back to the bitmap
    for x in range(im.size[0]):
        for y in range(im.size[1]):
            dx = x - args.xOffset
            dy = y - args.yOffset
            hexNum = pixelToHex(dx*cos(angle) + dy*sin(angle),
                                dy*cos(angle) - dx*sin(angle),
                                hexSize)
            px[x,y] = tuple(hexes[hexNum])

    return px

if __name__ == "__main__":
    args = parser.parse_args();
    im = Image.open(args.src_name)
    convertToHexBitmap(im, args)
    im.save(args.dest_name)
