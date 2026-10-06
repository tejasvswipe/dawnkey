#!/usr/bin/python3
"""Merge a FreeRouting Specctra session (.ses) into a KiCad .kicad_pcb via pcbnew."""
import os, sys
sys.path.append('/usr/lib/python3/dist-packages')
import pcbnew
from sexpdata import loads, Symbol

folder=os.path.dirname(os.path.abspath(__file__))
board_path=sys.argv[1] if len(sys.argv)>1 else os.path.join(folder,'DawnKey.kicad_pcb')
ses_path=sys.argv[2] if len(sys.argv)>2 else os.path.join(folder,'DawnKey.ses')
out_path=sys.argv[3] if len(sys.argv)>3 else os.path.join(folder,'DawnKey_routed.kicad_pcb')
board=pcbnew.LoadBoard(board_path)
root=loads(open(ses_path,encoding='utf-8').read())

def tag(node):
    return str(node[0]) if isinstance(node,list) and node else ''

def mm_vec(tick_x,tick_y):
    # FreeRouting emits 0.1-µm coordinate units and inverted Y coordinates.
    return pcbnew.VECTOR2I(pcbnew.FromMM(float(tick_x)*0.0001),
                           pcbnew.FromMM(-float(tick_y)*0.0001))

def net_obj(name):
    n=board.FindNet(name)
    if n is None:
        raise RuntimeError('SES references unknown board net '+name)
    return n

routes=next(x for x in root if tag(x)=='routes')
netout=next(x for x in routes if tag(x)=='network_out')
added_tracks=0
added_vias=0
skipped_protected=0
existing_vias=[]
for item in board.GetTracks():
    if isinstance(item,pcbnew.PCB_VIA):
        p=item.GetPosition()
        existing_vias.append((p.x,p.y,item.GetNetCode()))
for entry in netout[1:]:
    if tag(entry)!='net': continue
    net_name=str(entry[1])
    n=net_obj(net_name)
    for item in entry[2:]:
        if tag(item)=='wire':
            path=next((x for x in item if tag(x)=='path'),None)
            if path is None: continue
            # Protected paths were already present as intentional short bridges.
            if any(tag(x)=='type' and len(x)>1 and str(x[1])=='protect' for x in item):
                skipped_protected+=1
                continue
            layer_name=str(path[1]); width_ticks=float(path[2])
            layer=pcbnew.F_Cu if layer_name=='F.Cu' else pcbnew.B_Cu if layer_name=='B.Cu' else None
            if layer is None: raise RuntimeError('Unexpected route layer '+layer_name)
            coords=path[3:]
            if len(coords)<4 or len(coords)%2: continue
            pts=[mm_vec(coords[i],coords[i+1]) for i in range(0,len(coords),2)]
            for a,z in zip(pts[:-1],pts[1:]):
                if a==z: continue
                track=pcbnew.PCB_TRACK(board)
                track.SetStart(a); track.SetEnd(z)
                track.SetLayer(layer)
                track.SetWidth(pcbnew.FromMM(width_ticks*0.0001))
                track.SetNet(n)
                board.Add(track); added_tracks+=1
        elif tag(item)=='via':
            if len(item)<4: continue
            position=mm_vec(item[2],item[3])
            if any(nx==position.x and ny==position.y and nc==n.GetNetCode() for nx,ny,nc in existing_vias):
                continue
            via=pcbnew.PCB_VIA(board)
            via.SetPosition(position)
            via.SetWidth(pcbnew.FromMM(0.6))
            via.SetDrill(pcbnew.FromMM(0.3))
            via.SetLayerPair(pcbnew.F_Cu,pcbnew.B_Cu)
            via.SetViaType(pcbnew.VIATYPE_THROUGH)
            via.SetNet(n)
            board.Add(via); added_vias+=1
            existing_vias.append((position.x,position.y,n.GetNetCode()))

pcbnew.SaveBoard(out_path,board)
print('Imported tracks:',added_tracks,'vias:',added_vias,'protected paths skipped:',skipped_protected)
print('Footprints:',len(list(board.GetFootprints())),'total tracks/vias:',len(list(board.GetTracks())))
print('Wrote',out_path)
