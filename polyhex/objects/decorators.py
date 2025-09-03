### Decorators for Polyhex
### These decorators are used to declutter the code and raise Errors in a systematic fashion
import functools 

def vertex_orientation_dependent(method):
    """Decorator to ensure that a method errors for the non-implemented  ordering of the vertex orientation"""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.vertex_orientation == 'clockwise':
            result = method(self, *args, **kwargs)
            return result
        elif self.vertex_orientation in ['counterclockwise']:
            raise NotImplementedError(f'The method {method} is notimplemented for a counterclockwise ordering of the vertices. Please use `clockwise` orientation.')
        else:
            raise ValueError
    return wrapper

def hex_coord_system_dependent(method):
    """"Decorator to ensure that a method errors for the non-implemented  hexagonal coordinate system of the vertex orientation"""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.hex_coord_system == 'axial':
            result = method(self, *args, **kwargs)
            return result
        elif self.hex_coord_system in ['offset', 'cube', 'doubled']:
            raise NotImplementedError(f'The method {method} is not implemented for the {self.hex_coord_system} coordinate system. Please use `axial` coordinate system.')
        else:
            raise ValueError
    return wrapper

def top_dependent(method):
    """"Decorator to ensure that a method errors for the non-implemented  hexagonal coordinate system of the vertex orientation"""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.top == 'pointy':
            result = method(self, *args, **kwargs)
            return result
        elif self.top == 'flat':
            raise NotImplementedError(f'The method {method.__str__()} is not implemented for hexagons with {self.top} top. Please use hexagons with `pointy` top instead.')
        else:
            raise ValueError
    return wrapper