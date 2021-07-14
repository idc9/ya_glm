from ya_glm.autoassign import autoassign
from inspect import Signature, signature, Parameter

from makefun import wraps


def add_init_params(*classes, add_first=True):
    """
    
    Parameters
    ----------
    classes: 
        The classes whose init signatures we want to inherit.

    add_first: bool
        Add the parameters in first or last.
        
    Output
    -------
    init_wrapper: callable(init) --> callable
        A wrapper for __init__ that adds the keyword arguments from the super classes.
        Preference is given to init's params
    
    """
        
    def init_wrapper(init):

        # start with init's current parameters
        init_params = list(signature(init).parameters.values())
        init_params = init_params[1:]  # ignore self
        current_param_names = set(p.name for p in init_params)

        empty_init_params = set(['self', 'args', 'kwargs'])

        params = []
        if add_first:
            params.extend(init_params)

        for C in classes:
            # get params for this super class
            cls_params = signature(C.__init__).parameters

            # ignore classes with empty inits
            if set(cls_params) == empty_init_params:
                continue

            cls_params = list(cls_params.values())
            cls_params = cls_params[1:]  # ignore self
            # ignore parameter if it was already in init
            cls_params = [p for p in cls_params
                          if p.name not in current_param_names]
            current_param_names.update([p.name for p in cls_params])
            
            params.extend(cls_params)

        if not add_first:
            params.extend(init_params)
            
        # make sure self is first argument
        params.insert(0,
                      Parameter('self', kind=Parameter.POSITIONAL_OR_KEYWORD))

        @wraps(init, new_sig=Signature(params))
        @autoassign
        def __init__(self, **kws): pass    
        
        return __init__
    
    return init_wrapper

