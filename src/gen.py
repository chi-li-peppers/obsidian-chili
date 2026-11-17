import colorsys, json, os

# name, slug, accent A, accent B, heat(1-5), note
P = [
 ("Jalapeño","jalapeno","#3FA34D","#A7D16A",2,"Fresh green, the calm default"),
 ("Habanero","habanero","#FF7A1A","#FFC145",4,"Orange heat with a sunny accent"),
 ("Carolina Reaper","reaper","#D7263D","#FF6B6B",5,"The meanest red there is"),
 ("Ghost","ghost","#8E7CC3","#C9B8FF",5,"Smoky lavender, quiet but hot"),
 ("Poblano","poblano","#2E6E4E","#7FB685",1,"Deep pine, made for long reads"),
 ("Chipotle","chipotle","#A0522D","#D98E4E",3,"Smoked cinnamon"),
 ("Padrón","padron","#7A9A3A","#C5D86D",1,"Olive and lime"),
 ("Shishito","shishito","#4DB6AC","#9ED9C9",1,"Minty and light"),
 ("Scotch Bonnet","scotch","#F2B705","#F27405",4,"Yellow-orange, wide awake"),
 ("Cayenne","cayenne","#C0392B","#E67E22",4,"Classic red with a flame"),
 ("Espelette","espelette","#D9480F","#F59F00",3,"Basque paprika"),
 ("Aleppo","aleppo","#8B2635","#D17A22",3,"Burgundy and saffron"),
 ("Urfa Biber","urfa","#6D2E46","#C08497",3,"Plum-black, velvety"),
 ("Bird's Eye","birdseye","#FF3366","#FFB3C6",5,"Thai pink-red"),
 ("Piri Piri","piripiri","#FF6F59","#43AA8B",4,"Coral and green, high contrast"),
 ("Banana","banana","#E9C46A","#2A9D8F",1,"Soft yellow with teal"),
 ("Fresno","fresno","#E63946","#4F8FC0",3,"Red and steel blue"),
 ("Pasilla","pasilla","#6B5876","#B48EAD",2,"Near-black violet, Nord vibes"),
 ("Guajillo","guajillo","#B5523B","#E9A178",2,"Rust and terracotta"),
 ("Ancho","ancho","#7B3F2B","#C08552",2,"Mahogany, warm wood"),
 ("Serrano","serrano","#10B981","#F97316",3,"Emerald with an orange spark"),
 ("Datil","datil","#F59E0B","#84CC16",4,"Amber and lime"),
 ("Purple Bell","bell","#7C3AED","#F472B6",1,"Purple bell, neon-lite"),
 ("Ají Amarillo","amarillo","#FFB000","#FF5F1F",3,"Peruvian sun"),
 ("Pepper X","pepperx","#00D9FF","#FF2E88",5,"Cyberpunk: cyan and magenta"),
 ("Adjika","adjika","#C1121F","#6A994E",4,"Red pepper and herbs, Georgian style"),
 ("Svan Salt","svan","#E07A5F","#81B29A",2,"Paprika, coriander and blue fenugreek"),
]

def h2rgb(h): h=h.lstrip('#'); return tuple(int(h[i:i+2],16)/255 for i in (0,2,4))
def hls(h): r,g,b=h2rgb(h); return colorsys.rgb_to_hls(r,g,b)
def mk(hh,l,s): r,g,b=colorsys.hls_to_rgb(hh,l,s); return '#%02x%02x%02x'%(round(r*255),round(g*255),round(b*255))
def lum(hx):
    def c(v): return v/12.92 if v<=0.03928 else ((v+0.055)/1.055)**2.4
    r,g,b=h2rgb(hx); return 0.2126*c(r)+0.7152*c(g)+0.0722*c(b)
def contrast(a,b):
    la,lb=sorted([lum(a),lum(b)],reverse=True); return (la+0.05)/(lb+0.05)
