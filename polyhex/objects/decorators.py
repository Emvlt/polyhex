import functools 

__all__ = ('hex_coord_system_dependent',)

def hex_coord_system_dependent(method):
    """Decorator to log a class method call."""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.hex_coord_system == 'axial':
            result = method(self, *args, **kwargs)
            return result
        elif self.hex_coord_system in ['offset', 'cube', 'doubled']:
            raise NotImplementedError
        else:
            raise ValueError
    return wrapper