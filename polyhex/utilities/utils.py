def replicate_vector(vector, n):
    if isinstance(vector, (list)):
        return n * vector
    else:
        raise NotImplementedError