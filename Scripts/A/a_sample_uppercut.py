"""Sample this baked Mixamo FBX with the Python standard library.
Rejects unsupported transforms; keeps the original FBX intact.
"""
import bisect, json, math, struct, zlib, hashlib
from pathlib import Path
REPO=Path(__file__).resolve().parents[2]

def mul(a,b):
    x,y,z,w=a;X,Y,Z,W=b
    return (w*X+x*W+y*Z-z*Y,w*Y-x*Z+y*W+z*X,w*Z+x*Y-y*X+z*W,w*W-x*X-y*Y-z*Z)
def inv(q):return (-q[0],-q[1],-q[2],q[3])
def rotate(q,v):return mul(mul(q,(*v,0)),inv(q))[:3]
def euler(v):
    qs=[]
    for i,angle in enumerate(v):
        q=[0.,0.,0.,math.cos(math.radians(angle)/2)];q[i]=math.sin(math.radians(angle)/2);qs.append(q)
    return mul(qs[2],mul(qs[1],qs[0]))

def read_fbx(path):
    raw=path.read_bytes();assert struct.unpack_from('<I',raw,23)[0]>=7500
    def node(offset):
        end,count,size,length=struct.unpack_from('<QQQB',raw,offset)
        if not end:return None,offset+25
        offset+=25;name=raw[offset:offset+length].decode();offset+=length;props=[]
        for _ in range(count):
            kind=chr(raw[offset]);offset+=1
            if kind in 'YCFDIL':
                fmt={'Y':'h','C':'?','F':'f','D':'d','I':'i','L':'q'}[kind]
                value=struct.unpack_from('<'+fmt,raw,offset)[0];offset+=struct.calcsize(fmt)
            elif kind in 'SR':
                n=struct.unpack_from('<I',raw,offset)[0];offset+=4;value=raw[offset:offset+n];offset+=n
                if kind=='S':value=value.decode()
            else:
                assert kind in 'fdlibc',kind
                n,encoding,size=struct.unpack_from('<III',raw,offset);offset+=12
                data=raw[offset:offset+size];offset+=size
                if encoding:data=zlib.decompress(data)
                fmt={'f':'f','d':'d','l':'q','i':'i','b':'b','c':'?'}[kind]
                value=list(struct.unpack('<'+str(n)+fmt,data))
            props.append(value)
        children=[]
        while offset<end:
            child,offset=node(offset)
            if child is None:break
            children.append(child)
        return {'name':name,'props':props,'children':children},end
    nodes=[];offset=27
    while True:
        n,offset=node(offset)
        if n is None:return nodes
        nodes.append(n)

def sample():
    path=REPO/'SourceData/A/Uppercut/SurpriseUppercut.fbx'
    nodes=read_fbx(path)
    objects=next(n['children'] for n in nodes if n['name']=='Objects')
    connections=[n['props'] for n in next(n['children'] for n in nodes if n['name']=='Connections')]
    models={n['props'][0]:n for n in objects if n['name']=='Model'}
    curves={n['props'][0]:n for n in objects if n['name']=='AnimationCurve'}
    parents={c[1]:c[2] for c in connections if c[0]=='OO' and c[1] in models}
    def props(n):return {p['props'][0]:p['props'][4:] for x in n['children'] if x['name']=='Properties70' for p in x['children']}
    properties={i:props(n) for i,n in models.items()}
    for p in properties.values():
        assert p.get('RotationOrder',[0])==[0]
        assert p.get('Lcl Scaling',[1.,1.,1.])==[1.,1.,1.]
        for key in ('RotationPivot','RotationOffset','ScalingPivot','ScalingOffset'):
            assert all(abs(x)<1e-6 for x in p.get(key,[0,0,0]))
    names={i:n['props'][1].split('\x00')[0].split(':')[-1] for i,n in models.items()}
    channels={}
    for c in connections:
        if c[0]=='OP' and c[1] in curves:
            owner=next((x for x in connections if x[0]=='OP' and x[1]==c[2] and x[2] in models and x[3] in ('Lcl Rotation','Lcl Translation')),None)
            if owner is None:continue
            fields={x['name']:x['props'][0] for x in curves[c[1]]['children'] if x['props']}
            channels[(owner[2],owner[3],c[3][-1])]=(fields['KeyTime'],fields['KeyValueFloat'])
    def value(i,key,t):
        v=list(properties[i].get(key,[0.,0.,0.]))
        if t is None:return v
        for axis in range(3):
            curve=channels.get((i,key,'XYZ'[axis]))
            if not curve:continue
            times,values=curve;j=max(0,min(len(times)-1,bisect.bisect_right(times,t)-1))
            if j==len(times)-1:v[axis]=values[j]
            else:
                f=(t-times[j])/(times[j+1]-times[j]);v[axis]=values[j]*(1-f)+values[j+1]*f
        return v
    def frame(t):
        world={}
        def solve(i):
            if i in world:return world[i]
            p=properties[i];q=mul(euler(p.get('PreRotation',[0,0,0])),mul(euler(value(i,'Lcl Rotation',t)),inv(euler(p.get('PostRotation',[0,0,0])))))
            v=value(i,'Lcl Translation',t)
            if parents.get(i) in models:
                parent=solve(parents[i]);v=[a+b for a,b in zip(parent['p'],rotate(parent['q'],v))];q=mul(parent['q'],q)
            world[i]={'p':v,'q':q};return world[i]
        result={}
        for i in models:
            v=solve(i);x,y,z,w=v['q'];px,py,pz=v['p']
            result[names[i]]={'p':[-pz,px,py],'q':[z,-x,-y,w]}
        return result
    rest=frame(None);ticks=46186158000
    end=max(max(t) for t,v in channels.values());duration=end/ticks
    data={'source':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'duration':duration,'fps':30,
          'bones':{names[i]:{'parent':names.get(parents.get(i),''),'rest':rest[names[i]]} for i in models},
          'frames':[frame(round(i*ticks/30)) for i in range(round(duration*30)+1)]}
    out=REPO/'SourceData/A/Uppercut/uppercut_samples.json';out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(data,separators=(',',':')),encoding='utf-8')
    print('SAMPLED_UPPERCUT',duration,len(data['frames']))
    return data

if __name__=='__main__':sample()
