
class Color(object):
    """Clase color para poder guardar los datos RGB (RED, GREEN, BLUE)"""
    def __init__(self, red=0, green=0, blue=0):
        self.red = red
        self.green = green
        self.blue = blue

class NodoOctree(object):
    """Clase que representa al nodo del Octree, modificada para que pueda aplicarse el algoritmo de Color Quantizer"""
    def __init__(self, lvl, padre):
        self.color = Color(0, 0, 0)
        self.pixel_count = 0
        self.pos_paleta = 0
        self.hijos = [None for _ in range(8)]

        ##añade un color en el nivel en el que se encuentra
        if lvl < OctreeColorQuantizer.MAX_DEPTH - 1:
            padre.add_nodo_level(lvl, self)

    def es_hoja(self):
        """Revisa si en nodo en cuestion es hoja o no, de"""
        return self.pixel_count > 0

    def get_all_hojas(self):
        """Getter para retornar todos los nodos hojas"""
        hojas = []
        for i in range(8):
            node = self.hijos[i]
            if node:
                if node.es_hoja():
                    hojas.append(node)
                else:
                    hojas.extend(node.get_all_hojas())
        return hojas

    def get_nodes_pixel_count(self):
        """Retorna la suma del recuento de píxeles del nodo y sus hijos"""
        cont = self.pixel_count
        for i in range(8):
            node = self.hijos[i]
            if node:
                cont += node.pixel_count
        return cont

    def add_color(self, color, level, parent):
        """Inserta un nodo(color) al octree"""
        if level >= OctreeColorQuantizer.MAX_DEPTH:
            self.color.red += color.red
            self.color.green += color.green
            self.color.blue += color.blue
            self.pixel_count += 1
            return
        index = self.get_color_index_next_level(color, level)
        if not self.hijos[index]:
            self.hijos[index] = NodoOctree(level, parent)
        self.hijos[index].add_color(color, level + 1, parent)

    def get_pos_paleta(self, color, nivel):
        """Retorna la posicion del color dado en la paleta, recorriendo el octree hasta llegar a un nodo hoja"""
        if self.es_hoja():
            return self.pos_paleta
        pos = self.get_color_index_next_level(color, nivel)
        if self.hijos[pos]:
            return self.hijos[pos].get_pos_paleta(color, nivel+1)
        else:
            # get palette index for a first found child node
            for i in range(8):
                if self.hijos[i]:
                    return self.hijos[i].get_pos_paleta(color, nivel+1)

    def remove_hojas(self):
        """Borra las hojas de un nodo padre y recuenta los píxeles de los 8 nodos hijos al nodo padre"""
        cont = 0
        for i in range(8):
            node = self.hijos[i]
            if node:
                self.color.red += node.color.red
                self.color.green += node.color.green
                self.color.blue += node.color.blue
                self.pixel_count += node.pixel_count
                cont+=1
        return cont-1

    def get_color_index_next_level(self, color, nivel):
        """Retorna la posicion del color dado para el siguiente nivel"""
        pos = 0
        aux = 0x80 >> nivel
        if color.red & aux:
            pos |= 4
        if color.green & aux:
            pos |= 2
        if color.blue & aux:
            pos |= 1
        return pos

    def get_color(self):
        return Color(self.color.red / self.pixel_count, self.color.green / self.pixel_count, self.color.blue / self.pixel_count)

class OctreeColorQuantizer(object):
    """Clase que servira para cuantizar los colores de una imagen"""
    MAX_DEPTH = 8

    def __init__(self):
        self.niveles = {i: [] for i in range(OctreeColorQuantizer.MAX_DEPTH)}
        self.root = NodoOctree(0, self)

    def get_hojas(self):
        """Retorna todo los nodos hoja del octree"""
        return [node for node in self.root.get_all_hojas()]

    def add_nodo_level(self, level, node):
        """Inserta un nodo en un nivel dado"""
        self.niveles[level].append(node)

    def add_color(self, color):
        """Inserta un color en el octree"""
        self.root.add_color(color, 0, self)

    def make_paleta(self, color_count):
        """Hace una paleta de colores con el máximo de colores determinado por color_count"""
        palette = []
        pos_plta = 0
        cont_hoja = len(self.get_hojas())

        ##Reduccion de los nodos
        for lvl in range(OctreeColorQuantizer.MAX_DEPTH - 1, -1, -1):
            if self.niveles[lvl]:
                for nd in self.niveles[lvl]:
                    cont_hoja -= nd.remove_hojas()
                    if cont_hoja <= color_count:
                        break
                if cont_hoja <= color_count:
                    break
                self.niveles[lvl] = []
        
        #Construccion de la paleta
        for nd in self.get_hojas():
            if pos_plta >= color_count:
                break
            if nd.es_hoja():
                palette.append(nd.get_color())
            nd.pos_paleta = pos_plta
            pos_plta += 1
        return palette

    def get_pos_paleta(self, color):
        """Obtiene la pocision del color dado en la paleta"""
        return self.root.get_pos_paleta(color, 0)