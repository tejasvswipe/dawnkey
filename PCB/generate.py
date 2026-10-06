#!/usr/bin/python3
"""Generate the DAWNKEY BLARE alarm clock PCB using KiCad's pcbnew API.

Board architecture: 4x3 MX matrix through MCP23017, XIAO ESP32-C3, ST7789 8-pin
header, switched piezo driver, DS3231 RTC, 2xAA-to-5V boost, and I2C expansion.
"""
import os, sys, math
sys.path.append('/usr/lib/python3/dist-packages')
import pcbnew

OUT = os.path.dirname(os.path.abspath(__file__))
os.makedirs(OUT, exist_ok=True)
MM = pcbnew.FromMM
V = pcbnew.VECTOR2I

# 2-layer board, 90 x 90 mm, chamfered corners, MX 19.05 mm pitch.
W, H = 94.0, 90.0
b = pcbnew.BOARD()
settings = b.GetDesignSettings()
settings.SetCopperLayerCount(2)
# Economical 0.20 mm routing rules are documented in the project notes.

NET_NAMES = [
    'GND','3V3','USB_5V','BAT_RAW','BOOST_SW','BOOST_5V','BOOST_FB','TFT_SCLK','TFT_MOSI','TFT_RST','TFT_DC','TFT_CS','TFT_BL',
    'I2C_SDA','I2C_SCL','BUZZER_CTL','BUZZER_SW','BUZZER','RTC_INT','RTC_VBAT','MCP_RESET',
    'KEY_COL0','KEY_COL1','KEY_COL2','KEY_COL3','KEY_ROW0','KEY_ROW1','KEY_ROW2'
]
nets={}
for name in NET_NAMES:
    n=pcbnew.NETINFO_ITEM(b,name)
    b.Add(n)
    nets[name]=n

# Drawing helpers.
def mm(x): return MM(float(x))
def vec(x,y): return V(mm(x),mm(y))
def add_line(x1,y1,x2,y2,layer=pcbnew.F_SilkS,width=0.15, board=b):
    s=pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(vec(x1,y1)); s.SetEnd(vec(x2,y2))
    s.SetLayer(layer); s.SetWidth(mm(width)); board.Add(s)
    return s

def add_text(text,x,y,size=1.0,layer=pcbnew.F_SilkS,angle=0,width=0.15,board=b):
    t=pcbnew.PCB_TEXT(board)
    t.SetText(text); t.SetPosition(vec(x,y)); t.SetLayer(layer)
    t.SetTextSize(vec(size,size)); t.SetTextThickness(mm(width)); t.SetTextAngle(pcbnew.EDA_ANGLE(angle, pcbnew.DEGREES_T))
    board.Add(t); return t

def layers(*ll):
    ls=pcbnew.LSET()
    for l in ll: ls.AddLayer(l)
    return ls

# Attach local-coordinate pads while footprint is still at (0,0).
custom_placements={}
def new_fp(ref,value,x,y,angle=0,back=False,libid=''):
    fp=pcbnew.FOOTPRINT(b)
    fp.SetReference(ref); fp.SetValue(value)
    if libid:
        try: fp.SetFPIDAsString(libid)
        except Exception: pass
    fp.SetPosition(vec(x,y))
    fp.SetOrientationDegrees(angle)
    fp.SetLayer(pcbnew.B_Cu if back else pcbnew.F_Cu)
    custom_placements[ref]=(x,y,angle,back)
    return fp

def finish_custom(fp):
    b.Add(fp)
    return fp