def fit(color,bg,target,darker):
    h,l,s=hls(color)
    for _ in range(60):
        c=mk(h,l,s)
        if contrast(c,bg)>=target: return c
        l = l-0.015 if darker else l+0.015
        l=max(0,min(1,l))
    return mk(h,l,s)

def palettes(a,b):
    h,_,s=hls(a); ts=min(s,0.9)
    dark=dict(
      bg=mk(h,0.085,ts*0.22), bg2=mk(h,0.065,ts*0.22), bg3=mk(h,0.115,ts*0.22),
      border=mk(h,0.18,ts*0.18), text=mk(h,0.89,ts*0.12), muted=mk(h,0.64,ts*0.10), faint=mk(h,0.45,ts*0.10))
    light=dict(
      bg=mk(h,0.975,ts*0.45), bg2=mk(h,0.935,ts*0.38), bg3=mk(h,0.955,ts*0.40),
      border=mk(h,0.85,ts*0.25), text=mk(h,0.14,ts*0.25), muted=mk(h,0.40,ts*0.15), faint=mk(h,0.60,ts*0.12))
    dark['a']=fit(a,dark['bg'],4.5,False); dark['b']=fit(b,dark['bg'],3.0,False)
    light['a']=fit(a,light['bg'],4.5,True); light['b']=fit(b,light['bg'],3.0,True)
    for p in (dark,light):
        p['onA'] = '#ffffff' if contrast('#ffffff',p['a'])>=contrast('#111111',p['a']) else '#111111'
    return dark,light

VARS=[]
for name,slug,a,b,heat,note in P:
    d,l=palettes(a,b)
    VARS.append(dict(name=name,slug=slug,heat=heat,note=note,dark=d,light=l))

def block(sel,p):
    h,lv,s=hls(p['a'])
    return f"""{sel} {{
  --chili-a: {p['a']}; --chili-b: {p['b']};
  --chili-bg: {p['bg']}; --chili-bg2: {p['bg2']}; --chili-bg3: {p['bg3']};
  --chili-border: {p['border']}; --chili-text: {p['text']}; --chili-muted: {p['muted']}; --chili-faint: {p['faint']};
  --chili-on-a: {p['onA']};
  --accent-h: {round(h*360)}; --accent-s: {round(s*100)}%; --accent-l: {round(lv*100)}%;
}}
"""

opts="\n".join(f"        -\n            label: \"{v['name']}\"\n            value: chili-{v['slug']}" for v in VARS)
settings=f"""/* @settings
name: Chili
id: chili-theme
settings:
    -
        id: chili-variant
        title: Pepper (palette variant)
        type: class-select
        allowEmpty: false
        default: chili-jalapeno
        options:
{opts}
    -
        id: chili-no-heat-strip
        title: Hide the heat strip
        type: class-toggle
    -
        id: chili-flat-headings
        title: Flat headings (no gradient)
        type: class-toggle
    -
        id: chili-sans-headings
        title: Sans-serif headings
        type: class-toggle
*/
"""

css=[ "/* Chili — an Obsidian theme with 27 pepper palettes. MIT. */\n", settings]
# defaults (jalapeño) + per-variant
css.append(block("body.theme-dark", VARS[0]['dark']))
css.append(block("body.theme-light", VARS[0]['light']))
for v in VARS:
    css.append(block(f"body.theme-dark.chili-{v['slug']}", v['dark']))
    css.append(block(f"body.theme-light.chili-{v['slug']}", v['light']))

css.append(open(os.path.join(os.path.dirname(__file__),'base.css')).read())
os.makedirs(os.path.join(os.path.dirname(__file__),'..'),exist_ok=True)
open(os.path.join(os.path.dirname(__file__),'..','theme.css'),'w').write("".join(css))
json.dump(VARS,open(os.path.join(os.path.dirname(__file__),'variants.json'),'w'),ensure_ascii=False)
print(len(VARS),"variants")
for v in VARS: print(v['slug'], v['dark']['a'], v['light']['a'])
