def replicate_vector(vector, n:int):
    if isinstance(vector, (list)):
        return n * vector
    else:
        raise NotImplementedError(f'The function `replicate_vector` is not implemented for lists, got {type(vector)}')