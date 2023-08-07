from numpy import random as npr
import duckdb
from duckdb import typing as ducktypes


def numpy_rand():
    return npr.rand()


def numpy_randn():
    return npr.randn()


def numpy_randint(low, high):
    return npr.randint(low, high)


def numpy_sample():
    return npr.sample()


def numpy_choice(a, p):
    """
    In order to utilise the numpy.random.choice() function, the inputs and outputs need to be formatted in a specific way. 
    Parameters:
        a (Str): a string of the choices in the format "choice1, choice2, choice3" as string will be split on commas(,)
        p (Str): a string of all the choice probabilities, the same length and format as choices. 
    Returns:
        choice (Str): A STRING of the choice from the choices list (a) based on the probability list (p)
    """
    a = a.split(",")
    p = [float(x) for x in p.split(",")]
    choice = npr.choice(a=a, p=p)
    return choice


def numpy_beta(a, b):
    return npr.beta(a, b)


def numpy_binomial(n, p):
    return npr.binomial(n=n, p=p)


def numpy_chisquare(df):
    return npr.chisquare(df=df)


def numpy_dirichlet(alpha):
    """
    In order to use the dirichlet function properly 2+ fields for alpha are needed. 
    alpha in this function needs to be a comma separated string.
    eg. '0.2, 0.4, 0.8' as pvals.
    It also needs to return a string due to SQL not liking variable length arrays

    Parameters:
        alpha (Str): string containing an array of alpha values (see above description)

    Returns:
        output (Str): string containing the array of return values.
    """
    alpha = [float(x) for x in alpha.split(",")]
    samples = npr.dirichlet(alpha=alpha)
    output = ''
    for sample in samples:
        output = output + ',' + str(sample)

    return output[1:]


def numpy_exponential(scale):
    return npr.exponential(scale=scale)


def numpy_f(dfnum, dfden):
    return npr.f(dfnum=dfnum, dfden=dfden)


def numpy_gamma(shape, scale):
    return npr.gamma(shape=shape, scale=scale)


def numpy_geometric(p):
    return npr.geometric(p=p)


def numpy_gumbel(loc, scale):
    return numpy_gumbel(loc=loc, scale=scale)


def numpy_hypergeometric(ngood, nbad, nsamp):
    return npr.hypergeometric(ngood, nbad, nsamp)


def numpy_laplace(loc, scale):
    return npr.laplace(loc=loc, scale=scale)


def numpy_logistic(loc, scale):
    return npr.logistic(loc=loc, scale=scale)


def numpy_lognormal(mean, sigma):
    return npr.lognormal(mean=mean, sigma=sigma)


def numpy_logseries(p):
    return npr.logseries(p=p)


def numpy_multinomial(n, pvals):
    """
    pvals in this function needs to be a comma separated string.
    eg. '0.2, 0.4, 0.8' as pvals 
    """
    pvals = [float(x) for x in pvals.split(",")]
    return npr.multinomial(n=n, pvals=pvals)


def numpy_negative_binomial(n, p):
    return npr.negative_binomial(n=n, p=p)


def numpy_noncentral_chisquare(df, nonc):
    return npr.noncentral_chisquare(df=df, nonc=nonc)


def numpy_noncentral_f(dfnum, dfden, nonc):
    return npr.noncentral_f(dfnum=dfnum, dfden=dfden, nonc=nonc)


def numpy_normal(loc, scale):
    return npr.normal(loc=loc, scale=scale)


def numpy_pareto(a):
    return npr.pareto(a=a)


def numpy_poisson(lam):
    return npr.poisson(lam=lam)


def numpy_power(a):
    return npr.power(a=a)


def numpy_rayleigh(scale):
    return npr.rayleigh(scale=scale)


def numpy_standard_cauchy():
    return npr.standard_cauchy()


def numpy_standard_exponential():
    return npr.standard_exponential()


def numpy_standard_gamma(shape):
    return npr.standard_gamma(shape=shape)


def numpy_standard_normal():
    return npr.standard_normal()


def numpy_standard_t(df):
    return npr.standard_t(df=df)


def numpy_triangular(left, mode, right):
    return npr.triangular(left, mode, right)


def numpy_uniform(low, high):
    return npr.uniform(low=low, high=high)


def numpy_vonmises(mu, kappa):
    return npr.vonmises(mu=mu, kappa=kappa)


def numpy_wald(mean, scale):
    return npr.wald(mean=mean, scale=scale)


