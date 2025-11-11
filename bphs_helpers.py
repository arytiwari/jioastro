
# Minimal Python mirror of core helpers (for backend usage)
SIGN_LORD = {1:'Mars',2:'Venus',3:'Mercury',4:'Moon',5:'Sun',6:'Mercury',7:'Venus',8:'Mars',9:'Jupiter',10:'Saturn',11:'Saturn',12:'Jupiter'}
def wrap1to12(n): return (n-1)%12+1
def house_sign(asc, house): return wrap1to12(asc + (house-1))
def sign_house(asc, sign):
    d = sign - asc
    while d<=0: d += 12
    return d
def house_of(chart, planet):
    pl = next(x for x in chart['placements'] if x['planet']==planet)
    return pl.get('house') or sign_house(chart['ascSign'], pl['sign'])
def aspect(chart, a, b):
    ha, hb = house_of(chart,a), house_of(chart,b)
    diff = wrap1to12(hb-ha)
    if diff==7: return True
    if a=='Mars' and diff in (4,8): return True
    if a=='Jupiter' and diff in (5,9): return True
    if a=='Saturn' and diff in (3,10): return True
    return False
def lord_of_house(chart, house): from_sign = house_sign(chart['ascSign'], house); return SIGN_LORD[from_sign]
if __name__=='__main__':
    chart={'ascSign':9,'placements':[{'planet':'Jupiter','sign':1,'house':5},{'planet':'Ketu','sign':1,'house':5}]}
    print('LL=', lord_of_house(chart,1), 'LL house=', house_of(chart, lord_of_house(chart,1)))
