# -*- coding: utf-8 -*-
"""
Corrector de GLB de Meshy para la Division D (solo Python estandar).

Hace en el propio archivo lo que no se puede hacer bien por instancia en Unreal:
  - escala real horneada (metros) por eje, con limite de deformacion,
  - origen (pivote) en el centro de la fachada a ras de suelo (casas) o centro de la base (props),
  - orienta la fachada hacia +Z de glTF (que el import de Unreal convierte de forma fija; se verifica tras importar),
  - separa la cubierta (triangulos inclinados por encima del alero) en un segundo material "Roof",
  - elimina texturas incrustadas (los materiales se montan en Unreal).

Uso:
  python -I Scripts/D/glb_fix.py info  <in.glb>
  python -I Scripts/D/glb_fix.py fix   <in.glb> <out.glb> --front +z|-z|+x|-x --size W H D [--pivot front|base]
        [--roof-split EAVE_FRACTION] [--max-stretch 0.10]
     W = ancho de fachada (m), H = alto total (m), D = fondo (m). Si --max-stretch se supera, se avisa y se
     limita la deformacion respecto a la escala media.
"""
import json, math, struct, sys

def read_glb(path):
    data = open(path, "rb").read()
    magic, ver, length = struct.unpack_from("<4sII", data, 0)
    assert magic == b"glTF"
    off = 12; js = None; binc = b""
    while off < length:
        clen, ctype = struct.unpack_from("<I4s", data, off); off += 8
        chunk = data[off:off + clen]; off += clen
        if ctype == b"JSON": js = json.loads(chunk.decode("utf-8"))
        elif ctype == b"BIN\x00": binc = chunk
    return js, binc

CT = {5126: ("f", 4), 5125: ("I", 4), 5123: ("H", 2), 5121: ("B", 1)}
NC = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}

def accessor(js, binc, idx):
    a = js["accessors"][idx]; bv = js["bufferViews"][a["bufferView"]]
    fmt, size = CT[a["componentType"]]; n = NC[a["type"]]
    stride = bv.get("byteStride", size * n)
    base = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
    out = []
    for i in range(a["count"]):
        o = base + i * stride
        out.append(struct.unpack_from("<" + fmt * n, binc, o))
    return out

def load_mesh(js, binc):
    prims = [p for m in js["meshes"] for p in m["primitives"]]
    P, N, UV, I = [], [], [], []
    for p in prims:
        base = len(P)
        P += accessor(js, binc, p["attributes"]["POSITION"])
        N += accessor(js, binc, p["attributes"]["NORMAL"]) if "NORMAL" in p["attributes"] else [(0, 1, 0)] * (len(P) - base)
        UV += accessor(js, binc, p["attributes"]["TEXCOORD_0"]) if "TEXCOORD_0" in p["attributes"] else [(0, 0)] * (len(P) - base)
        I += [base + i[0] for i in accessor(js, binc, p["indices"])]
    # nodo con transform: Meshy suele dejar el nodo sin transform; si tiene matriz/escala se avisa
    for nd in js.get("nodes", []):
        if any(k in nd for k in ("matrix", "scale", "rotation", "translation")):
            print("AVISO: nodo con transform", {k: nd[k] for k in nd if k in ("matrix", "scale", "rotation", "translation")})
    return P, N, UV, I

def bbox(P):
    return [min(p[i] for p in P) for i in range(3)], [max(p[i] for p in P) for i in range(3)]

def detail_side(P):
    """cuenta vertices cerca de cada cara del bbox: la fachada tiene mas relieve (huecos, marcos)"""
    mn, mx = bbox(P); res = {}
    for ax, nm in ((0, "x"), (2, "z")):
        span = mx[ax] - mn[ax]
        for sgn, v in (("-", mn[ax]), ("+", mx[ax])):
            band = [p for p in P if abs(p[ax] - v) < span * 0.06]
            res[sgn + nm] = len(band)
    return res

