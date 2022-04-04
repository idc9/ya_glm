from time import time
from warnings import warn

from yaglm.solver.base import GlmSolverWithPath
from yaglm.autoassign import autoassign
from yaglm.utils import is_multi_response, get_shapes_from, clip_zero
from yaglm.config.penalty_utils import get_flavor_kind
from yaglm.config.penalty import NoPenalty


class Cvxpy(GlmSolverWithPath):
    """
    Solves a penalized GLM problem using cvxpy.

    Parameters
    ---------
    zero_tol: float
        Values of the solution smaller than this are set to exactly zero.

    solver: None, str
        Which cvxpy solver to use. See cvxpy docs.

    cp_kws: dict
        Keyword arguments to the call to problem.solve(). See cvxpy docs.
    """

    @autoassign
    def __init__(self, zero_tol=1e-8, solver=None, verbose=False,
                 cp_kws={}): pass

    @classmethod
    def _is_applicable(self, loss, penalty=None, constraint=None):

        try:
            import cvxpy
        except ModuleNotFoundError:
            warn("cvxpy not installed so yaglm.solver.Cvxpy cannot be used")
            return False

        # cvxpy is applicable to any convex penalty
        return get_flavor_kind(penalty) not in ['non_convex', 'mixed']

    def setup(self, X, y, loss, penalty, constraint=None,
              fit_intercept=True, sample_weight=None):
        """
        Sets up anything the solver needs.
        """
        # import cvxpy in this call so we don't force the user
        # to have it installed
        import cvxpy as cp
        from yaglm.cvxpy.from_config import get_loss, get_penalty,\
            get_constraints

        # make sure CVXPY is applicable
        if not self.is_applicable(loss, penalty, constraint):
            raise ValueError("CVXPY is not applicable to "
                             "loss={}, penalty={}, constrain={}".
                             format(loss, penalty, constraint))

        self.is_mr_ = is_multi_response(y)
        coef_shape, intercept_shape = get_shapes_from(X, y)

        # initialize coefficient and intercepet
        self.coef_ = cp.Variable(shape=coef_shape)
        if fit_intercept:
            self.intercept_ = cp.Variable(shape=intercept_shape)
        else:
            self.intercept_ = None

        #######################
        # setup cvxpy problem #
        #######################
        loss_func = get_loss(coef=self.coef_,
                             intercept=self.intercept_,
                             X=X, y=y,
                             config=loss,
                             sample_weight=sample_weight)

        penalty_func, pen_val, weights = get_penalty(coef=self.coef_,
                                                     config=penalty)

        constraints = get_constraints(coef=self.coef_,
                                      config=constraint)

        # setup objective function
        objective = cp.Minimize(loss_func + penalty_func)

        self.problem_ = cp.Problem(objective=objective,
                                   constraints=constraints)

        # store these so they can be modified
        self.pen_val_ = pen_val
        self.weights_ = weights
        self.penalty_config_ = penalty if penalty is not None else NoPenalty()

    def update_penalty(self, **params):
        """
        Updates the penalty parameters.
        """
        # local import to avoid requiring cvxpy to be installed
        from yaglm.cvxpy.from_config import update_pen_val_and_weights

        self.penalty_config_.set_params(**params)
        update_pen_val_and_weights(config=self.penalty_config_,
                                   pen_val=self.pen_val_,
                                   weights=self.weights_)

    def solve(self, coef_init=None, intercept_init=None, other_init=None):

        # setup initialization
        self.coef_.value = coef_init
        self.intercept_.value = intercept_init

        # solve the problem
        start_time = time()
        self.problem_.solve(solver=self.solver, verbose=self.verbose,
                            **self.cp_kws)
        runtime = time() - start_time

        # TODO: should we copy here?
        coef = clip_zero(self.coef_.value, zero_tol=self.zero_tol)
        soln = {'coef': coef}
        if self.intercept_ is not None:
            soln['intercept'] = self.intercept_.value

        # TODO: should we copy here?
        opt_info = {**self.problem_.solver_stats.__dict__}
        opt_info['status'] = self.problem_.status
        opt_info['runtime'] = runtime

        opt_data = None

        return soln, opt_data, opt_info
