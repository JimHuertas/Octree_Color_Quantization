from PIL import Image
from octree_color_quantization import OctreeColorQuantizer, Color

def main(bits):
    ##usando la clase Image para poder cargar la imagen en python
    image = Image.open('img/scrim.png')
    pixels = image.load()
    width, height = image.size

    ##Creando el octree
    octree = OctreeColorQuantizer()

    #añadiendo los colores de la imagen al octree
    for j in range(height):
        for i in range(width):
            octree.add_color(Color(*pixels[i, j]))

    #Creando la paleta de acuerdo de n bits, creando una paleta de 2^n cuadriculas
    paleta = octree.make_paleta(bits*bits)
    paleta_img = Image.new('RGB', (bits,bits))
    paleta_pixels = paleta_img.load()
    for i, color in enumerate(paleta):
        #print(type(i))
        #print((int(color.red), int(color.green), int(color.blue)))
        #print(i%16, "  ", i/16)
        paleta_pixels[i%bits, i/bits] = (int(color.red), int(color.green), int(color.blue))

    paleta_img.save('scrim_palette.png')

    #Creando una nueva imagen apartir de la paleta creada
    resultado_img = Image.new('RGB', (width, height))
    out_pixels = resultado_img.load()
    for j in range(height):
        for i in range(width):
            index = octree.get_pos_paleta(Color(*pixels[i, j]))
            color = paleta[index]
            out_pixels[i, j] = (int(color.red), int(color.green), int(color.blue))
    resultado_img.save('scrim_out.png')


main(4)
