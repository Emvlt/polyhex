from typing import Dict

from polyhex.objects import Polyhex, Hexagon
from polyhex import DEFAULT_CONFIG_FILE

def hawk_A(polyhex:Polyhex) -> int:
    # Calculate point helper
    def _calculate_points(count):
        assert 0 <= count
        if count == 0:
            return 0 
        if count == 1:
            return 2
        if count == 2:
            return 5
        if count == 3:
            return 8
        if count == 4:
            return 11
        if count == 5:
            return 14
        if count == 6:
            return 18
        elif count == 7:
            return 22
        else:
            return 26
        
    ### Solitary Hawk
    count = 0
    counted = []
    for coord, hex in polyhex.hawk_hexagons.items():
        # Clokwise search for neighbours
        coord : tuple
        hex   : Hexagon
        counted.append(coord)
        for coord in hex.adjency():
            if coord in polyhex.hawk_hexagons:
                break
        count += 1
    return _calculate_points(count)

def score_hawk(polyhex, identifier: str) -> int:
    if identifier == 'A':
        return hawk_A(polyhex)
    else:
        raise ValueError

def wildlife(polyhex, identifiers:Dict[str, str]):
    score = 0 
    score += score_hawk(polyhex, identifiers['hawk'])

def habitat(polyhex:Polyhex, verbose=False) -> int:
    result = {}
    total  = 0
    for area_name, area_list in polyhex.edge_features.items():
        area_total = max([len(area) for area in area_list])
        result[area_name] = area_total
        total += area_total

    if verbose : 
        for k, v in result.items():
            print(f'The {k} area yields {v} points.')
        print(f'For a total of {total} :)')
    return total
    