# Yet another generalized linear model package


`yaglm` [is a modern, comprehensive and flexible Python package](https://arxiv.org/abs/2110.05567) for fitting and tuning penalized generalized linear models and other supervised [M-estimators](https://en.wikipedia.org/wiki/M-estimator) in Python. It supports a wide variety of losses (linear, logistic, quantile, etc) combined with penalties and/or constraints. Beyond the basic lasso/ridge, `yaglm` supports  **structured sparsity** penalties such as the nuclear norm and the [group](https://rss.onlinelibrary.wiley.com/doi/pdfdirect/10.1111/j.1467-9868.2005.00532.x?casa_token=wN_F5iYwNK4AAAAA:4PVnAz4icP5hR9FIRviV0zqnp_QAibv55uYkptKQKezvDoqtMzrSpFyHh15lL4IO1yFJ3Sfl4OwOuA), [exclusive](https://projecteuclid.org/journals/electronic-journal-of-statistics/volume-11/issue-2/Within-group-variable-selection-through-the-Exclusive-Lasso/10.1214/17-EJS1317.full), [graph fused](https://arxiv.org/pdf/1505.06475.pdf), and [generalized lasso](https://www.stat.cmu.edu/~ryantibs/papers/genlasso.pdf). It also supports the more accurate **[adaptive](http://users.stat.umn.edu/~zouxx019/Papers/adalasso.pdf)** and **non-convex** (e.g. [SCAD](https://fan.princeton.edu/papers/01/penlike.pdf)) *flavors* of these penalties that typically come with strong statistical guarantees at limited additional computational expense.

Parameter tuning methods including cross-validation, generalized cross-validation, and information criteria (e.g. AIC, BIC, [EBIC](https://www.jstor.org/stable/20441500), [HBIC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4060811/)) come built-in. BIC-like information criteria are important for analysts interested in model selection [(Zhang et al, 2012)](https://www.tandfonline.com/doi/abs/10.1198/jasa.2009.tm08013). We also provide built-in linear regression noise variance estimators ([Reid et al, 2016](https://www.jstor.org/stable/pdf/24721190.pdf?casa_token=wVML37DFzk4AAAAA:PCPZH8z98S_ZDNMyFxtec9-ZsIx73xoxDgWJUEObeJooVLwMWhOAn_Tnf2GQGL3H36XAROk5P08aNGcDnJUG95ahVwe1F57AsJg0_kxntX4UIoSoEAk); [Yu and Bien, 2019](https://academic.oup.com/biomet/article/106/3/533/5498375?casa_token=MSUn8MK2SgYAAAAA:r1tkX7-qUE7RIndcJk4_mfKUcuo3SuPImBy8pLX7H5rTA8cp_-7pUn-XzZzpAJuT_Blr8xmLFjvd); [Liu et al, 2020](https://academic.oup.com/biomet/article/107/2/481/5716270?casa_token=EYC-Z7uyoScAAAAA:6kQhSHg6NJEDWKAgJobCfV_HwNxa5uSWD38hzjW8zUj33n8EUJgzPWuT6yiVUVwmgVMook0oUajW)). Tuning parameter grids are automatically created from the data whenever possible.

`yaglm` comes with a computational backend based on [FISTA](https://epubs.siam.org/doi/pdf/10.1137/080716542?casa_token=cjyK5OxcbSoAAAAA:lQOp0YAVKIOv2-vgGUd_YrnZC9VhbgWvZgj4UPbgfw8I7NV44K82vbIu0oz2-xAACBz9k0Lclw) with adaptive restarts, an [augmented ADMM](https://www.tandfonline.com/doi/full/10.1080/10618600.2015.1114491) algorithm, [cvxpy](https://www.cvxpy.org/index.html), and the [LLA](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4295817/) algorithm for non-convex penalties. Path algorithms and parallelization for fast tuning are supported. It is straightforward to supply your favorite, state of the art optimization algorithm to the package.


`yaglm` follows a sklearn compatible API, is highly customizable and was inspired by many existing packages including [sklearn](https://scikit-learn.org/stable/), [lightning](https://github.com/scikit-learn-contrib/lightning), [statsmodels](https://www.statsmodels.org/), [pyglmnet](https://github.com/glm-tools/pyglmnet), [celer](https://github.com/mathurinm/celer), [andersoncd](https://github.com/mathurinm/andersoncd), [picasso](https://github.com/jasonge27/picasso), [tick](https://github.com/X-DataInitiative/tick), [PyUNLocBoX](https://github.com/epfl-lts2/pyunlocbox), [regerg](https://github.com/regreg/regreg), [grpreg](https://github.com/pbreheny/grpreg), [ncreg](https://cran.r-project.org/web/packages/ncvreg/index.html), and [glmnet](https://glmnet.stanford.edu/articles/glmnet.html).

A manuscript describing this package and the broader GLM ecosystem can be [found on arxiv](https://arxiv.org/abs/2110.05567).

 **Beware**: This is a preliminary release of version 0.3.1. Not all features have been fully added and it has not yet been rigorously tested.


# Installation
`yaglm` can be installed via github
```
git clone https://github.com/yaglm/yaglm.git
python setup.py install
```


# Examples

`yaglm` should feel a lot like sklearn -- particularly [LassoCV](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LassoCV.html). The major difference is that we make extensive use of config objects to specify the loss, penalty, penalty flavor, constraint, and solver.


```python
from yaglm.toy_data import sample_sparse_lin_reg

from yaglm.GlmTuned import GlmCV, GlmTrainMetric

from yaglm.config.loss import Huber
from yaglm.config.penalty import Lasso, GroupLasso
from yaglm.config.flavor import Adaptive, NonConvex

from yaglm.metrics.info_criteria import InfoCriteria
from yaglm.infer.Inferencer import Inferencer
from yaglm.infer.lin_reg_noise_var import ViaRidge


# sample sparse linear regression data
X, y, _ = sample_sparse_lin_reg(n_samples=100, n_features=10)

# fit a lasso penalty tuned via cross-validation with the 1se rule
GlmCV(loss='lin_reg',
      penalty=Lasso(),  # specify penalty with config object
      select_rule='1se'
      ).fit(X, y)

# fit an adaptive lasso tuned via cross-validation
# initialized with a lasso tuned with cross-validation
GlmCV(loss='lin_reg',
      penalty=Lasso(flavor=Adaptive()),
      initializer='default'
      ).fit(X, y)

# fit an adaptive lasso and tuned via EBIC
# estimate the noise variance via a ridge-regression method
GlmTrainMetric(loss='lin_reg',
               penalty=Lasso(flavor=Adaptive()),

               inferencer=Inferencer(scale=ViaRidge()),  # noise variance estimator
               scorer=InfoCriteria(crit='ebic')  # Info criteria
               ).fit(X, y)

# fit a huber loss with a group SCAD penalty
# both the huber knot parameter and the SCAD penalty parameter are tuned with CV
# the LLA algorithm is initialized with a group Lasso penalty tuned via cross-validation
groups = [range(5), range(5, 10)]
GlmCV(loss=Huber().tune(knot=range(1, 5)),
      penalty=GroupLasso(groups=groups,
                         flavor=NonConvex()),
      lla=True,  # we use the LLA algorithm by default. If lla=False, we would use FISTA
      ).fit(X, y)
```

We can use the basic penalties as building blocks to create new ones e.g. via overlapping or separable sums of penalties. For example, we might want to penalized some features while leaving others unpenalized.

```python
from yaglm.config.penalty import OverlappingSum, SeparableSum, \
      FusedLasso, NoPenalty
from yaglm.pen_seq import get_sequence_decr_max


# Sometimes we want to put different penalties on different sets of features
# this can be accomplished with the SeparableSum() class
groups = {'no_pen': range(5),  # don't penalized the first 5 features!
          'sparse': range(5, 10)
          }
est = GlmCV(penalty=SeparableSum(groups=groups,
                                 no_pen=NoPenalty(),
                                 sparse=Lasso(flavor=NonConvex())
                                 )
            ).fit(X, y)

# Fit an adaptive sparse-fused lasso using the OverlappingSum() class
# note we have to manually specify the tuning sequence for the fused lasso
pen_val_seq = get_sequence_decr_max(max_val=1, num=10)
fused_config = FusedLasso(flavor=Adaptive()).tune(pen_val_seq=pen_val_seq)

est = GlmCV(penalty=OverlappingSum(fused=fused_config,
                                   sparse=Lasso(flavor=Adaptive())
                                   )
            ).fit(X, y)
```

You can employ your favoirite state of the art optimization algorithm by wrapping it in a solver config object. These objects can also be used to specify optimization parameters (e.g. maximum number of iterations).

```python
from yaglm.solver.FISTA import FISTA  # or your own solver!
# supply your favorite optimization algorithm!
solver = FISTA(max_iter=100)  # specify optimzation parameters in the solvers' init
GlmCV(loss='lin_reg', penalty='lasso', solver=solver)
```


See the [docs/](docs/) folder for additional examples in jupyter notebooks (if they don't load on github try [nbviewer.jupyter.org/](https://nbviewer.jupyter.org/)).


# Help and Support

Additional documentation, examples and code revisions are coming soon.
For questions, issues or feature requests please reach out to Iain:
idc9@cornell.edu.



## Contributing

We welcome contributions to make this a stronger package: data examples,
bug fixes, spelling errors, new features, etc.

# Citation

If you use this package please cite our [arxiv manuscript](https://arxiv.org/abs/2110.05567)


```
@article{carmichael2021yaglm,
  title={yaglm: a Python package for fitting and tuning generalized linear models that supports structured, adaptive and non-convex penalties},
  author={Carmichael, Iain and Keefe , Thomas and Giertych, Naomi and Williams, Jonathan P},
  journal={arXiv preprint arXiv:2110.05567},
  year={2021}
}
```

Some of `yaglm`'s solvers wrap solvers implemented by other software packages. We kindly ask you also cite these underlying packages if you use their solver (see the solver config documentation).

# References


Zou, H., 2006. [The adaptive lasso and its oracle properties](http://users.stat.umn.edu/~zouxx019/Papers/adalasso.pdf). Journal of the American statistical association, 101(476), pp.1418-1429.

Zou, H. and Li, R., 2008. [One-step sparse estimates in nonconcave penalized likelihood models](http://www.personal.psu.edu/ril4/research/AOS0316.pdf). Annals of statistics, 36(4), p.1509.

Beck, A. and Teboulle, M., 2009. [A fast iterative shrinkage-thresholding algorithm for linear inverse problems](https://epubs.siam.org/doi/pdf/10.1137/080716542?casa_token=cjyK5OxcbSoAAAAA:lQOp0YAVKIOv2-vgGUd_YrnZC9VhbgWvZgj4UPbgfw8I7NV44K82vbIu0oz2-xAACBz9k0Lclw). SIAM journal on imaging sciences, 2(1), pp.183-202.

Zhang, Y., Li, R. and Tsai, C.L., 2010. [Regularization parameter selections via generalized information criterion](https://www.tandfonline.com/doi/abs/10.1198/jasa.2009.tm08013). Journal of the American Statistical Association, 105(489), pp.312-323.

Fan, J., Xue, L. and Zou, H., 2014. [Strong oracle optimality of folded concave penalized estimation](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4295817/). Annals of statistics, 42(3), p.819.


Loh, P.L. and Wainwright, M.J., 2017. [Support recovery without incoherence: A case for nonconvex regularization](https://projecteuclid.org/journals/annals-of-statistics/volume-45/issue-6/Support-recovery-without-incoherence-A-case-for-nonconvex-regularization/10.1214/16-AOS1530.pdf). The Annals of Statistics, 45(6), pp.2455-2482.

Reid, S., Tibshirani, R. and Friedman, J., 2016. [A study of error variance estimation in lasso regression](https://www.jstor.org/stable/pdf/24721190.pdf?casa_token=wVML37DFzk4AAAAA:PCPZH8z98S_ZDNMyFxtec9-ZsIx73xoxDgWJUEObeJooVLwMWhOAn_Tnf2GQGL3H36XAROk5P08aNGcDnJUG95ahVwe1F57AsJg0_kxntX4UIoSoEAk). Statistica Sinica, pp.35-67.


Zhu, Y., 2017. [An augmented ADMM algorithm with application to the generalized lasso problem](https://www.tandfonline.com/doi/full/10.1080/10618600.2015.1114491). Journal of Computational and Graphical Statistics, 26(1), pp.195-204.

Yu, G. and Bien, J., 2019. [Estimating the error variance in a high-dimensional linear model](https://academic.oup.com/biomet/article/106/3/533/5498375?casa_token=MSUn8MK2SgYAAAAA:r1tkX7-qUE7RIndcJk4_mfKUcuo3SuPImBy8pLX7H5rTA8cp_-7pUn-XzZzpAJuT_Blr8xmLFjvd). Biometrika, 106(3), pp.533-546.


Liu, X., Zheng, S. and Feng, X., 2020. [Estimation of error variance via ridge regression](https://academic.oup.com/biomet/article/107/2/481/5716270?casa_token=EYC-Z7uyoScAAAAA:6kQhSHg6NJEDWKAgJobCfV_HwNxa5uSWD38hzjW8zUj33n8EUJgzPWuT6yiVUVwmgVMook0oUajW). Biometrika, 107(2), pp.481-488.


Carmichael, I., Keefe, T., Giertych, N., Williams, JP., 2021 [yaglm: a Python package for fitting and tuning generalized linear models that supports structured, adaptive and non-convex penalties](https://arxiv.org/abs/2110.05567). 
