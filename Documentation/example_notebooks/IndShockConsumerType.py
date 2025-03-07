# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: collapsed,code_folding,heading_collapsed,hidden
#     cell_metadata_json: true
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.15.2
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # IndShockConsumerType Documentation
# ## Consumption-Saving model with Idiosyncratic Income Shocks

# %% {"code_folding": [0]}
# Initial imports and notebook setup, click arrow to show
from HARK.ConsumptionSaving.ConsIndShockModel import IndShockConsumerType
from HARK.utilities import plot_funcs_der, plot_funcs
import matplotlib.pyplot as plt
import numpy as np

mystr = lambda number: "{:.4f}".format(number)

# %% [markdown]
# The module `HARK.ConsumptionSaving.ConsIndShockModel` concerns consumption-saving models with idiosyncratic shocks to (non-capital) income.  All of the models assume CRRA utility with geometric discounting, no bequest motive, and income shocks are fully transitory or fully permanent.
#
# `ConsIndShockModel` includes:
# 1. A very basic "perfect foresight" model with no uncertainty.
# 2. A model with risk over transitory and permanent income shocks.
# 3. The model described in (2), with an interest rate for debt that differs from the interest rate for savings.
#
# This notebook provides documentation for the second of these models.
# $\newcommand{\CRRA}{\rho}$
# $\newcommand{\DiePrb}{\mathsf{D}}$
# $\newcommand{\PermGroFac}{\Gamma}$
# $\newcommand{\Rfree}{\mathsf{R}}$
# $\newcommand{\DiscFac}{\beta}$

# %% [markdown]
# ## Statement of idiosyncratic income shocks model
#
# Suppose we want to solve a model like the one analyzed in [BufferStockTheory](http://www.econ2.jhu.edu/people/ccarroll/papers/BufferStockTheory/), which has all the same features as the perfect foresight consumer, plus idiosyncratic shocks to income each period.  Agents with this kind of model are represented by the class `IndShockConsumerType`.
#
# Specifically, this type of consumer receives two income shocks at the beginning of each period: a completely transitory shock $\newcommand{\tShkEmp}{\theta}{\tShkEmp_t}$ and a completely permanent shock $\newcommand{\pShk}{\psi}{\pShk_t}$.  Moreover, the agent is subject to borrowing a borrowing limit: the ratio of end-of-period assets $A_t$ to permanent income $P_t$ must be greater than $\underline{a}$.  As with the perfect foresight problem, this model is stated in terms of *normalized* variables, dividing all real variables by $P_t$:
#
# \begin{eqnarray*}
# v_t(m_t) &=& \max_{c_t} {~} u(c_t) + \DiscFac (1-\DiePrb_{t+1})  \mathbb{E}_{t} \left[ (\PermGroFac_{t+1}\psi_{t+1})^{1-\CRRA} v_{t+1}(m_{t+1}) \right], \\
# a_t &=& m_t - c_t, \\
# a_t &\geq& \text{$\underline{a}$}, \\
# m_{t+1} &=& \Rfree/(\PermGroFac_{t+1} \psi_{t+1}) a_t + \theta_{t+1}, \\
# (\psi_{t+1},\theta_{t+1}) &\sim& F_{t+1}, \\
# \mathbb{E}[\psi]=\mathbb{E}[\theta] &=& 1, \\
# u(c) &=& \frac{c^{1-\rho}}{1-\rho}.
# \end{eqnarray*}

