"""Direct Python vector figures from retained widths, traces and model relations."""
from pathlib import Path
import argparse
import csv
import json
ARTIFACT=Path(__file__).resolve().parents[1]

def read_data(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        data = [(int(r["round"]), int(r["width"])) for r in csv.DictReader(stream)]
    if data != [(k, k + 1) for k in range(1, 13)]:
        raise ValueError("Expected all twelve retained sharp-family depths")
    return data

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=ARTIFACT/'results/figure-sources/widths.csv')
    parser.add_argument('--output-dir', type=Path, required=True)
    # Accepted for existing callers; direct vector output never invokes TeX.
    parser.add_argument('--tex-font-root', type=Path)
    parser.add_argument('--tex-font-map-dir', type=Path)
    parser.add_argument('--tex-bin-dir', type=Path)
    args=parser.parse_args()
    out=args.output_dir.resolve()
    retained=(ARTIFACT/'results').resolve()
    if out==retained or retained in out.parents:
        raise ValueError('Output must be separate from retained results')
    out.mkdir(parents=True,exist_ok=True)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, Polygon, Circle, FancyArrowPatch
    
    plt.rcParams.update({'font.family':'STIXGeneral', 'mathtext.fontset':'stix',
                         'font.size':9, 'pdf.fonttype':42, 'ps.fonttype':42,
                         'text.usetex':False, 'axes.unicode_minus':False})
    CM = 1 / 2.54
    
    class Drawing:
        def __init__(self, bounds):
            x0,y0,x1,y1 = bounds
            self.fig = plt.figure(figsize=((x1-x0)*CM,(y1-y0)*CM))
            self.ax = self.fig.add_axes([0,0,1,1], xlim=(x0,x1), ylim=(y0,y1))
            self.ax.set_aspect('equal'); self.ax.axis('off')
            self.nodes = {}
            self.labels = []
    
        def text(self,x,y,label,size=9,ha='center',va='center'):
            artist=self.ax.text(x,y,label,fontsize=size,ha=ha,va=va,
                                linespacing=1.15,clip_on=False,zorder=4)
            self.labels.append([artist,None])
            return artist
    
        def box(self,name,x,y,w,h,label,dashed=False,shape='rect',size=9):
            style = {'edgecolor':'black','facecolor':'white','linewidth':.55,
                     'linestyle':(0,(4,3)) if dashed else 'solid', 'zorder':2}
            if shape == 'diamond':
                obj = Polygon([(x-w/2,y),(x,y+h/2),(x+w/2,y),(x,y-h/2)],**style)
            elif shape == 'circle': obj = Circle((x,y),w/2,**style)
            else: obj = Rectangle((x-w/2,y-h/2),w,h,**style)
            self.ax.add_patch(obj); self.text(x,y,label,size)
            self.labels[-1][1]=(x-w/2,y-h/2,x+w/2,y+h/2)
            self.nodes[name] = (x,y,w,h,shape)
    
        def point(self,name,side):
            x,y,w,h,_ = self.nodes[name]
            return {'n':(x,y+h/2),'s':(x,y-h/2),'e':(x+w/2,y),
                    'w':(x-w/2,y),'nw':(x-w/2,y+h/2),
                    'ne':(x+w/2,y+h/2),'c':(x,y)}[side]
    
        def line(self,points,dashed=False):
            xs,ys=zip(*points)
            self.ax.plot(xs,ys,color='black',linewidth=.55,
                         linestyle=(0,(4,3)) if dashed else 'solid',zorder=1)
    
        def arrow(self,p,q,dashed=False,via=()):
            points=[p,*via,q]
            if via:self.line(points[:-1],dashed)
            self.ax.add_patch(FancyArrowPatch(points[-2],points[-1],
                             arrowstyle='-|>',mutation_scale=7.5,linewidth=.55,
                             color='black',shrinkA=0,shrinkB=0,
                             linestyle=(0,(4,3)) if dashed else 'solid',zorder=1))
    
        def edge(self,a,b,sa='s',sb='n',**kwargs):
            self.arrow(self.point(a,sa),self.point(b,sb),**kwargs)
    
        def frame(self,x,y,w,h):
            self.ax.add_patch(Rectangle((x,y),w,h,fill=False,edgecolor='black',
                                       linewidth=.55,linestyle=(0,(4,3)),zorder=0))
    
        def save(self,out,name):
            # Fixed physical canvas: do not enlarge or rasterize the scientific figure.
            self.fig.canvas.draw()
            renderer=self.fig.canvas.get_renderer()
            x0,x1=self.ax.get_xlim();y0,y1=self.ax.get_ylim()
            for artist,node in self.labels:
                b=artist.get_window_extent(renderer).transformed(self.ax.transData.inverted())
                if b.x0<x0-.02 or b.x1>x1+.02 or b.y0<y0-.02 or b.y1>y1+.02:
                    raise ValueError(name+': clipped label '+repr(artist.get_text()))
                if node and (b.x0<node[0]-.02 or b.x1>node[2]+.02 or b.y0<node[1]-.02 or b.y1>node[3]+.02):
                    raise ValueError(name+': label exceeds node '+repr(artist.get_text()))
            self.fig.savefig(out/(name+'.pdf'),format='pdf',
                             metadata={'Creator':'Python Matplotlib','Producer':None,
                                       'CreationDate':None,'ModDate':None})
            plt.close(self.fig)
    
    
    
    
    
    
    d=Drawing((-.9,-1.4,5.8,1.4))
    for i,y in [(1,.75),(2,-.65)]:
        d.text(-.65,y,rf'$C_{i}$',size=8)
        for j,x in enumerate([0,1.7,3.4,5.1]):
            key=f'{i}-{j}'
            symbol='C' if j%2==0 else 'T'
            d.box(key,x,y,.78,.43,'$'+symbol+'_{'+str(i)+str(j//2+1)+'}$',size=8)
            if j:d.edge(f'{i}-{j-1}',key,'e','w')
    d.edge('1-1','2-1',dashed=True)
    d.edge('2-1','2-3','s','s',dashed=True,via=((1.7,-1.18),(5.1,-1.18)))
    d.edge('2-3','1-3','n','s',dashed=True)
    d.save(out,'event-model')
    d=Drawing((-.2,-.8,7.5,1.75))
    d.arrow((0,0),(7.2,0))
    for x,label in [(2.6,'$H$'),(4.5,'$J$')]:
        d.line([(x,-.1),(x,.1)]);d.text(x,-.3,label,size=8)
        d.ax.add_patch(Circle((x,.5),.055,facecolor='white',edgecolor='black',linewidth=.55,zorder=3))
    d.arrow((2.5,.5),(.15,.5));d.arrow((4.6,.5),(7.05,.5),dashed=True)
    d.text(1.3,.9,'12 may survive',size=8);d.text(5.9,.9,'21 may survive',size=8)
    d.arrow((2.6,1.27),(4.5,1.27));d.arrow((4.5,1.27),(2.6,1.27))
    d.text(3.55,1.52,'$J-H>0$',size=8)
    d.text(3.55,-.65,'No input pair satisfies both conditions',size=8)
    d.text(7.05,-.30,r"$x'-y$",size=8)
    d.save(out,'separation')
    record=json.loads((ARTIFACT/'results/pairing-boundary.json').read_text())
    d=Drawing((-1.0,-4.9,13.1,2.6))
    scale=.7
    for offset,word,title in [(0,[1,2,1,2],'(a) Paired: 1212'),(-3.8,[1,1,2,2],'(b) Unrestricted: 1122')]:
        d.text(0,offset+2.25,title,size=8,ha='left')
        for lane,name in [(1.5,'$C_1$'),(.75,'$C_2$'),(0,'$L$')]:
            d.line([(0,offset+lane),(17*scale,offset+lane)])
            d.text(-.45,offset+lane+.20,name,size=7)
        trace=next(x['trace'] for x in record['orders'] if x['word']==word)
        for event in trace:
            i,k=event['stream'],event['round']
            for kind,y in [('compute',offset+(3-i)*.75),('transfer',offset)]:
                l=float(event[kind+'_start'])*scale;r=float(event[kind+'_end'])*scale
                d.ax.add_patch(Rectangle((l,y+.025),r-l,.43,facecolor='white' if kind=='compute' else '.88',edgecolor='black',linewidth=.55,zorder=2))
                symbol='C' if kind=='compute' else 'T'
                d.text((l+r)/2,y+.24,'$'+symbol+'_{'+str(i)+str(k)+'}$',size=6.5)
        d.arrow((0,offset-.36),(17.6*scale,offset-.36))
        for t in [0,5,10,13,17]:
            x=t*scale;d.line([(x,offset-.36),(x,offset-.44)]);d.text(x,offset-.61,str(t),size=7)
    d.save(out,'pairing-boundary')
    data=read_data(args.input)
    rounds,widths=zip(*data)
    fig=plt.figure(figsize=(3.5,4.21/2.54))
    ax=fig.add_axes([.14,.30,.83,.65])
    ax.plot(rounds,[k+1 for k in rounds],color='#243952',linewidth=.7,label='Proved bound $k+1$')
    ax.plot(rounds,widths,linestyle='none',color='#243952',marker='o',markerfacecolor='white',markersize=4,markeredgewidth=.7,label='Sharp-family checks')
    ax.plot([1,12],[2,2],color='.35',linestyle='--',linewidth=.7,label='Reset bound')
    ax.set(xlim=(.8,12.2),ylim=(0,14),xlabel='Round $k$',ylabel='Frontier states')
    ax.set_xticks([1,3,5,7,9,12]);ax.set_yticks([0,2,5,9,13])
    ax.tick_params(length=3,width=.55,labelsize=8.5)
    ax.legend(loc='upper left',frameon=False,fontsize=8,handlelength=2,borderaxespad=.35,labelspacing=.3)
    fig.savefig(out/'frontier-width.pdf',metadata={'CreationDate':None,'ModDate':None,'Creator':'Python Matplotlib'})
    plt.close(fig)
    print('Four direct vector figures rendered from declared dependencies and retained widths/traces.')


if __name__=='__main__':
    main()
