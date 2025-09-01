from importlib.resources import files
import json
from pathlib import Path

def load_assets(assets_file_name : str):
    path = Path(files("polyhex.assets").joinpath(assets_file_name))
    assert path.is_file(), f"There is no asset file at {path} for the asset file with name {assets_file_name}"
    file_extension = assets_file_name.split('.')[-1]
    if path.suffix == '.json':
        with path.open("r", encoding="utf-8") as f:
            return dict(json.load(f))
    else:
        raise NotImplementedError(f'load_assets is only implemented for json files, got {file_extension}.')