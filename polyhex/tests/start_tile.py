from polyhex.objects import Hexagon
from polyhex.rules.pools import START_TILES
from polyhex.rules import scoring

# key = 'bear'
# p = START_TILES[key]
# axes = p.draw(save_path=key, scale=False)

for key, p in START_TILES.items():

    axes = p.draw(save_path=key, scale=False)
    nodes = p.get_graph_nodes()
    print(nodes)
    p.append_hex(Hexagon(
        hex_centre_coord=[1,0],
        node_feature='salmon',
        edge_feature=['water']
    ))
    edge_indices, edge_attributes = p.get_graph_edges()
    nodes = p.get_graph_nodes()
    print(len(nodes))
    p.append_hex(Hexagon(
        hex_centre_coord=[-1,0],
        node_feature='bear_hawk',
        edge_feature=['mountain']
    ))
    p.add_token((1,0), 'salmon')
    edge_indices, edge_attributes = p.get_graph_edges()
    nodes = p.get_graph_nodes()
    print(len(nodes))
    p.append_hex(Hexagon(
        hex_centre_coord=[0,2],
        node_feature='salmon',
        edge_feature=['water']
    ))
    p.add_token((0,2), 'salmon')
    edge_indices, edge_attributes = p.get_graph_edges()
    nodes = p.get_graph_nodes()
    print(len(nodes))
    p.append_hex(Hexagon(
        hex_centre_coord=[2,0],
        node_feature='salmon',
        edge_feature=['water']
    ))
    edge_indices, edge_attributes = p.get_graph_edges()
    nodes = p.get_graph_nodes()
    print(len(nodes))
    p.append_hex(Hexagon(
        hex_centre_coord=[1,1],
        node_feature='salmon',
        edge_feature=['water']
    ))
    edge_indices, edge_attributes = p.get_graph_edges()
    nodes = p.get_graph_nodes()
    print(len(nodes))
    p.append_hex(Hexagon(
        hex_centre_coord=[-1,2],
        node_feature='salmon',
        edge_feature=['desert','desert','desert', 'swamp', 'swamp', 'swamp']
    ))
    edge_indices, edge_attributes = p.get_graph_edges()
    nodes = p.get_graph_nodes()
    print(len(nodes))
    axes = p.draw(save_path=key, scale=False)
    print(Hexagon(
        hex_centre_coord=[-1,2],
        node_feature='salmon',
        edge_feature=['desert','desert','desert', 'swamp', 'swamp', 'swamp']
    ).get_graph_nodes())

    # p.compute_habitat_result(verbose=True)
    break
    hawk_result = scoring.wildlife(p, {'hawk': 'A'})