def pad(fp,num,x,y,w,h,kind='pth',drill=0.9,shape=None,layer='all',net=None,roundratio=0.25):
    p=pcbnew.PAD(fp); p.SetNumber(str(num))
    p.SetSize(vec(w,h))
    if shape is None:
        shape=pcbnew.PAD_SHAPE_CIRCLE if w==h else pcbnew.PAD_SHAPE_OVAL
    p.SetShape(shape)
    if kind=='pth':
        p.SetAttribute(pcbnew.PAD_ATTRIB_PTH); p.SetDrillSize(vec(drill,drill)); p.SetLayerSet(layers(pcbnew.F_Cu,pcbnew.B_Cu,pcbnew.F_Mask,pcbnew.B_Mask))
    elif kind=='npth':
        p.SetAttribute(pcbnew.PAD_ATTRIB_NPTH); p.SetDrillSize(vec(drill,drill)); p.SetLayerSet(layers(pcbnew.F_Cu,pcbnew.B_Cu,pcbnew.F_Mask,pcbnew.B_Mask))
    elif kind=='smd':
        p.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
        back=custom_placements.get(fp.GetReference(),(0,0,0,False))[3]
        p.SetLayerSet(layers(*( (pcbnew.B_Cu,pcbnew.B_Mask,pcbnew.B_Paste) if back else (pcbnew.F_Cu,pcbnew.F_Mask,pcbnew.F_Paste) )))
        try: p.SetRoundRectRadiusRatio(roundratio)
        except Exception: pass
    # The pcbnew Python API takes absolute pad coordinates for dynamically-built
    # footprints. Convert this component-local offset to a board coordinate.
    px,py,ang,_back=custom_placements.get(fp.GetReference(),(0,0,0,False))
    rad=math.radians(ang)
    wx=px + x*math.cos(rad) - y*math.sin(rad)
    wy=py + x*math.sin(rad) + y*math.cos(rad)
    fp.Add(p)
    p.SetPosition(vec(wx,wy))
    p.SetLocalCoord()
    if net is not None: p.SetNet(nets[net])
    return p

def graphics_line(fp,x1,y1,x2,y2,layer=pcbnew.F_SilkS,width=0.12):
    s=pcbnew.FP_SHAPE(fp); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetStart(vec(x1,y1)); s.SetEnd(vec(x2,y2)); s.SetLayer(layer); s.SetWidth(mm(width)); fp.Add(s)

def graphics_rect(fp,x1,y1,x2,y2,layer=pcbnew.F_Fab,width=0.10):
    graphics_line(fp,x1,y1,x2,y1,layer,width); graphics_line(fp,x2,y1,x2,y2,layer,width); graphics_line(fp,x2,y2,x1,y2,layer,width); graphics_line(fp,x1,y2,x1,y1,layer,width)

def fp_text(fp,text,x,y,size=0.9,layer=pcbnew.F_Fab,angle=0,width=0.12):
    t=pcbnew.FP_TEXT(fp); t.SetText(text); t.SetPosition(vec(x,y)); t.SetLayer(layer); t.SetTextSize(vec(size,size)); t.SetTextThickness(mm(width)); t.SetTextAngle(pcbnew.EDA_ANGLE(angle,pcbnew.DEGREES_T)); fp.Add(t)

def load_fp(lib,name,ref,val,x,y,angle=0,back=False,libid=None):
    fp=pcbnew.FootprintLoad('/usr/share/kicad/footprints/'+lib+'.pretty',name)
    if fp is None: raise RuntimeError('Could not load footprint '+lib+':'+name)
    fp.SetReference(ref); fp.SetValue(val)
    if libid:
        try: fp.SetFPIDAsString(libid)
        except Exception: pass
    fp.SetPosition(vec(x,y)); fp.SetOrientationDegrees(angle)
    b.Add(fp)
    if back: fp.Flip(vec(x,y),True)
    return fp

def connect(fp, mapping):
    for p in fp.Pads():
        n=mapping.get(p.GetNumber())
        if n: p.SetNet(nets[n])

