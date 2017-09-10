#!python 
from __future__ import division,print_function
import numpy as np
from typyPRISM.core.PRISM import PRISM
from typyPRISM.core.MatrixArray import MatrixArray
from typyPRISM.core.PairTable import PairTable
from typyPRISM.core.ValueTable import ValueTable
from typyPRISM.core.Space import Space
from typyPRISM.core.Density import Density

from typyPRISM.closure.AtomicClosure import AtomicClosure
from typyPRISM.closure.MolecularClosure import MolecularClosure

class System:
    '''Primary class used to spawn PRISM calculations
    
    .. warning::
    
        The *intra*-molecular correlation functions (omega attribute)
        should be specified such that they are in Fourier space and such
        that their k->0 values approach the total number of sites in a 
        given molecule for the self (i==j) pairs.
    
    Attributes
    ----------
    types: list
        list of site types
        
    rank: int
        number of site types
    
    density: typyPRISM.Density
        Container for all density values
        
    potential: typyPRISM.PairTable
        Table of pair potentials between all site pairs in real space
        
    closure: typyPRISM.PairTable
        Table of closures between all site pairs
        
    omega: typyPRISM.PairTable
        Table of omega correlation functions in k-space
    
    domain: typyPRISM.Domain
        Domain object which specifies the Real and Fourier space 
        solution grid.
        
    kT: float
        Value of the thermal energy scale. Used to vary temperature and
        scale the potential energy functions.

    diameter: typyPRISM.ValueTable
        Site diameters. Note that these are not passed to potentials and it
        is up to the user to set sane \sigma values that match these 
        diameters. 
    
    
    '''
    def __init__(self,types,kT=1.0):
        self.types = types
        self.rank  = len(types)
        self.kT = kT
        
        self.domain    = None
        self.diameter  = ValueTable(types,'diameter')
        self.density   = Density(types)
        self.potential = PairTable(types,'potential')
        self.closure   = PairTable(types,'closure')
        self.omega = PairTable(types,'omega')

    def check(self):
        '''Make sure all values in the system are specified'''
        for table in [self.density,self.potential,self.closure,self.omega,self.diameter]:
            table.check()
        
        if self.domain is None:
            raise ValueError(('System has no domain! '
                              'User must instatiate and assign a domain to the system!'))
    def createPRISM(self):
        '''Construct a fully specified PRISM object that can be solved'''
        self.check() #sanity check
        
        # Need to set the potential for each closure object
        for (i,j),(t1,t2),U in self.potential.iterpairs():
            if isinstance(self.closure[t1,t2],AtomicClosure):
                self.closure[t1,t2].potential = U.calculate(self.domain.r) / self.kT
            elif isinstance(self.closure[t1,t2],MolecularClosure):
                raise NotImplementedError('Molecular closures are not fully implemented in this release.')
                self.closure[t1,t2].potential = U.calculate_attractive(self.domain.r) / self.kT

        return PRISM(self)
        
