# plano v4: celdas de 2 m; u=Y (este), v=X (norte); marco u -6..66, v -6..60
Z={"I":(12,24,0,8),"P":(6,26,8,22),"C":(26,46,14,18),"h":(34,38,10,14),"A":(46,58,8,22),
   "T":(46,58,22,34),"X":(26,46,22,36),"t":(14,26,24,32),"R":(2,14,22,36),"S":(18,42,36,48),"E":(24,36,48,54)}
def zone(u,v):
    for k,(u0,u1,v0,v1) in Z.items():
        if u0<=u<u1 and v0<=v<v1: return k
    return None
U=range(-6,66,2); V=list(range(-6,60,2))
def storeys(u,v):
    # celda de edificio: mira el espacio jugable mas cercano en cada direccion (<=6 m)
    north=any(zone(u+1,v+1+d) for d in range(2,8,2))   # hay espacio al norte -> este edificio es su lado sur (camara)
    east=any(zone(u+1+d,v+1) for d in range(2,8,2))    # espacio al este -> lado oeste (camara)
    south=any(zone(u+1,v+1-d) for d in range(2,8,2))   # espacio al sur -> lado norte (fondo)
    west=any(zone(u+1-d,v+1) for d in range(2,8,2))
    if north or east: return "1"
    if south or west: return "3"
    return "2"
rows=[]
for v in reversed(V):
    line=""
    for u in U:
        z=zone(u+1,v+1)
        line+= z if z else storeys(u,v)
    rows.append(f"v={v+2:>3} |{line}|")
print("\n".join(rows))
print("       u=-6"+" "*30+"u=66")
