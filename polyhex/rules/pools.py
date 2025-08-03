from polyhex.objects import Polyhex, Hexagon


hex_list_0 = [
    Hexagon(
        hex_centre_coord=[0,0],
        node_feature='bear',
        edge_feature=['mountain']
    ),
    Hexagon(
        hex_centre_coord=[0,1],
        node_feature='bear_salmon',
        edge_feature=[
            'water','water','desert','desert','desert','water'
            ]
    ),
    Hexagon(
        hex_centre_coord=[-1,1],
        node_feature='elk_fox_hawk',
        edge_feature=['forest','swamp','swamp','swamp','forest','forest']
    )
]
hex_list_1 = [
    Hexagon(
        hex_centre_coord=[0,0],
        node_feature='elk',
        edge_feature=['forest']
    ),
    Hexagon(
        hex_centre_coord=[0,1],
        node_feature='fox_salmon',
        edge_feature=['swamp','swamp','desert','desert','desert',
        'swamp']
            
    ),
    Hexagon(
        hex_centre_coord=[-1,1],
        node_feature='bear_elk_hawk',
        edge_feature=['mountain','water','water','water',
        'mountain','mountain']
    )
]
hex_list_2 = [
    Hexagon(
        hex_centre_coord=[0,0],
        node_feature='fox',
        edge_feature=['desert']
    ),
    Hexagon(
        hex_centre_coord=[0,1],
        node_feature='bear_elk',
        edge_feature=[
            'forest','forest','mountain','mountain',
            'mountain','forest'
            ]
    ),
    Hexagon(
        hex_centre_coord=[-1,1],
        node_feature='fox_hawk_salmon',
        edge_feature=['swamp','water','water','water','swamp','swamp']
    )
]
hex_list_3 = [
    Hexagon(
        hex_centre_coord=[0,0],
        node_feature='hawk',
        edge_feature=['swamp']
    ),
    Hexagon(
        hex_centre_coord=[0,1],
        node_feature='bear_fox',
        edge_feature=['desert','desert','mountain','mountain','mountain','desert']
    ),
    Hexagon(
        hex_centre_coord=[-1,1],
        node_feature='elk_hawk_salmon',
        edge_feature=['water','forest','forest','forest','water','water']
    )
]
hex_list_4 = [
    Hexagon(
        hex_centre_coord=[0,0],
        node_feature='salmon',
        edge_feature=['water']
    ),
    Hexagon(
        hex_centre_coord=[0,1],
        node_feature='bear_fox',
        edge_feature=['mountain','mountain','swamp','swamp','swamp','mountain']
            
    ),
    Hexagon(
        hex_centre_coord=[-1,1],
        node_feature='elk_hawk_salmon',
        edge_feature=['desert','forest','forest','forest','desert','desert']
    )
]

START_TILES = {
    "bear"   : Polyhex(hex_list_0),
    "elk"    : Polyhex(hex_list_1),
    "fox"    : Polyhex(hex_list_2),
    "hawk"   : Polyhex(hex_list_3),
    "salmon" : Polyhex(hex_list_4)
}