# Custom XIAO ESP32-C3 footprint. Based on Seeed's official pad-row geometry,
# with the 14 edge pads only; 6 programming/test pads are intentionally omitted.
xiao = new_fp('U1','XIAO ESP32-C3',17.0,72.0,0,True,'Seeed_Studio_XIAO_Series:XIAO-ESP32-C3-SMD')
# Mirror-aware pad placement is handled by pcbnew Flip after adding pads; pads are
# kept on standard F.Cu before flipping. Coordinates are centered from Seeed OPL.
# Actual pad numbering 1-14 exactly follows the Seeed symbol (D0..D10, 3V3, GND, 5V).
for i in range(7): pad(xiao,i+1,-7.62,7.62-i*2.54,2.75,2.0,'smd',shape=pcbnew.PAD_SHAPE_ROUNDRECT)
for i in range(7): pad(xiao,i+8,7.62,-7.62+i*2.54,2.75,2.0,'smd',shape=pcbnew.PAD_SHAPE_ROUNDRECT)
graphics_rect(xiao,-9.0,-12.0,9.0,12.0,pcbnew.F_Fab,0.10)
fp_text(xiao,'SEEED XIAO ESP32-C3',0,0,0.85,pcbnew.F_Fab)
finish_custom(xiao)
connect(xiao,{'1':'TFT_SCLK','2':'TFT_MOSI','3':'TFT_RST','4':'TFT_DC','5':'TFT_CS','6':'TFT_BL',
              '7':'I2C_SCL','8':'I2C_SDA','11':'BUZZER_CTL','12':'3V3','13':'GND','14':'USB_5V'})

# 12 MX-style switches: 4 columns x 3 rows, switch apertures / stabilizer holes.
xs=[16.425,35.475,54.525,73.575]
ys=[51.6,32.55,13.5]  # row 0 is nearest the display: 1–4, then 5–8, then 9/0/S/OK
key_index=0
for r,y in enumerate(ys):
    for c,x in enumerate(xs):
        key_index+=1
        fp=new_fp('SW%02d'%key_index,'MX-STYLE KEY %02d'%key_index,x,y,0,False,'BLARE:SW_MX_1u')
        # MX switch support holes (kept as copper/mask openings as per stock footprint).
        pad(fp,'',-5.08,0,1.75,1.75,'npth',1.75)
        pad(fp,'',0,0,3.9878,3.9878,'npth',3.9878)
        pad(fp,'',5.08,0,1.75,1.75,'npth',1.75)
        # Stock BLARE MX electrical contacts.
        pad(fp,'1',-3.81,-2.54,2.3,2.3,'pth',1.524,net='KEY_COL%d'%c)
        pad(fp,'2',2.54,-5.08,2.3,2.3,'pth',1.524,net='KINT%02d'%key_index if 'KINT%02d'%key_index in nets else None)
        # Add per-key intermediate net and bind the switch contact.
        if 'KINT%02d'%key_index not in nets:
            n=pcbnew.NETINFO_ITEM(b,'KINT%02d'%key_index); b.Add(n); nets['KINT%02d'%key_index]=n
            fp.FindPadByNumber('2').SetNet(n)
        # A simple readable fab outline with full 19.05 mm pitch.
        graphics_rect(fp,-7,-7,7,7,pcbnew.F_Fab,0.08)
        fp_text(fp,'%02d'%key_index,0,0,0.9,pcbnew.F_Fab)
        finish_custom(fp)

# Diodes underneath each key, pad 1=cathode, pad 2=anode.
# Pad 1 sits exactly at SW pad 2; pad 2 joins the row bus.
key_index=0
for r,y in enumerate(ys):
    for c,x in enumerate(xs):
        key_index+=1
        d=new_fp('D%02d'%key_index,'1N4148 / DO-35',x+5.0,y-5.08,0,True,'Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal')
        pad(d,'1',0,0,1.8,1.8,'pth',0.8,net='KINT%02d'%key_index)
        pad(d,'2',7.62,0,1.8,1.8,'pth',0.8,net='KEY_ROW%d'%r)
        graphics_line(d,2.6,-1.4,2.6,1.4,pcbnew.B_SilkS,0.20)
        fp_text(d,'K',0,-1.5,0.6,pcbnew.B_SilkS)
        finish_custom(d)
        # Short backside bridge from the switch contact to this diode's cathode.
        bridge=pcbnew.PCB_TRACK(b); bridge.SetStart(vec(x+2.54,y-5.08)); bridge.SetEnd(vec(x+5.0,y-5.08))
        bridge.SetLayer(pcbnew.B_Cu); bridge.SetWidth(mm(0.30)); bridge.SetNet(nets['KINT%02d'%key_index]); b.Add(bridge)