# %% [markdown]
# ## Solution method for IndShockConsumerType
#
# With the introduction of (non-trivial) risk, the idiosyncratic income shocks model has no closed form solution and must be solved numerically.  The function `solveConsIndShock` solves the one period problem for the `IndShockConsumerType` class.  To do so, HARK uses the original version of the endogenous grid method (EGM) first described [here](http://www.econ2.jhu.edu/people/ccarroll/EndogenousGridpoints.pdf); see also the [SolvingMicroDSOPs](http://www.econ2.jhu.edu/people/ccarroll/SolvingMicroDSOPs/) lecture notes. <!--- <cite data-cite="6202365/HQ6H9JEI"></cite> -->
#
# Briefly, the transition equation for $m_{t+1}$ can be substituted into the problem definition; the second term of the reformulated maximand represents "end of period value of assets" $\mathfrak{v}_t(a_t)$ ("Gothic v"):
#
# \begin{eqnarray*}
# v_t(m_t) &=& \max_{c_t} {~} u(c_t) + \underbrace{\DiscFac (1-\DiePrb_{t+1})  \mathbb{E}_{t} \left[ (\PermGroFac_{t+1}\psi_{t+1})^{1-\CRRA} v_{t+1}(\Rfree/(\PermGroFac_{t+1} \psi_{t+1}) a_t + \theta_{t+1}) \right]}_{\equiv \mathfrak{v}_t(a_t)}.
# \end{eqnarray*}
#
# The first order condition with respect to $c_t$ is thus simply:
#
# \begin{eqnarray*}
# u^{\prime}(c_t) - \mathfrak{v}'_t(a_t) = 0 \Longrightarrow c_t^{-\CRRA} = \mathfrak{v}'_t(a_t) \Longrightarrow c_t = \mathfrak{v}'_t(a_t)^{-1/\CRRA},
# \end{eqnarray*}
#
# and the marginal value of end-of-period assets can be computed as:
#
# \begin{eqnarray*}
# \mathfrak{v}'_t(a_t) = \DiscFac (1-\DiePrb_{t+1})  \mathbb{E}_{t} \left[ \Rfree (\PermGroFac_{t+1}\psi_{t+1})^{-\CRRA} v'_{t+1}(\Rfree/(\PermGroFac_{t+1} \psi_{t+1}) a_t + \theta_{t+1}) \right].
# \end{eqnarray*}
#
# To solve the model, we choose an exogenous grid of $a_t$ values that span the range of values that could plausibly be achieved, compute $\mathfrak{v}'_t(a_t)$ at each of these points, calculate the value of consumption $c_t$ whose marginal utility is consistent with the marginal value of assets, then find the endogenous $m_t$ gridpoint as $m_t = a_t + c_t$.  The set of $(m_t,c_t)$ gridpoints is then interpolated to construct the consumption function.

# %% [markdown]
# ## Example parameter values to construct an instance of IndShockConsumerType
#
# In order to create an instance of `IndShockConsumerType`, the user must specify parameters that characterize the (age-varying) distribution of income shocks $F_{t+1}$, the artificial borrowing constraint $\underline{a}$, and the exogenous grid of end-of-period assets-above-minimum for use by EGM, along with all of the parameters for the perfect foresight model.  The table below presents the complete list of parameter values required to instantiate an `IndShockConsumerType`, along with example values.
#
# | Parameter | Description | Code | Example value | Time-varying? |
# | :---: | --- | --- | --- | --- |
# | $\DiscFac$ |Intertemporal discount factor  | $\texttt{DiscFac}$ | $0.96$ |  |
# | $\CRRA$|Coefficient of relative risk aversion | $\texttt{CRRA}$ | $2.0$ | |
# | $\Rfree$ | Risk free interest factor | $\texttt{Rfree}$ | $1.03$ | |
# | $1 - \DiePrb_{t+1}$ |Survival probability | $\texttt{LivPrb}$ | $[0.98]$ | $\surd$ |
# |$\PermGroFac_{t+1}$|Permanent income growth factor|$\texttt{PermGroFac}$| $[1.01]$ | $\surd$ |
# | $\sigma_\psi$| Standard deviation of log permanent income shocks | $\texttt{PermShkStd}$ | $[0.1]$ |$\surd$ |
# | $N_\psi$| Number of discrete permanent income shocks | $\texttt{PermShkCount}$ | $7$ | |
# | $\sigma_\theta$| Standard deviation of log transitory income shocks | $\texttt{TranShkStd}$ | $[0.2]$ | $\surd$ |
# | $N_\theta$| Number of discrete transitory income shocks | $\texttt{TranShkCount}$ | $7$ |  |
# | $\mho$ | Probability of being unemployed and getting $\theta=\underline{\theta}$ | $\texttt{UnempPrb}$ | $0.05$ |  |
# | $\underline{\theta}$| Transitory shock when unemployed | $\texttt{IncUnemp}$ | $0.3$ |  |
# | $\mho^{Ret}$ | Probability of being "unemployed" when retired | $\texttt{UnempPrb}$ | $0.0005$ |  |
# | $\underline{\theta}^{Ret}$| Transitory shock when "unemployed" and retired | $\texttt{IncUnemp}$ | $0.0$ |  |
# | $(none)$ | Period of the lifecycle model when retirement begins | $\texttt{T_retire}$ | $0$ | |
# | $(none)$ | Minimum value in assets-above-minimum grid | $\texttt{aXtraMin}$ | $0.001$ | |
# | $(none)$ | Maximum value in assets-above-minimum grid | $\texttt{aXtraMax}$ | $20.0$ | |
# | $(none)$ | Number of points in base assets-above-minimum grid | $\texttt{aXtraCount}$ | $48$ | |
# | $(none)$ | Exponential nesting factor for base assets-above-minimum grid | $\texttt{aXtraNestFac}$ | $3$ | |
# | $(none)$ | Additional values to add to assets-above-minimum grid | $\texttt{aXtraExtra}$ | $None$ | |
# | $\underline{a}$| Artificial borrowing constraint (normalized) | $\texttt{BoroCnstArt}$ | $0.0$ | |
# | $(none)$|Indicator for whether $\texttt{vFunc}$ should be computed | $\texttt{vFuncBool}$ | $True$ | |
# | $(none)$ |Indicator for whether $\texttt{cFunc}$ should use cubic splines | $\texttt{CubicBool}$ | $False$ |  |
# |$T$| Number of periods in this type's "cycle" |$\texttt{T_cycle}$| $1$ | |
# |(none)| Number of times the "cycle" occurs |$\texttt{cycles}$| $0$ | |