def write_glb(path, P, N, UV, prims_idx, mat_names):
    def pad(b, ch=b"\x00"):
        return b + ch * ((4 - len(b) % 4) % 4)
    buf = b""; views = []; accs = []
    def add_view(raw, target=None):
        nonlocal buf
        off = len(buf); buf = pad(buf + raw)
        v = {"buffer": 0, "byteOffset": off, "byteLength": len(raw)}
        if target: v["target"] = target
        views.append(v); return len(views) - 1
    mn, mx = bbox(P)
    vp = add_view(b"".join(struct.pack("<3f", *p) for p in P), 34962)
    accs.append({"bufferView": vp, "componentType": 5126, "count": len(P), "type": "VEC3", "min": mn, "max": mx})
    vn = add_view(b"".join(struct.pack("<3f", *n) for n in N), 34962)
    accs.append({"bufferView": vn, "componentType": 5126, "count": len(N), "type": "VEC3"})
    vu = add_view(b"".join(struct.pack("<2f", *u) for u in UV), 34962)
    accs.append({"bufferView": vu, "componentType": 5126, "count": len(UV), "type": "VEC2"})
    prims = []
    for k, idx in enumerate(prims_idx):
        if not idx: continue
        vi = add_view(b"".join(struct.pack("<I", i) for i in idx), 34963)
        accs.append({"bufferView": vi, "componentType": 5125, "count": len(idx), "type": "SCALAR"})
        prims.append({"attributes": {"POSITION": 0, "NORMAL": 1, "TEXCOORD_0": 2}, "indices": len(accs) - 1, "material": k})
    js = {"asset": {"version": "2.0", "generator": "Unscripted D glb_fix.py"}, "scene": 0, "scenes": [{"nodes": [0]}],
          "nodes": [{"mesh": 0, "name": "root"}], "meshes": [{"primitives": prims, "name": "mesh"}],
          "materials": [{"name": n, "pbrMetallicRoughness": {"metallicFactor": 0, "roughnessFactor": 0.8}} for n in mat_names],
          "buffers": [{"byteLength": len(buf)}], "bufferViews": views, "accessors": accs}
    jb = pad(json.dumps(js).encode("utf-8"), b" ")
    total = 12 + 8 + len(jb) + 8 + len(buf)
    with open(path, "wb") as f:
        f.write(struct.pack("<4sII", b"glTF", 2, total))
        f.write(struct.pack("<I4s", len(jb), b"JSON")); f.write(jb)
        f.write(struct.pack("<I4s", len(buf), b"BIN\x00")); f.write(buf)

def write_obj(path, P, N, UV, prims_idx, mat_names):
    """OBJ en centimetros (1 unidad = 1 cm en Unreal), Y arriba como glTF; UV con V invertida (convencion OBJ)."""
    import os
    mtl = os.path.splitext(path)[0] + ".mtl"
    with open(mtl, "w") as f:
        for n in mat_names:
            f.write("newmtl %s\nKd 0.8 0.8 0.8\n\n" % n)
    with open(path, "w") as f:
        f.write("# Unscripted D glb_fix.py\nmtllib %s\no mesh\n" % os.path.basename(mtl))
        # El import OBJ de Unreal usa UE_X = x, UE_Y = -y, UE_Z = z. Se escribe (z, x, y) de glTF para obtener
        # fachada hacia +X de Unreal, anchura en Y y altura en Z (permutacion ciclica: conserva el sentido de las caras).
        f.write("".join("v %.4f %.4f %.4f\n" % (p[2] * 100, p[0] * 100, p[1] * 100) for p in P))
        f.write("".join("vt %.6f %.6f\n" % (u[0], 1.0 - u[1]) for u in UV))
        f.write("".join("vn %.5f %.5f %.5f\n" % (n[2], n[0], n[1]) for n in N))
        for k, idx in enumerate(prims_idx):
            if not idx: continue
            f.write("usemtl %s\n" % mat_names[k])
            for t in range(0, len(idx), 3):
                a, b, c = idx[t] + 1, idx[t + 1] + 1, idx[t + 2] + 1
                f.write("f %d/%d/%d %d/%d/%d %d/%d/%d\n" % (a, a, a, b, b, b, c, c, c))