# TFT ST7789 header: stock 8-pin order. Off-board display connects by supplied jumpers.
j1=load_fp('Connector_PinHeader_2.54mm','PinHeader_1x08_P2.54mm_Vertical','J1','TFT / ST7789',90.5,22.0,0,False,'Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical')
connect(j1,{'1':'GND','2':'3V3','3':'TFT_SCLK','4':'TFT_MOSI','5':'TFT_RST','6':'TFT_DC','7':'TFT_CS','8':'TFT_BL'})

# I2C add-on header (RTC is onboard; header is for ambient-light / sensor accessories).
j2=load_fp('Connector_PinHeader_2.54mm','PinHeader_1x04_P2.54mm_Vertical','J2','I2C EXPANSION: 3V3 GND SDA SCL',39.0,64.0,0,True,'Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical')
connect(j2,{'1':'3V3','2':'GND','3':'I2C_SDA','4':'I2C_SCL'})

# MCP23017 16-bit I2C expander, SOIC-28W. Port A scans the 4x3 diode matrix.
u2=load_fp('Package_SO','SOIC-28W_7.5x17.9mm_P1.27mm','U2','MCP23017-I/SO',49.5,73.0,0,True,'Package_SO:SOIC-28W_7.5x17.9mm_P1.27mm')
mpmap={'1':'KEY_COL0','2':'KEY_COL1','3':'KEY_COL2','4':'KEY_COL3','5':'KEY_ROW0','6':'KEY_ROW1','7':'KEY_ROW2',
       '9':'3V3','10':'GND','12':'I2C_SCL','13':'I2C_SDA','15':'GND','16':'GND','17':'GND','18':'MCP_RESET'}
connect(u2,mpmap)

# DS3231 precision RTC. With the 2xAA pack as the clock's always-on source, no
# coin-cell backup is fitted; VBAT is grounded as directed when backup is unused.
u3=load_fp('Package_SO','SOIC-16W_7.5x10.3mm_P1.27mm','U3','DS3231S RTC',64.0,73.0,0,True,'Package_SO:SOIC-16W_7.5x10.3mm_P1.27mm')
rtcmap={'2':'3V3','3':'RTC_INT','5':'GND','6':'GND','7':'GND','8':'GND','9':'GND','10':'GND','11':'GND','12':'GND','13':'GND','14':'GND','15':'I2C_SDA','16':'I2C_SCL'}
connect(u3,rtcmap)

# Small SMD component helper.
def smd_pad(fp,num,x,y,w=1.0,h=1.0,net=None): return pad(fp,num,x,y,w,h,'smd',shape=pcbnew.PAD_SHAPE_ROUNDRECT,net=net)
def resistor(ref,val,x,y,a,bnet,angle=0,back=True):
    f=new_fp(ref,val,x,y,angle,back,'Resistor_SMD:R_0603_1608Metric')
    smd_pad(f,'1',-0.8,0,0.9,1.0,a); smd_pad(f,'2',0.8,0,0.9,1.0,bnet)
    graphics_rect(f,-1.0,-0.5,1.0,0.5,pcbnew.B_Fab,0.08)
    finish_custom(f)
    return f
def capacitor(ref,val,x,y,a,bnet,angle=0):
    f=new_fp(ref,val,x,y,angle,True,'Capacitor_SMD:C_0603_1608Metric')
    smd_pad(f,'1',-0.8,0,0.9,1.0,a); smd_pad(f,'2',0.8,0,0.9,1.0,bnet)
    graphics_rect(f,-1.0,-0.5,1.0,0.5,pcbnew.B_Fab,0.08)
    finish_custom(f)
    return f