# %% {"code_folding": [0]}
IdiosyncDict = {
    # Parameters shared with the perfect foresight model
    "CRRA": 2.0,  # Coefficient of relative risk aversion
    "Rfree": 1.03,  # Interest factor on assets
    "DiscFac": 0.96,  # Intertemporal discount factor
    "LivPrb": [0.98],  # Survival probability
    "PermGroFac": [1.01],  # Permanent income growth factor
    # Parameters that specify the income distribution over the lifecycle
    "PermShkStd": [0.1],  # Standard deviation of log permanent shocks to income
    "PermShkCount": 7,  # Number of points in discrete approximation to permanent income shocks
    "TranShkStd": [0.2],  # Standard deviation of log transitory shocks to income
    "TranShkCount": 7,  # Number of points in discrete approximation to transitory income shocks
    "UnempPrb": 0.05,  # Probability of unemployment while working
    "IncUnemp": 0.3,  # Unemployment benefits replacement rate
    "UnempPrbRet": 0.0005,  # Probability of "unemployment" while retired
    "IncUnempRet": 0.0,  # "Unemployment" benefits when retired
    "T_retire": 0,  # Period of retirement (0 --> no retirement)
    "tax_rate": 0.0,  # Flat income tax rate (legacy parameter, will be removed in future)
    # Parameters for constructing the "assets above minimum" grid
    "aXtraMin": 0.001,  # Minimum end-of-period "assets above minimum" value
    "aXtraMax": 20,  # Maximum end-of-period "assets above minimum" value
    "aXtraCount": 48,  # Number of points in the base grid of "assets above minimum"
    "aXtraNestFac": 3,  # Exponential nesting factor when constructing "assets above minimum" grid
    "aXtraExtra": [None],  # Additional values to add to aXtraGrid
    # A few other paramaters
    "BoroCnstArt": 0.0,  # Artificial borrowing constraint; imposed minimum level of end-of period assets
    "vFuncBool": True,  # Whether to calculate the value function during solution
    "CubicBool": False,  # Preference shocks currently only compatible with linear cFunc
    "T_cycle": 1,  # Number of periods in the cycle for this agent type
    # Parameters only used in simulation
    "AgentCount": 10000,  # Number of agents of this type
    "T_sim": 120,  # Number of periods to simulate
    "aNrmInitMean": -6.0,  # Mean of log initial assets
    "aNrmInitStd": 1.0,  # Standard deviation of log initial assets
    "pLvlInitMean": 0.0,  # Mean of log initial permanent income
    "pLvlInitStd": 0.0,  # Standard deviation of log initial permanent income
    "PermGroFacAgg": 1.0,  # Aggregate permanent income growth factor
    "T_age": None,  # Age after which simulated agents are automatically killed
}