def numpy_weibull(a):
    return npr.weibull(a=a)


def numpy_zipf(a):
    return npr.zipf(a=a)


def register_numpy_random_functions(con: duckdb.DuckDBPyConnection) -> None:

    con.create_function(
        name='numpy_rand',
        function=numpy_rand,
        return_type=None,
        parameters=ducktypes.FLOAT,
        side_effects=True,
    )

    con.create_function(
        name='numpy_randn',
        function=numpy_rand,
        return_type=None,
        parameters=ducktypes.FLOAT,
        side_effects=True,
    )

    con.create_function(
        name='numpy_randint',
        function=numpy_randint,
        return_type=[ducktypes.INTEGER, ducktypes.INTEGER],
        parameters=ducktypes.INTEGER,
        side_effects=True,
    )

    con.create_function(
        name='numpy_sample',
        function=numpy_sample,
        return_type=None,
        parameters=ducktypes.FLOAT,
        side_effects=True,
    )

    con.create_function(
        name='numpy_choice',
        function=numpy_choice,
        return_type=[ducktypes.VARCHAR, ducktypes.VARCHAR],
        parameters=ducktypes.VARCHAR,
        side_effects=True,
    )

    con.create_function(
        name='numpy_beta',
        function=numpy_beta,
        return_type=[ducktypes.FLOAT, ducktypes.FLOAT],
        parameters=ducktypes.FLOAT,
        side_effects=True,
    )

    con.create_function(
        name='numpy_binomial',
        function=numpy_binomial,
        return_type=[ducktypes.INTEGER, ducktypes.FLOAT],
        parameters=ducktypes.FLOAT,
        side_effects=True,
    )

    con.create_function(
        name='numpy_chisquare',
        function=numpy_chisquare,
        return_type=[ducktypes.INTEGER],
        parameters=ducktypes.FLOAT,
        side_effects=True,
    )

    con.create_function(
        name='numpy_dirichlet',
        function=numpy_dirichlet,
        return_type=[ducktypes.VARCHAR],
        parameters=ducktypes.VARCHAR,
        side_effects=True,
    )

    con.create_function(
        name='numpy_exponential',
        function=numpy_exponential,
        return_type=[ducktypes.FLOAT],
        parameters=ducktypes.FLOAT,
        side_effects=True,
    )

    con.create_function(
        name='numpy_f',
        function=numpy_f,
        return_type=[ducktypes.FLOAT, ducktypes.FLOAT],
        parameters=ducktypes.FLOAT,
        side_effects=True,
    )

    con.create_function(
        name='numpy_gamma',
        function=numpy_gamma,
        return_type=[ducktypes.FLOAT, ducktypes.FLOAT],
        parameters=ducktypes.FLOAT,
        side_effects=True,
    )

    con.create_function(
        name='numpy_geometric',
        function=numpy_geometric,
        return_type=[ducktypes.FLOAT],
        parameters=ducktypes.FLOAT,
        side_effects=True,
    )

    con.create_function(
        name='numpy_gumbel',
        function=numpy_gumbel,
        return_type=[ducktypes.FLOAT, ducktypes.FLOAT],
        parameters=ducktypes.FLOAT,
        side_effects=True,
    )

    con.create_function(
        name='numpy_hypergeometric',
        function=numpy_hypergeometric,
        return_type=[ducktypes.INTEGER, ducktypes.INTEGER, ducktypes.INTEGER],
        parameters=ducktypes.INTEGER,
        side_effects=True,
    )

    # Last checked here!!

    con.create_function(
        name='numpy_laplace',
        function=numpy_laplace,
        return_type=[ducktypes.FLOAT, ducktypes.FLOAT],
        parameters=ducktypes.FLOAT,
        side_effects=True,
    )

    con.create_function(
        name='numpy_logistic',
        function=numpy_logistic,
        return_type=[ducktypes.FLOAT, ducktypes.FLOAT],
        parameters=ducktypes.FLOAT,
        side_effects=True,
    )

    con.create_function(
        name='numpy_lognormal',
        function=numpy_lognormal,
        return_type=[ducktypes.FLOAT, ducktypes.FLOAT],
        parameters=ducktypes.FLOAT,
        side_effects=True,
    )

    con.create_function(
        name='numpy_logseries',
        function=numpy_logseries,
        return_type=[ducktypes.FLOAT],
        parameters=ducktypes.FLOAT,
        side_effects=True,
    )

    con.create_function(
        name='numpy_multinomial',
        function=numpy_multinomial,
        return_type=[ducktypes.FLOAT, ducktypes.VARCHAR],
        parameters=ducktypes.FLOAT,
        side_effects=True,
    )

    con.create_function(
        name='numpy_negative_binomial',
        function=numpy_negative_binomial,
        return_type=[ducktypes.FLOAT, ducktypes.FLOAT],
        parameters=ducktypes.FLOAT,
        side_effects=True,
    )

    con.create_function(
        name='numpy_noncentral_chisquare',
        function=numpy_noncentral_chisquare,
        return_type=[ducktypes.FLOAT, ducktypes.FLOAT],
        parameters=ducktypes.FLOAT,
        side_effects=True,
    )

    con.create_function(
        name='numpy_noncentral_f',
        function=numpy_noncentral_f,
        return_type=[ducktypes.FLOAT, ducktypes.FLOAT, ducktypes.FLOAT],
        parameters=ducktypes.FLOAT,
        side_effects=True,
    )

    con.create_function(
        name='numpy_normal',
        function=numpy_normal,
        return_type=[ducktypes.FLOAT, ducktypes.FLOAT],
        parameters=ducktypes.FLOAT,
        side_effects=True,
    )

    con.create_function(
        name='numpy_pareto',
        function=numpy_pareto,
        return_type=[ducktypes.FLOAT],
        parameters=ducktypes.FLOAT,
        side_effects=True,
    )

    con.create_function(
        name='numpy_poisson',
        function=numpy_poisson,
        return_type=[ducktypes.FLOAT],
        parameters=ducktypes.FLOAT,
        side_effects=True,
    )

    con.create_function(
        name='numpy_power',
        function=numpy_power,
        return_type=[ducktypes.FLOAT],
        parameters=ducktypes.FLOAT,
        side_effects=True,
    )

    con.create_function(
        name='numpy_rayleigh',
        function=numpy_rayleigh,
        return_type=[ducktypes.FLOAT],
        parameters=ducktypes.FLOAT,
        side_effects=True,
    )

    con.create_function(
        name='numpy_standard_cauchy',
        function=numpy_standard_cauchy,
        return_type=[],
        parameters=ducktypes.FLOAT,
        side_effects=True,
    )

    con.create_function(
        name='numpy_standard_exponential',
        function=numpy_standard_exponential,
        return_type=[],
        parameters=ducktypes.FLOAT,
        side_effects=True,
    )

    con.create_function(
        name='numpy_standard_gamma',
        function=numpy_standard_gamma,
        return_type=[ducktypes.FLOAT],
        parameters=ducktypes.FLOAT,
        side_effects=True,
    )

    con.create_function(
        name='numpy_standard_normal',
        function=numpy_standard_normal,
        return_type=[],
        parameters=ducktypes.FLOAT,
        side_effects=True,
    )

    con.create_function(
        name='numpy_standard_t',
        function=numpy_standard_t,
        return_type=[ducktypes.FLOAT],
        parameters=ducktypes.FLOAT,
        side_effects=True,
    )

    con.create_function(
        name='numpy_triangular',
        function=numpy_triangular,
        return_type=[ducktypes.FLOAT, ducktypes.FLOAT, ducktypes.FLOAT],
        parameters=ducktypes.FLOAT,
        side_effects=True,
    )

    con.create_function(
        name='numpy_uniform',
        function=numpy_uniform,
        return_type=[ducktypes.FLOAT, ducktypes.FLOAT],
        parameters=ducktypes.FLOAT,
        side_effects=True,
    )

    con.create_function(
        name='numpy_vonmises',
        function=numpy_vonmises,
        return_type=[ducktypes.FLOAT, ducktypes.FLOAT],
        parameters=ducktypes.FLOAT,
        side_effects=True,
    )

    con.create_function(
        name='numpy_wald',
        function=numpy_wald,
        return_type=[ducktypes.FLOAT, ducktypes.FLOAT],
        parameters=ducktypes.FLOAT,
        side_effects=True,
    )

    con.create_function(
        name='numpy_weibull',
        function=numpy_weibull,
        return_type=[ducktypes.FLOAT],
        parameters=ducktypes.FLOAT,
        side_effects=True,
    )

    con.create_function(
        name='numpy_zipf',
        function=numpy_zipf,
        return_type=[ducktypes.FLOAT],
        parameters=ducktypes.FLOAT,
        side_effects=True,
    )
