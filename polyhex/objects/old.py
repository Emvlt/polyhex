# def travel_edge(self, edge:Edge, t_hexes:List, t_edges:List):
    #     if edge not in t_edges:
    #         t_edges.append(edge)
    #         edge_key = self._get_edge_key(edge)
    #         for n in self.edges[edge_key].neighbours:
    #             t_hexes, t_edges = self.travel_hex(n, t_hexes, t_edges)
    #     return t_hexes, t_edges        
    
    # def travel_hex(self, hex: Hexagon, t_hexes:List, t_edges:List):
    #     if hex not in t_hexes:
    #         t_hexes.append(hex)
    #     for edge in hex.edges.values():
    #         t_hexes, t_edges = self.travel_edge(edge, t_hexes, t_edges)
    #     return t_hexes, t_edges
        
    # def travel(self):
    #     t_hexes = []
    #     t_edges = []
    
    #     for hexagon in self.hexagons.values():
    #         t_hexes, t_edges = self.travel_hex(
    #             hexagon, t_hexes, t_edges
    #             )
    #     return t_hexes, t_edges

    # def travel_area(self, 
    #         edge:Edge, 
    #         hex_in_area:List[Hexagon], 
    #         area_type : ArrayLike):
        
    #     current_hex = edge.hexagon_neighbours[0]
    #     if current_hex not in hex_in_area:
    #         hex_in_area.append(current_hex)

    #     if current_hex not in self.traversed_hexagons:
    #         self.traversed_hexagons.append(current_hex)

    #     if not edge in self.traversed_edges:        
    #         self.traversed_edges.append(edge)
            
    #         for neighbour_edge in edge.edge_neighbours:
    #             hex_in_area = self.travel_area(
    #                 neighbour_edge, hex_in_area, area_type
    #             )
        
    #     return hex_in_area

    # def travel_edge(self, edge:Edge):
    #     if not edge in self.traversed_edges:
    #         area_type = edge.feature
    #         hex_in_area = []
    #         hex_in_area = self.travel_area(
    #             edge, hex_in_area, area_type
    #         )
    #         self.edge_features[area_type].append(hex_in_area)
    
    # def travel(self):
    #     for edge in self.edges.values():
    #        self.travel_edge(edge)
    #     return self.edge_features
    