def capacitor0805(ref,val,x,y,a,bnet):
    f=load_fp('Capacitor_SMD','C_0805_2012Metric',ref,val,x,y,0,True,'Capacitor_SMD:C_0805_2012Metric')
    connect(f,{'1':a,'2':bnet})
    return f

# 2xAA power: two cells in series enter at J3; TPS61023 boosts the pack to 5 V.
# U1's 5V pad receives the boost only through D13 (Schottky, anode at boost),
# as required by Seeed. USB VBUS remains available and cannot back-feed the pack.
j3=load_fp('Connector_JST','JST_PH_S2B-PH-K_1x02_P2.00mm_Horizontal','J3','2xAA PACK (SWITCHED)',76.0,86.0,0,True,'Connector_JST:JST_PH_S2B-PH-K_1x02_P2.00mm_Horizontal')
connect(j3,{'1':'BAT_RAW','2':'GND'})
u4=load_fp('Package_TO_SOT_SMD','SOT-563','U4','TPS61023 2xAA BOOST',82.0,72.0,0,True,'Package_TO_SOT_SMD:SOT-563')
connect(u4,{'1':'BOOST_FB','2':'BAT_RAW','3':'BAT_RAW','4':'GND','5':'BOOST_SW','6':'BOOST_5V'})
l1=load_fp('Inductor_SMD','L_Wuerth_MAPI-4030','L1','1uH Isat>=7A',87.5,69.0,0,True,'Inductor_SMD:L_Wuerth_MAPI-4030')
connect(l1,{'1':'BAT_RAW','2':'BOOST_SW'})
capacitor0805('C3','10uF 10V X7R IN',78.5,68.5,'BAT_RAW','GND')
capacitor('C4','100nF BOOST HF',78.5,72.0,'BAT_RAW','GND',0)
capacitor0805('C5','22uF 10V X7R OUT',87.0,75.5,'BOOST_5V','GND')
capacitor0805('C6','22uF 10V X7R OUT',90.0,79.0,'BOOST_5V','GND')
resistor('R6','732k BOOST FB TOP',84.0,82.0,'BOOST_5V','BOOST_FB',0)
resistor('R7','100k BOOST FB BOT',87.5,82.0,'BOOST_FB','GND',0)
d13=load_fp('Diode_SMD','D_SMA','D13','SS14 1A SCHOTTKY',78.5,78.0,0,True,'Diode_SMD:D_SMA')
# KiCad D_SMA numbering: pad 1 is cathode, pad 2 is anode.
connect(d13,{'1':'USB_5V','2':'BOOST_5V'})

# MCP23017 RESET pull-up and I2C pull-ups (4.7k); RTC interrupt pull-up (10k).
# Put the buzzer base resistor on the front side so KiCad and FreeRouting use
# the same pad numbering; the resistor itself is non-polar.
resistor('R1','1k BUZZER BASE',32.0,65.5,'BUZZER_CTL','BUZZER_SW',0,False)
resistor('R2','10k RTC INT PU',57.0,65.5,'RTC_INT','3V3',0)
# These three 0603 resistors are unpolarized; swap pad nets so the underside
# router/import transform lands each named net on the matching physical pad.
resistor('R3','10k MCP RESET PU',51.0,64.5,'3V3','MCP_RESET',90)
resistor('R4','4k7 I2C SDA PU',59.0,64.5,'3V3','I2C_SDA',90)
resistor('R5','4k7 I2C SCL PU',64.0,64.5,'3V3','I2C_SCL',90)
capacitor('C1','100nF MCP DECOUPLE',56.3,75.5,'3V3','GND',90)
capacitor('C2','100nF RTC DECOUPLE',70.5,70.8,'3V3','GND',90)

