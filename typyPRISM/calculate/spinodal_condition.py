#!python

from __future__ import division,print_function
from typyPRISM.core.MatrixArray import MatrixArray
from typyPRISM.core.Space import Space
from typyPRISM.core.PairTable import PairTable
import numpy as np

def spinodal_condition(PRISM,extrapolate=True):
    '''Calculate the spinodal condition between pairs of components 

        
    Parameters
    ----------
    PRISM: typyPRISM.core.PRISM
        A **solved** PRISM object.

    extrapolate: bool, *optional*
        If True, only return the value extrapolated to :math:`k=0` rather than
        reporting the value at the lowest-k
    
    Returns
    -------
    lambda: typyPRISM.core.MatrixArray
        The full MatrixArray of structure factors

        
    **Mathematical Definition**


    .. math::

        \hat{s}_{\alpha,\beta}(k) = \rho^{site}_{\alpha,\beta} \hat{\omega}_{\alpha,\beta}(k) + \rho^{pair}_{\alpha,\beta} \hat{h}_{\alpha,\beta}(k)

    
    **Variable Definitions**

        - :math:`\hat{\omega}_{\alpha,\beta}(k)`
            Intra-molecular correlation function between sites :math:`\alpha`
            and :math:`\beta` at a wavenumber :math:`k`

        - :math:`\hat{h}_{\alpha,\beta}(k)`
            Total correlation function between sites :math:`\alpha` and
            :math:`\beta` at a wavenumber :math:`k`

        - :math:`\rho^{site}_{\alpha,\beta}`, :math:`\rho^{pair}_{\alpha,\beta}`
            Sitewise and pairwise densities for sites :math:`\alpha` and
            :math:`\beta`. See :class:`typyPRISM.core.Density` for details. 

    **Description**

        To be added...


    .. warning::

        Passing an unsolved PRISM object to this function will still produce
        output based on the default values of the attributes of the PRISM
        object.

    References
    ----------
    Schweizer, Curro, Thermodynamics of Polymer Blends,
    J. Chem. Phys., 1989 91 (8) 5059
    

    Example
    -------
    .. code-block:: python

        import typyPRISM

        sys = typyPRISM.System(['A','B'])

        # ** populate system variables **
        
        PRISM = sys.createPRISM()

        PRISM.solve()

        sk = typyPRISM.calculate.structure_factor(PRISM)

        sk_BB = sk['B','B']
    
    
    '''
    
    assert PRISM.sys.rank>1,'The spinodal calculation is only valid for multicomponent systems'
    
    if PRISM.directCorr.space == Space.Real:
        PRISM.sys.domain.MatrixArray_to_fourier(PRISM.directCorr)

    if PRISM.omega.space == Space.Real:
        PRISM.sys.domain.MatrixArray_to_fourier(PRISM.omega)
        
    
    lam = PairTable(name='spinodal_condition',types=PRISM.sys.types)
    for i,t1 in enumerate(PRISM.sys.types):
        for j,t2 in enumerate(PRISM.sys.types):
            if i<j:

                omega_AA  = PRISM.omega[t1,t1]
                omega_AB  = PRISM.omega[t1,t2]
                omega_BB  = PRISM.omega[t2,t2]

                C_AA = PRISM.directCorr[t1,t1]
                C_AB = PRISM.directCorr[t1,t2]
                C_BB = PRISM.directCorr[t2,t2]

                rho_AA = PRISM.sys.density.site[t1,t1]
                rho_AB = PRISM.sys.density.site[t1,t2]
                rho_BB = PRISM.sys.density.site[t2,t2]

                curve  = +1
                curve += -1*C_AA * rho_AA * omega_AA
                curve += -2*C_AB * rho_AB * omega_AB
                curve += -1*C_BB * rho_BB * omega_BB
                curve += +C_AB*C_AB * rho_AB*rho_AB * omega_AB*omega_AB
                curve += -C_AA*C_BB * rho_AB*rho_AB * omega_AB*omega_AB
                curve += -C_AB*C_AB * rho_AA*rho_BB * omega_AA*omega_BB
                curve += +C_AA*C_BB * rho_AA*rho_BB * omega_AA*omega_BB

                fit = np.poly1d(np.polyfit(PRISM.sys.domain.k[:3],curve[:3],2))
                
                lam[t1,t2] = fit(0)
                  
        
    
    return lam