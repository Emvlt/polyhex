from typing import Optional, List
from pathlib import Path 
parent_path = Path(__file__).parent.parent.resolve()

import numpy as np
from numpy.random import Generator, PCG64
import json 
import pygame
import gymnasium as gym
import pandas as pd

from polyhex.objects import Hexagon
from polyhex.rules.pools import START_TILES

def parse_node_feature(row):
    s0 = row[6].strip()
    s1 = row[7].strip()
    s2 = row[8].strip()
    node_feature = f"{s0}"
    if s1 == 'False':
        return node_feature
    node_feature += f"_{s1}"
    if s2 == 'False':
        return node_feature
    node_feature += f"_{s2}"
    return node_feature

def parse_edge_feature(row):
    return [row[i].strip() for i in range(6)]

def parse_row(row):
    node_feature = parse_node_feature(row)
    edge_feature = parse_edge_feature(row)
    return node_feature, edge_feature

hexagons_file = pd.read_csv(parent_path.joinpath(f'rules/hexagons.csv'))
HEXAGON_POOL = []
for row in hexagons_file.itertuples(index=False):
    node_feature, edge_feature = parse_row(row)
    HEXAGON_POOL.append(Hexagon(
        node_feature=node_feature,
        edge_feature=edge_feature
    ))

class CascadiaEnv(gym.Env):
    
    def __init__(self, 
            n_players = 1,
            seed = 0,
            resources_path : str | Path = parent_path.joinpath(f'rules')   
            ):
        ### Setting the random state generator
        self.rng = np.random.default_rng(seed)
        ### Loading the resources
        # Hexagon pool
        self.hex_pool = HEXAGON_POOL
        
        # Config file
        with open(parent_path.joinpath('config.json'), 'rb') as fp:
            self.config = dict(json.load(fp))

        #### Building the initial state
        self.draw_pool = [
            self.draw() for i in range(4)
        ]

        # starting tile
        tile_names = list(self.config['encodings']['wildlife'].keys())
        self.player_polyhex = {
            i: START_TILES[animal] for i, animal in enumerate(self.rng.choice(tile_names, size=n_players))
            }

    def draw(self):
        index = self.rng.integers(0, len(self.hex_pool))
        hexagon = self.hex_pool[index]
        self.hex_pool.remove(hexagon)
        return hexagon
    
    def _get_obs(self):
        # Get the hexagon pool
        draw_pool_encoding = []
        for i in range(4):
            draw_pool_encoding += self.draw_pool[i].get_graph_nodes()
        return draw_pool_encoding
    
    def render(self):
        if self.render_mode == "rgb_array":
            return self._render_frame()
        
    def _render_frame(self):
        if self.window is None and self.render_mode == "human":
            pygame.init()
            pygame.display.init()
            self.window = pygame.display.set_mode(
                (self.window_size, self.window_size)
            )
        if self.clock is None and self.render_mode == "human":
            self.clock = pygame.time.Clock()

        canvas = pygame.Surface((self.window_size, self.window_size))
        canvas.fill((255, 255, 255))
        pix_square_size = (
            self.window_size / self.size
        )  # The size of a single grid square in pixels

        # First we draw the target
        pygame.draw.rect(
            canvas,
            (255, 0, 0),
            pygame.Rect(
                pix_square_size * self._target_location,
                (pix_square_size, pix_square_size),
            ),
        )
        # Now we draw the agent
        pygame.draw.circle(
            canvas,
            (0, 0, 255),
            (self._agent_location + 0.5) * pix_square_size,
            pix_square_size / 3,
        )

        # Finally, add some gridlines
        for x in range(self.size + 1):
            pygame.draw.line(
                canvas,
                0,
                (0, pix_square_size * x),
                (self.window_size, pix_square_size * x),
                width=3,
            )
            pygame.draw.line(
                canvas,
                0,
                (pix_square_size * x, 0),
                (pix_square_size * x, self.window_size),
                width=3,
            )

        if self.render_mode == "human":
            # The following line copies our drawings from `canvas` to the visible window
            self.window.blit(canvas, canvas.get_rect())
            pygame.event.pump()
            pygame.display.update()

            # We need to ensure that human-rendering occurs at the predefined framerate.
            # The following line will automatically add a delay to keep the framerate stable.
            self.clock.tick(self.metadata["render_fps"])
        else:  # rgb_array
            return np.transpose(
                np.array(pygame.surfarray.pixels3d(canvas)), axes=(1, 0, 2)
            )
        
    def close(self):
        if self.window is not None:
            pygame.display.quit()
            pygame.quit()