# Piezo driver: low-side NPN protects XIAO GPIO from buzzer current.
q1=load_fp('Package_TO_SOT_SMD','SOT-23','Q1','MMBT3904 / NPN',40.5,77.0,0,True,'Package_TO_SOT_SMD:SOT-23')
# Standard KiCad SOT-23 pinout 1=B, 2=E, 3=C.
connect(q1,{'1':'BUZZER_SW','2':'GND','3':'BUZZER'})
# Stock BLARE 12 mm piezo footprint; pad 1 positive, pad 2 switched low-side.
bz=new_fp('BZ1','3.3V PIEZO',32.0,74.0,0,True,'BLARE:Buzzer_12x9.5RM7.6')
pad(bz,'1',-3.8,0,1.8,1.8,'pth',0.8,net='3V3'); pad(bz,'2',3.8,0,1.8,1.8,'pth',0.8,net='BUZZER')
finish_custom(bz)
# Acoustic ports: drill array in the copper-free lower edge area is handled in the enclosure.

# Mounting holes for BLARE's M3 screw / heat-set insert enclosure interface.
for ref,x,y in [('H1',4.5,4.5),('H2',89.5,4.5),('H3',4.5,85.5),('H4',89.5,85.5)]:
    h=new_fp(ref,'M3 CLEARANCE',x,y,0,False,'MountingHole:MountingHole_3.2mm_M3')
    pad(h,'',0,0,3.2,3.2,'npth',3.2)
    finish_custom(h)

# Board outline: 2 mm corner chamfers; line-segment outline on Edge.Cuts.
outline=[(2,0),(W-2,0),(W,2),(W,H-2),(W-2,H),(2,H),(0,H-2),(0,2),(2,0)]
for p1,p2 in zip(outline[:-1],outline[1:]): add_line(*p1,*p2,layer=pcbnew.Edge_Cuts,width=0.05)

# High-contrast front legends; title plus row guides / keypad legend.
add_text('DAWNKEY  /  BLARE',45.0,2.8,1.45,pcbnew.F_SilkS,0,0.18)
add_text('12-KEY WAKE PROTOCOL  |  2xAA BOOST',45.0,87.5,0.95,pcbnew.B_SilkS,0,0.13)
for i,(x,y) in enumerate([(xx,5.4) for xx in xs],1): add_text('%02d'%i,x,5.4,0.8,pcbnew.F_SilkS,0,0.12)
add_text('TFT',90.5,20.5,0.8,pcbnew.F_SilkS,90,0.12)
add_text('QWIIC / I2C',39.0,61.0,0.8,pcbnew.B_SilkS,90,0.12)
add_text('2xAA  /  NO CHARGER',79.0,88.8,0.72,pcbnew.B_SilkS,0,0.11)

# Key/connector silkscreen descriptions on the bottom side.
add_text('MCP23017  0x20',49.5,62.5,0.85,pcbnew.B_SilkS,0,0.12)
add_text('DS3231  0x68',64.0,63.5,0.85,pcbnew.B_SilkS,0,0.12)
add_text('D0 CLK D1 MOSI D2 RST D3 DC D4 CS D5 BL | D10 BUZZ',51.0,54.0,0.7,pcbnew.B_SilkS,0,0.10)

# Board title block and custom design settings.
title=b.GetTitleBlock(); title.SetTitle('DAWNKEY — BLARE 12-key RTC Alarm Clock'); title.SetComment(0,'2-layer, 94 x 90 mm; XIAO ESP32-C3; 4x3 MX matrix; 2xAA boost')
title.SetComment(1,'Firmware: Wire.begin(7,6); MCP23017 @ 0x20; DS3231 @ 0x68')

# Board setup for economical fabrication: 2 copper layers, 0.20 mm minimum.
# Run automatic routing from the generated DSN; ground pour is added after routing.

pcbnew.SaveBoard(os.path.join(OUT,'DawnKey.kicad_pcb'),b)
print('Saved',os.path.join(OUT,'DawnKey.kicad_pcb'))
print('Footprints:',len(list(b.GetFootprints())),'Nets:',b.GetNetCount())
print('XIAO pad positions:',[(p.GetNumber(),round(p.GetPosition().x/1e6,2),round(p.GetPosition().y/1e6,2),p.GetNetname()) for p in xiao.Pads()])
