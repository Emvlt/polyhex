from typing import Optional, List, Tuple
from pathlib import Path 
parent_path = Path(__file__).parent.parent.resolve()
from io import BytesIO
import numpy as np
from numpy.random import Generator, PCG64
import json 
from PIL import Image
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
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 4}
    def __init__(self, 
            seed = 0,
            resources_path : str | Path = parent_path.joinpath(f'rules'),
            render_mode = "human"
            ):
        ### Setting the random state generator
        self.rng = np.random.default_rng(seed)
        ### Loading the resources
        # Hexagon pool
        self.hex_pool = HEXAGON_POOL.copy()
        
        # Config file
        with open(parent_path.joinpath('config.json'), 'rb') as fp:
            self.config = dict(json.load(fp))

        #### Building the initial state
        self.draw_pool = [
            self.draw() for i in range(4)
        ]
        # starting tile
        self.tile_names = list(self.config['encodings']['wildlife'].keys())
        animal_index = self.rng.choice(self.tile_names, size=1)[0]
        self.player_polyhex = START_TILES[animal_index] 
        # Player turn
        self.player_turn = 0
        
        # Rendering 
        self.render_mode = render_mode
        self.window = None
        self.clock = None
        self.window_size = (512+128,512)  # The size of the PyGame window

    def draw(self):
        index = self.rng.integers(0, len(self.hex_pool))
        hexagon = self.hex_pool[index]
        self.hex_pool.remove(hexagon)
        return hexagon
    
    def _get_obs(self):
        
        observations = {}
        # Get the hexagon pool
        draw_pool_encoding = []
        for i in range(4):
            draw_pool_encoding.append(self.draw_pool[i].centre_node.feature)
        observations["draw_pool"] = draw_pool_encoding
        # Get the available polyhex available nodes 
        observations[f"player_polyhex"] = f'{len(self.player_polyhex.get_graph_nodes())} available edges'

        return observations

    def reset(self, seed=None, options=None):
        # We need the following line to seed self.np_random
        super().reset(seed=seed)

        # Reset the pool
        self.hex_pool = HEXAGON_POOL.copy()
        # Deal the start tiles
        animal_index = self.rng.choice(self.tile_names, size=1)
        self.player_polyhex = START_TILES[animal_index] 
        # Reset player turns
        self.player_turn = 0
        # re-draw the pool
        self.draw_pool = [self.draw() for i in range(4)]

        observation = self._get_obs()

        if self.render_mode == "human":
            self._render_frame()

        return observation
    
    def step(self, action:Tuple[int,int]):
        """
        The action is a tuple (a,b) where:
            -> a is the index of the edge in the polyhex's border to which attach b
            -> b is one of the 24 indices (4hex*6edges) to sellect from the draw pool
        """
        # We map the action to the dictionnaries
        # Hex index and rotations to apply
        hex_index   = action[1] // 6
        edge_index = action[1] % 4
        drawn_hex : Hexagon = self.draw_pool[hex_index]
        # We need to get the right feature vector
        
        
        # We extract the polyhex's edge information
        edge_key = self.player_polyhex.index_to_edge_key(action[0])
        inner_hex = self.player_polyhex.polyhex_border[edge_key][2]
        placeholder_hex = self.player_polyhex.polyhex_border[edge_key][3]
        n_rotations = inner_hex.edges_to_adjency[edge_key][edge_index]
        edge_feature_vec = [drawn_hex.edges[(i+n_rotations )%6].feature for i in range(6)]
        # we construct a new polyhex with the desired position and feature
        new_hex = self.player_polyhex.placeholder_hex(
            hex_centre_coord = placeholder_hex.hex_coord,
            node_feature = drawn_hex.centre_node.feature,
            edge_feature = edge_feature_vec
        )
        self.player_polyhex.append_hex(new_hex)


        # Draw new tile
        self.draw_pool[hex_index] = self.draw()
        # Increment player turn
        self.player_turn += 1
        # An episode is over once 20 turns were taken
        terminated = False
        if self.player_turn == 5:
            terminated = True
        reward = self.player_polyhex.compute_habitat_result()

        observation = self._get_obs()

        if self.render_mode == "human":
            self._render_frame()

        return observation, reward, terminated, False, None
    
    def render(self):
        if self.render_mode == "human":
            return self._render_frame()
        
    def _render_frame(self):
        if self.window is None and self.render_mode == "human":
            pygame.init()
            pygame.display.init()
            self.window = pygame.display.set_mode(
                self.window_size
            )
        if self.clock is None and self.render_mode == "human":
            self.clock = pygame.time.Clock()

        ### Draw Board
        buf = BytesIO()
        self.player_polyhex.draw(buffer=buf)
        buf.seek(0)
        # Load image with PIL
        img = Image.open(buf)
        img = img.resize((512,512))
        # Convert PIL image to pygame surface
        mode = img.mode
        size = img.size
        data = img.tobytes()
        board = pygame.image.fromstring(data, size, mode)

        ### Draw pool
        pool = []
        for i in range(4):
            buf = BytesIO()
            self.draw_pool[i].draw(buffer=buf)
            buf.seek(0)
            # Load image with PIL
            img = Image.open(buf)
            img = img.resize((128,128))
            # Convert PIL image to pygame surface
            mode = img.mode
            size = img.size
            data = img.tobytes()
            pool.append(pygame.image.fromstring(data, size, mode)
)
        if self.render_mode == "human":
            # The following line copies our drawings from `canvas` to the visible window
            self.window.blit(board, dest=(128,0))
            for i, hexagon in enumerate(pool):
                self.window.blit(hexagon, dest=(0,i*128))
            pygame.event.pump()
            pygame.display.update()

            # We need to ensure that human-rendering occurs at the predefined framerate.
            # The following line will automatically add a delay to keep the framerate stable.
            self.clock.tick(1)
            paused = True
            while paused:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        paused = False
                    elif event.type == pygame.KEYDOWN:
                        observation, reward, terminated, _, _ =self.step((0,0))
                        paused != terminated
                        print(reward)
                    elif event.type == pygame.KEYUP:
                        paused = False
            return  
    def close(self):
        if self.window is not None:
            pygame.display.quit()
            pygame.quit()

    