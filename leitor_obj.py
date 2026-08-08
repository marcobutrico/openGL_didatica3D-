# leitor_obj.py
class OBJ:
    def __init__(self, filename):
        self.vertices = []
        self.faces = []
        
        try:
            with open(filename, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    values = line.split()
                    if not values:
                        continue
                        
                    # Processa Vértices (v x y z)
                    if values[0] == 'v':
                        v = [float(x) for x in values[1:4]]
                        self.vertices.append(v)
                        
                    # Processa Faces (f v1/vt1/vn1 v2/vt2/vn2 ...)
                    elif values[0] == 'f':
                        face = []
                        for v in values[1:]:
                            # Pega apenas o índice do vértice antes da barra '/'
                            v_index = int(v.split('/')[0])
                            face.append(v_index)
                        self.faces.append(face)
                        
            print(f"Sucesso ao carregar '{filename}': {len(self.vertices)} vértices, {len(self.faces)} faces.")
        except Exception as e:
            print(f"Erro ao ler o arquivo {filename}: {e}")