# %% [markdown]
# The distribution of permanent income shocks is specified as mean one lognormal, with an age-varying (underlying) standard deviation. The distribution of transitory income shocks is also mean one lognormal, but with an additional point mass representing unemployment; the transitory shocks are adjusted so that the distribution is still mean one.  The continuous distributions are discretized with an equiprobable distribution.
#
# Optionally, the user can specify the period when the individual retires and escapes essentially all income risk as `T_retire`; this can be turned off by setting the parameter to $0$.  In retirement, all permanent income shocks are turned off, and the only transitory shock is an "unemployment" shock, likely with small probability; this prevents the retired problem from degenerating into a perfect foresight model.
#
# The grid of assets above minimum $\texttt{aXtraGrid}$ is specified by its minimum and maximum level, the number of gridpoints, and the extent of exponential nesting.  The greater the (integer) value of $\texttt{aXtraNestFac}$, the more dense the gridpoints will be at the bottom of the grid (and more sparse near the top); setting $\texttt{aXtraNestFac}$ to $0$ will generate an evenly spaced grid of $a_t$.
#
# The artificial borrowing constraint $\texttt{BoroCnstArt}$ can be set to `None` to turn it off.
#
# It is not necessary to compute the value function in this model, and it is not computationally free to do so.  You can choose whether the value function should be calculated and returned as part of the solution of the model with $\texttt{vFuncBool}$.  The consumption function will be constructed as a piecewise linear interpolation when $\texttt{CubicBool}$ is `False`, and will be a piecewise cubic spline interpolator if `True`.

# %% [markdown] {"heading_collapsed": true}
# ## Solving and examining the solution of the idiosyncratic income shocks model
#
# The cell below creates an infinite horizon instance of `IndShockConsumerType` and solves its model by calling its `solve` method.

# %% {"hidden": true}
IndShockExample = IndShockConsumerType(**IdiosyncDict)
IndShockExample.assign_parameters(CubicBool = False)
IndShockExample.cycles = 0  # Make this type have an infinite horizon
IndShockExample.solve()


# %% [markdown] {"hidden": true}
# After solving the model, we can examine an element of this type's $\texttt{solution}$:

# %% {"hidden": true}
print(vars(IndShockExample.solution[0]))

# %% [markdown] {"hidden": true}
# The single-period solution to an idiosyncratic shocks consumer's problem has all of the same attributes as in the perfect foresight model, with a couple additions.  The solution can include the marginal marginal value of market resources function $\texttt{vPPfunc}$, but this is only constructed if $\texttt{CubicBool}$ is `True`, so that the MPC can be accurately computed; when it is `False`, then $\texttt{vPPfunc}$ merely returns `NaN` everywhere.
#
# The `solveConsIndShock` function calculates steady state market resources and stores it in the attribute $\texttt{mNrmSS}$.  This represents the steady state level of $m_t$ if *this period* were to occur indefinitely, but with income shocks turned off.  This is relevant in a "one period infinite horizon" model like we've specified here, but is less useful in a lifecycle model.
#
# Let's take a look at the consumption function by plotting it, along with its derivative (the MPC):

# %% {"hidden": true}
print("Consumption function for an idiosyncratic shocks consumer type:")
plt.plot(np.arange(0,1.5,.1),np.arange(0,1.5,.1), color = 'black', ls = '--')
plot_funcs(IndShockExample.solution[0].cFunc, IndShockExample.solution[0].mNrmMin, 5)
print("Marginal propensity to consume for an idiosyncratic shocks consumer type:")
plot_funcs_der(
    IndShockExample.solution[0].cFunc, IndShockExample.solution[0].mNrmMin, 5
)

# %% [markdown] {"hidden": true}
# The lower part of the consumption function is linear with a slope of 1, representing the *constrained* part of the consumption function where the consumer *would like* to consume more by borrowing-- his marginal utility of consumption exceeds the marginal value of assets-- but he is prevented from doing so by the artificial borrowing constraint.
#
# The MPC is a step function, as the $\texttt{cFunc}$ itself is a piecewise linear function; note the large jump in the MPC where the borrowing constraint begins to bind.
#
# If you want to look at the interpolation nodes for the consumption function, these can be found by "digging into" attributes of $\texttt{cFunc}$:

# %% {"hidden": true}
print(
    "mNrmGrid for unconstrained cFunc is ",
    IndShockExample.solution[0].cFunc.functions[0].x_list,
)
print(
    "cNrmGrid for unconstrained cFunc is ",
    IndShockExample.solution[0].cFunc.functions[0].y_list,
)
print(
    "mNrmGrid for borrowing constrained cFunc is ",
    IndShockExample.solution[0].cFunc.functions[1].x_list,
)
print(
    "cNrmGrid for borrowing constrained cFunc is ",
    IndShockExample.solution[0].cFunc.functions[1].y_list,
)

# %% [markdown] {"hidden": true}
# The consumption function in this model is an instance of `LowerEnvelope1D`, a class that takes an arbitrary number of 1D interpolants as arguments to its initialization method.  When called, a `LowerEnvelope1D` evaluates each of its component functions and returns the lowest value.  Here, the two component functions are the *unconstrained* consumption function-- how the agent would consume if the artificial borrowing constraint did not exist for *just this period*-- and the *borrowing constrained* consumption function-- how much he would consume if the artificial borrowing constraint is binding.
#
# The *actual* consumption function is the lower of these two functions, pointwise.  We can see this by plotting the component functions on the same figure:

