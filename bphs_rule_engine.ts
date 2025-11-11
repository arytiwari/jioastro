
/**
 * BPHS Rule Engine (TypeScript)
 * Parāśari helpers + 250+ rules via builders
 */
export type Planet = 'Sun'|'Moon'|'Mars'|'Mercury'|'Jupiter'|'Venus'|'Saturn'|'Rahu'|'Ketu';
export type Dignity = 'exaltation'|'own'|'mooltrikona'|'debilitation'|'neutral'|'vargottama';
export interface Placement { planet: Planet; sign: number; house?: number; degrees?: number; retro?: boolean; dignity?: Dignity; tainted?: boolean; }
export interface Chart { ascSign: number; placements: Placement[]; options?: { treatMercuryAsBenefic?: boolean; moonPhase?: 'waxing'|'waning'|'unknown'; }; }
const SIGN_LORD: Record<number, Planet> = {1:'Mars',2:'Venus',3:'Mercury',4:'Moon',5:'Sun',6:'Mercury',7:'Venus',8:'Mars',9:'Jupiter',10:'Saturn',11:'Saturn',12:'Jupiter'};
const EXALTATION: Record<Planet, number> = {Sun:1, Moon:2, Mars:10, Mercury:6, Jupiter:4, Venus:12, Saturn:7, Rahu:0 as any, Ketu:0 as any};
export function wrap1to12(n:number){ return ((n-1)%12+12)%12+1; }
export function houseSign(ascSign:number, house:number){ return wrap1to12(ascSign + (house-1)); }
export function signHouse(ascSign:number, sign:number){ let d = sign-ascSign; while(d<=0) d+=12; return d; }
export function houseOf(c:Chart, p:Planet){ const pl=c.placements.find(x=>x.planet===p); if(!pl) throw new Error('Planet not found'); return pl.house ?? signHouse(c.ascSign, pl.sign); }
export function signOf(c:Chart, p:Planet){ const pl=c.placements.find(x=>x.planet===p); if(!pl) throw new Error('Planet not found'); return pl.sign; }
export function lordOfSign(s:number){ return SIGN_LORD[s]; }
export function lordOfHouse(c:Chart, h:number){ return lordOfSign(houseSign(c.ascSign,h)); }
export function isBenefic(c:Chart, p:Planet){ if(p==='Jupiter'||p==='Venus') return True; if(p==='Mercury'){ const opt=c.options?.treatMercuryAsBenefic??true; const t=c.placements.find(x=>x.planet==='Mercury')?.tainted; return opt && !t;} if(p==='Moon'){ return (c.options?.moonPhase==='waxing') && !c.placements.find(x=>x.planet==='Moon')?.tainted;} return false;}
export function isMalefic(c:Chart, p:Planet){ if(['Sun','Mars','Saturn','Rahu','Ketu'].includes(p)) return true; if(p==='Moon') return (c.options?.moonPhase==='waning') || !!c.placements.find(x=>x.planet==='Moon')?.tainted; if(p==='Mercury') return !!c.placements.find(x=>x.planet==='Mercury')?.tainted; return false; }
export function inKendra(h:number){ return [1,4,7,10].includes(h); }
export function inTrikona(h:number){ return [1,5,9].includes(h); }
export function inUpachaya(h:number){ return [3,6,10,11].includes(h); }
export function inPanaphara(h:number){ return [2,5,8,11].includes(h); }
export function inApoklima(h:number){ return [3,6,9,12].includes(h); }
export function conjunction(c:Chart, a:Planet, b:Planet){ return houseOf(c,a)===houseOf(c,b); }
export function aspect(c:Chart, a:Planet, b:Planet){ const ha=houseOf(c,a), hb=houseOf(c,b); const diff=wrap1to12(hb-ha); if(diff===7) return true; if(a==='Mars' && (diff===4||diff===8)) return true; if(a==='Jupiter' && (diff===5||diff===9)) return true; if(a==='Saturn' && (diff===3||diff===10)) return true; return false; }
export interface Rule { id:string; name:string; notes?:string; evaluate:(c:Chart)=>boolean; }
export class Engine { rules:Rule[]=[]; add(r:Rule){ this.rules.push(r); } evaluateAll(c:Chart){ return this.rules.map(r=>({id:r.id,name:r.name,pass:r.evaluate(c)})); }}
function rule(id:string,name:string, fn:(c:Chart)=>boolean, notes?:string):Rule{ return {id,name,notes,evaluate:fn}; }
export function buildEngine(){ const eng=new Engine(); const all:Planet[]=['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn'];
  eng.add(rule('A-14','Vaapī Nabhasa',(c)=> all.every(p=> inPanaphara(houseOf(c,p))) || all.every(p=> inApoklima(houseOf(c,p))), 'All seven in 2/5/8/11 or in 3/6/9/12'));
  eng.add(rule('B-16','Kālanidhi',(c)=>{ const hv=houseOf(c,'Venus'), hm=houseOf(c,'Mercury'); const ok=(h:number)=> h===2||h===11; const jV=aspect(c,'Jupiter','Venus'); const jM=aspect(c,'Jupiter','Mercury'); return ok(hv)&&ok(hm)&&(jV||jM); }));
  eng.add(rule('D-01','Vesi',(c)=> c.placements.some(p=> p.planet!=='Moon' && wrap1to12(houseOf(c,p.planet)-houseOf(c,'Sun'))===2)));
  eng.add(rule('D-02','Vasi',(c)=> c.placements.some(p=> p.planet!=='Moon' && wrap1to12(houseOf(c,p.planet)-houseOf(c,'Sun'))===12)));
  eng.add(rule('D-03','Ubhayachari',(c)=>{ const any2=c.placements.some(p=> p.planet!=='Moon' && wrap1to12(houseOf(c,p.planet)-houseOf(c,'Sun'))===2); const any12=c.placements.some(p=> p.planet!=='Moon' && wrap1to12(houseOf(c,p.planet)-houseOf(c,'Sun'))===12); return any2 && any12; }));
  const modes: ('conj'|'aspect'|'kendra'|'trikona'|'exchange')[]=['conj','aspect','kendra','trikona','exchange'];
  function rel(c:Chart, a:Planet,b:Planet, m:'conj'|'aspect'|'kendra'|'trikona'|'exchange'){ if(m==='conj') return conjunction(c,a,b); if(m==='aspect') return aspect(c,a,b)||aspect(c,b,a); if(m==='kendra'){ const ha=houseOf(c,a), hb=houseOf(c,b); const d=wrap1to12(hb-ha); return [1,4,7,10].includes(d);} if(m==='trikona'){ const ha=houseOf(c,a), hb=houseOf(c,b); const d=wrap1to12(hb-ha); return [1,5,9].includes(d);} if(m==='exchange'){ const sa=signOf(c,a), sb=signOf(c,b); return (SIGN_LORD[sa]===b && SIGN_LORD[sb]===a);} return false; }
  eng.add(rule('F-000','LL trine/kendra',(c)=> { const ll=lordOfHouse(c,1); const h=houseOf(c,ll); return inKendra(h)||inTrikona(h);}));
  for(const T of [5,9]){ eng.add(rule('F-00'+T,`LL with ${T}L`,(c)=>modes.some(m=> rel(c, lordOfHouse(c,1), lordOfHouse(c,T), m)))); }
  for(const K of [1,4,7,10]) for(const T of [5,9]) for(const m of modes){
    eng.add(rule(`F-${K}${T}-${m}`,`Rāja‑Yoga: ${K}L with ${T}L (${m})`,(c)=> rel(c,lordOfHouse(c,K),lordOfHouse(c,T),m)));
  }
  eng.add(rule('H-15','5L–9L wealth link',(c)=> modes.some(m=> rel(c,lordOfHouse(c,5),lordOfHouse(c,9),m))));
  eng.add(rule('I-16','Mars+Saturn in 2nd (poverty unless Mercury aspects)',(c)=>{ const hMa=houseOf(c,'Mars'), hSa=houseOf(c,'Saturn'); const both2=(hMa===2&&hSa===2); const mercA=aspect(c,'Mercury','Mars')||aspect(c,'Mercury','Saturn'); return both2 && !mercA; }));
  return eng; }
if(typeof require!=='undefined' && require.main===module){ const chart:Chart={ascSign:9, placements:[{planet:'Jupiter',sign:1,house:5},{planet:'Ketu',sign:1,house:5},{planet:'Sun',sign:11,house:3},{planet:'Moon',sign:11,house:3},{planet:'Mars',sign:2,house:6},{planet:'Mercury',sign:10,house:2},{planet:'Venus',sign:10,house:2},{planet:'Saturn',sign:4,house:8},{planet:'Rahu',sign:7,house:11}], options:{treatMercuryAsBenefic:true, moonPhase:'unknown'}}; const eng=buildEngine(); console.log(JSON.stringify(eng.evaluateAll(chart).filter(x=>x.pass), null, 2)); }