def fix(inp, out, front, W, H, D, pivot="front", roof_split=None, max_stretch=0.10, drop_roof=False):
    js, binc = read_glb(inp)
    P, N, UV, I = load_mesh(js, binc)
    # 1. orientar: girar alrededor de Y para que la fachada mire a +Z
    rot = {"+z": 0, "-z": 180, "+x": -90, "-x": 90}[front]
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    def ry(v): return (c * v[0] + s * v[2], v[1], -s * v[0] + c * v[2])
    P = [ry(p) for p in P]; N = [ry(n) for n in N]
    mn, mx = bbox(P)
    size = [mx[i] - mn[i] for i in range(3)]          # x = ancho, y = alto, z = fondo
    want = [W, H, D]
    sc = [want[i] / size[i] for i in range(3)]
    mean = sum(sc) / 3.0
    clamp = []
    for i in range(3):
        lo, hi = mean * (1 - max_stretch), mean * (1 + max_stretch)
        if not (lo <= sc[i] <= hi):
            clamp.append(("xyz"[i], round(sc[i] / mean - 1, 3)))
            sc[i] = min(max(sc[i], lo), hi)
    # 2. escala + pivote
    if pivot == "front":   # centro de la fachada (z = max) a ras de suelo
        ox, oy, oz = (mn[0] + mx[0]) / 2, mn[1], mx[2]
    else:                  # centro de la base
        ox, oy, oz = (mn[0] + mx[0]) / 2, mn[1], (mn[2] + mx[2]) / 2
    P = [((p[0] - ox) * sc[0], (p[1] - oy) * sc[1], (p[2] - oz) * sc[2]) for p in P]
    def nn(n):
        v = (n[0] / sc[0], n[1] / sc[1], n[2] / sc[2]); l = math.sqrt(sum(a * a for a in v)) or 1
        return tuple(a / l for a in v)
    N = [nn(n) for n in N]
    # 3. separar cubierta
    facade, roof = [], []
    if roof_split:
        hmax = max(p[1] for p in P); eave = hmax * roof_split
        for t in range(0, len(I), 3):
            a, b, cc = P[I[t]], P[I[t + 1]], P[I[t + 2]]
            u = [b[k] - a[k] for k in range(3)]; v = [cc[k] - a[k] for k in range(3)]
            nrm = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
            l = math.sqrt(sum(x * x for x in nrm)) or 1
            cy = (a[1] + b[1] + cc[1]) / 3
            ny = abs(nrm[1]) / l
            is_roof = cy > eave and (0.35 < ny < 0.97 if drop_roof else ny > 0.35)
            (roof if is_roof else facade).extend(I[t:t + 3])
        if drop_roof:
            roof = []   # la cubierta la pone el kit (SM_KIT_Gable) sobre toda la parcela
    else:
        facade = I
    if out.lower().endswith(".obj"):
        write_obj(out, P, N, UV, [facade, roof], ["Facade", "Roof"])
    else:
        write_glb(out, P, N, UV, [facade, roof], ["Facade", "Roof"])
    mn2, mx2 = bbox(P)
    return {"scale": [round(x, 4) for x in sc], "clamped": clamp, "bbox_min": [round(x, 3) for x in mn2],
            "bbox_max": [round(x, 3) for x in mx2], "tris_facade": len(facade) // 3, "tris_roof": len(roof) // 3}

if __name__ == "__main__":
    a = sys.argv
    if a[1] == "info":
        js, binc = read_glb(a[2]); P, N, UV, I = load_mesh(js, binc)
        mn, mx = bbox(P)
        print("verts", len(P), "tris", len(I) // 3, "min", [round(x, 3) for x in mn], "max", [round(x, 3) for x in mx])
        print("detalle por cara", detail_side(P))
        # perfil de altura: anchura de la seccion por franjas para localizar el alero
        h0, h1 = mn[1], mx[1]
        for k in range(10):
            y0 = h0 + (h1 - h0) * k / 10; y1 = h0 + (h1 - h0) * (k + 1) / 10
            band = [p for p in P if y0 <= p[1] < y1]
            if band:
                print("franja %.2f-%.2f  x %.3f..%.3f  z %.3f..%.3f  n=%d" % (y0, y1, min(p[0] for p in band), max(p[0] for p in band), min(p[2] for p in band), max(p[2] for p in band), len(band)))
    else:
        args = dict(zip(a[4::2], a[5::2])) if False else None
        front = a[a.index("--front") + 1]
        i = a.index("--size"); W, H, D = float(a[i + 1]), float(a[i + 2]), float(a[i + 3])
        pivot = a[a.index("--pivot") + 1] if "--pivot" in a else "front"
        rs = float(a[a.index("--roof-split") + 1]) if "--roof-split" in a else None
        ms = float(a[a.index("--max-stretch") + 1]) if "--max-stretch" in a else 0.10
        print(json.dumps(fix(a[2], a[3], front, W, H, D, pivot, rs, ms, "--drop-roof" in a)))