# %% {"hidden": true}
plot_funcs(IndShockExample.solution[0].cFunc.functions, -0.25, 5.0)

# %% [markdown]
# ## Simulating the idiosyncratic income shocks model
#
# In order to generate simulated data, an instance of `IndShockConsumerType` needs to know how many agents there are that share these particular parameters (and are thus *ex ante* homogeneous), the distribution of states for newly "born" agents, and how many periods to simulate.  These simulation parameters are described in the table below, along with example values.
#
# | Description | Code | Example value |
# | :---: | --- | --- |
# | Number of consumers of this type | $\texttt{AgentCount}$ | $10000$ |
# | Number of periods to simulate | $\texttt{T_sim}$ | $120$ |
# | Mean of initial $\textbf{log}$ (normalized) assets | $\texttt{aNrmInitMean}$ | $-6.0$ |
# | Stdev of initial $\textbf{log}$  (normalized) assets | $\texttt{aNrmInitStd}$ | $1.0$ |
# | Mean of initial $\textbf{log}$ permanent income | $\texttt{pLvlInitMean}$ | $0.0$ |
# | Stdev of initial $\textbf{log}$ permanent income | $\texttt{pLvlInitStd}$ | $0.0$ |
# | Aggregrate productivity growth factor | $\texttt{PermGroFacAgg}$ | $1.0$ |
# | Age after which consumers are automatically killed | $\texttt{T_age}$ | $None$ |
#
# Here, we will simulate 10,000 consumers for 120 periods.  All newly born agents will start with permanent income of exactly $P_t = 1.0 = \exp(\texttt{pLvlInitMean})$, as $\texttt{pLvlInitStd}$ has been set to zero; they will have essentially zero assets at birth, as $\texttt{aNrmInitMean}$ is $-6.0$; assets will be less than $1\%$ of permanent income at birth.
#
# These example parameter values were already passed as part of the parameter dictionary that we used to create `IndShockExample`, so it is ready to simulate.  We need to set the `track_vars` attribute to indicate the variables for which we want to record a *history*.

# %%
np.exp(-6)

# %%
IndShockExample.track_vars = ["aNrm", "mNrm", "cNrm", "pLvl"]
IndShockExample.initialize_sim()
IndShockExample.simulate()


# %% [markdown]
# We can now look at the simulated data in aggregate or at the individual consumer level.  Like in the perfect foresight model, we can plot average (normalized) market resources over time, as well as average consumption:

# %%

# %% {"code_folding": []}
# Define the saving rate function
def savRteFunc(SomeType, m, t):
    """
    Parameters:
    ----------
        SomeType:
             Agent type that has been solved and simulated.
        m:
            normalized market resources of agent
        t:
            age of agent (from starting in the workforce)


    Returns:
    --------
        savRte: float

    """
    inc = (SomeType.Rfree - 1.0) * (
        m - 1.0
    ) + 1.0  # Normalized by permanent labor income
    cns = SomeType.solution[t].cFunc(m)  # Consumption (normalized)
    sav = inc - cns  # Flow of saving this period
    savRte = sav / inc  # Saving Rate
    return savRte


# %%
IndShockExample.history["mNrm"].shape

# %%
IndShockExample.solution[0].cFunc(2)

# %%
np.mean([savRteFunc(IndShockExample, IndShockExample.history["mNrm"][t], 0) for t in range(120)], axis = 1)

# %%
plt.plot(np.mean(IndShockExample.history["mNrm"], axis=1))
plt.xlabel("Time")
plt.ylabel("Mean market resources")
plt.show()

plt.plot(np.mean(IndShockExample.history["cNrm"], axis=1))
plt.xlabel("Time")
plt.ylabel("Mean consumption")
plt.show()


plt.plot(np.mean([savRteFunc(IndShockExample, IndShockExample.history["mNrm"][t], 0) for t in range(120)], axis = 1))
plt.xlabel("Time")
plt.ylabel("Mean saving rate ")
plt.show()


# %% [markdown]
# We could also plot individual consumption paths for some of the consumers-- say, the first five:

# %%
plt.plot(IndShockExample.history["cNrm"][:, 0:5])
plt.xlabel("Time")
plt.ylabel("Individual consumption paths")
plt.show()

# %%
