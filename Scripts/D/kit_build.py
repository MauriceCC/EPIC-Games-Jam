# -*- coding: utf-8 -*-
"""
Kit modular de arquitectura (Division D). Escribe OBJ en ejes de Unreal:
el importador OBJ de Unreal aplica UE = (x, -y, z), asi que aqui se escribe y_obj = -UE_Y.
Todas las piezas miden 100 cm por eje, con el pivote en el centro de la base: se escalan a medida
y usan materiales de mapeado mundial (no se estiran al escalar).

Cada cara lleva sus propios vertices (sombreado plano); las normales las calcula el importador (con vn explicitas salian invertidas por el cambio de ejes). Con vertices compartidos el
importador suavizaba las normales entre caras y la proyeccion mundial de los materiales se estiraba.
Comprobado en el editor: el orden antihorario visto desde fuera da la cara exterior.

  SM_KIT4_Box        caja (cuerpos, muros, anexos, suelos)
  SM_KIT4_Gable      cubierta a dos aguas: cumbrera paralela al eje Y (fachada mirando a +X)
  SM_KIT4_Mono       cubierta a un agua: alta en -X, baja en +X
  SM_KIT4_Cornice    moldura de alero con vuelo (perfil escalonado), larga en Y
  SM_KIT4_Window     hueco de ventana: marco + cristal hundido (fachada a +X), 2 materiales
Uso: python -I Scripts/D/kit_build.py <carpeta_salida>
"""
import os, sys

NL = chr(10)

def write(path, verts, faces, mats):
    lines = ["# Unscripted D kit_build.py (caras planas)", "mtllib " + os.path.basename(path)[:-4] + ".mtl",
             "vt 0 0", "vt 1 0", "vt 1 1", "vt 0 1"]
    body = []
    vi = 0; ni = 0; cur = None
    for m, idx in sorted(faces, key=lambda q: q[0]):
        p = [verts[i] for i in idx]
        u = [p[1][k] - p[0][k] for k in range(3)]; w = [p[2][k] - p[0][k] for k in range(3)]
        n = (u[1] * w[2] - u[2] * w[1], u[2] * w[0] - u[0] * w[2], u[0] * w[1] - u[1] * w[0])
        l = (n[0] ** 2 + n[1] ** 2 + n[2] ** 2) ** 0.5 or 1
        ni += 1   # sin vn: con vertices por cara el importador calcula normales planas desde el orden de vertices
        base = vi
        for v in p:
            lines.append("v %.3f %.3f %.3f" % (v[0], -v[1], v[2])); vi += 1
        if m != cur:
            body.append("usemtl " + mats[m]); cur = m
        for k in range(1, len(idx) - 1):
            a, b, c = base + 1, base + k + 1, base + k + 2
            body.append("f %d/1 %d/2 %d/3" % (a, b, c))
    with open(path, "w") as f:
        f.write(NL.join(lines + body) + NL)
    with open(path[:-4] + ".mtl", "w") as f:
        f.write(NL.join("newmtl %s%sKd 0.7 0.7 0.7%s" % (m, NL, NL) for m in mats))

def box(x0, x1, y0, y1, z0, z1, base=0, m=0):
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    b = base
    f = [(m, [b+0, b+3, b+2, b+1]), (m, [b+4, b+5, b+6, b+7]), (m, [b+0, b+1, b+5, b+4]),
         (m, [b+1, b+2, b+6, b+5]), (m, [b+2, b+3, b+7, b+6]), (m, [b+3, b+0, b+4, b+7])]
    return v, f

def main(out):
    os.makedirs(out, exist_ok=True)
    v, f = box(-50, 50, -50, 50, 0, 100)
    write(os.path.join(out, "SM_KIT4_Box.obj"), v, f, ["Main"])
    v = [(-50, -50, 0), (50, -50, 0), (50, 50, 0), (-50, 50, 0), (0, -50, 100), (0, 50, 100)]
    f = [(0, [0, 3, 2, 1]), (0, [1, 2, 5, 4]), (0, [3, 0, 4, 5]), (1, [0, 1, 4]), (1, [2, 3, 5])]
    write(os.path.join(out, "SM_KIT4_Gable.obj"), v, f, ["Roof", "Wall"])
    v = [(-50, -50, 0), (50, -50, 0), (50, 50, 0), (-50, 50, 0), (-50, -50, 100), (-50, 50, 100)]
    f = [(0, [0, 3, 2, 1]), (0, [1, 2, 5, 4]), (1, [3, 0, 4, 5]), (1, [0, 1, 4]), (1, [2, 3, 5])]
    write(os.path.join(out, "SM_KIT4_Mono.obj"), v, f, ["Roof", "Wall"])
    verts, faces = [], []
    for (x0, x1, z0, z1) in [(-50, 10, 0, 40), (-50, 30, 40, 70), (-50, 50, 70, 100)]:
        vv, ff = box(x0, x1, -50, 50, z0, z1, base=len(verts)); verts += vv; faces += ff
    write(os.path.join(out, "SM_KIT4_Cornice.obj"), verts, faces, ["Main"])
    verts, faces = [], []
    for (y0, y1, z0, z1) in [(-50, -38, 0, 100), (38, 50, 0, 100), (-38, 38, 0, 10), (-38, 38, 90, 100), (-3, 3, 10, 90), (-38, 38, 47, 53)]:
        vv, ff = box(10, 50, y0, y1, z0, z1, base=len(verts)); verts += vv; faces += ff
    vv, ff = box(-50, 10, -38, 38, 10, 90, base=len(verts), m=1); verts += vv; faces += ff
    write(os.path.join(out, "SM_KIT4_Window.obj"), verts, faces, ["Frame", "Glass"])
    print("ok", sorted(x for x in os.listdir(out) if x.endswith(".obj")))

if __name__ == "__main__":
    main(sys.argv[1])
