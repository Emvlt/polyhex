from polyhex.objects import Hexagon


a = Hexagon(
        hex_centre_coord=[0,0],
        node_feature='bear_salmon',
        edge_feature=[
            'water','water','desert','desert','desert','water'
            ]
    )

for k, v in a.feature_to_edges.items():
    print(k, v)

for k, v in a.edges_to_feature.items():
    print(k, v)