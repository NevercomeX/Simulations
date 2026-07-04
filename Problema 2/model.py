# -*- coding: utf-8 -*-
"""
Motor de Simulación Termodinámica y Cinética para la Hidrogenación de Nitrobenceno
Autor: Antigravity AI
"""

import numpy as np
from thermo import Chemical
from scipy.optimize import brentq

# Constante de los gases ideales (J / (mol*K))
R = 8.3144

class NitrobenzeneSimulator:
    def __init__(self):
        """
        Inicializa las especies químicas de la reacción:
        C6H5NO2 (NB) + 3 H2 -> C6H5NH2 (Aniline) + 2 H2O
        """
        self.nb = Chemical('nitrobenzene')
        self.h2 = Chemical('hydrogen')
        self.ani = Chemical('aniline')
        self.h2o = Chemical('water')
        
        self.species = [self.nb, self.h2, self.ani, self.h2o]
        self.names = ['Nitrobenceno', 'Hidrógeno', 'Anilina', 'Agua']
        self.formulas = ['C6H5NO2', 'H2', 'C6H5NH2', 'H2O']
        self.nu = np.array([-1, -3, 1, 2])
        
        self.Hfgm = np.array([c.Hfgm for c in self.species]) # J/mol Gas
        self.Hfm = np.array([c.Hfm for c in self.species])   # J/mol fases estables
        
        # Entalpinas estándar de reacción a 298.15 K
        self.dH_rxn_std_gas = np.sum(self.nu * self.Hfgm)
        self.dH_rxn_std_stable = np.sum(self.nu * self.Hfm)
        
    def calculate_balance(self, F_NB0, H2_ratio, X):
        """
        Calcula el balance de materia (kmol/h) a partir del flujo de alimentación y conversión.
        """
        F_H20 = H2_ratio * F_NB0
        F0 = np.array([F_NB0, F_H20, 0.0, 0.0])
        xi = X * F_NB0 # kmol/h
        F = F0 + self.nu * xi
        F_total = np.sum(F)
        y = F / F_total
        return F0, F, y
        
    def calculate_thermodynamics(self, T_in_C, P_react_kPa, F_NB0, H2_ratio, X):
        """
        Calcula las entalpías de reacción y el calor necesario para el reactor isotérmico.
        """
        T_in = T_in_C + 273.15
        P_react = P_react_kPa * 1000.0
        
        # Calor de reacción a T_in (Gas Ideal)
        dH_rxn_ideal_Tin = self.dH_rxn_std_gas + np.sum(
            self.nu * np.array([c.HeatCapacityGas.T_dependent_property_integral(298.15, T_in) for c in self.species])
        )
        
        # Calor de reacción a T_in (Gas Real - Peng-Robinson)
        try:
            chems_in = [Chemical(c.CAS, T=T_in, P=P_react) for c in self.species]
            dH_rxn_real_Tin = self.dH_rxn_std_stable + np.sum(self.nu * np.array([c.Hm for c in chems_in]))
        except Exception:
            dH_rxn_real_Tin = dH_rxn_ideal_Tin
            chems_in = None
            
        xi = X * F_NB0 # kmol/h
        xi_mol_s = xi * 1000.0 / 3600.0
        Q_isothermal_ideal = xi_mol_s * dH_rxn_ideal_Tin / 1000.0 # kW
        Q_isothermal_real = xi_mol_s * dH_rxn_real_Tin / 1000.0 # kW
        
        return dH_rxn_ideal_Tin, dH_rxn_real_Tin, Q_isothermal_ideal, Q_isothermal_real, chems_in

    def solve_adiabatic(self, T_in_C, P_react_kPa, F_NB0, H2_ratio, X, chems_in=None):
        """
        Resuelve los balances de energía para calcular la temperatura de salida en reactor adiabático.
        """
        T_in = T_in_C + 273.15
        P_react = P_react_kPa * 1000.0
        
        F0, F, _ = self.calculate_balance(F_NB0, H2_ratio, X)
        
        # Entalpía total de entrada (J/h)
        H_in_ideal = np.sum(F0 * (self.Hfgm + np.array([c.HeatCapacityGas.T_dependent_property_integral(298.15, T_in) for c in self.species])))
        
        if chems_in is not None:
            H_in_real = np.sum(F0 * (self.Hfm + np.array([c.Hm for c in chems_in])))
        else:
            try:
                chems_in = [Chemical(c.CAS, T=T_in, P=P_react) for c in self.species]
                H_in_real = np.sum(F0 * (self.Hfm + np.array([c.Hm for c in chems_in])))
            except Exception:
                H_in_real = H_in_ideal
                
        def energy_balance_ideal(T):
            H_out = np.sum(F * (self.Hfgm + np.array([c.HeatCapacityGas.T_dependent_property_integral(298.15, T) for c in self.species])))
            return H_out - H_in_ideal
            
        def energy_balance_real(T):
            try:
                chems_T = [Chemical(c.CAS, T=T, P=P_react) for c in self.species]
                H_out = np.sum(F * (self.Hfm + np.array([c.Hm for c in chems_T])))
                return H_out - H_in_real
            except Exception:
                return energy_balance_ideal(T)
                
        try:
            T_out_ideal = brentq(energy_balance_ideal, T_in, 3000.0)
        except Exception:
            T_out_ideal = T_in
            
        try:
            T_out_real = brentq(energy_balance_real, T_in, 3000.0)
        except Exception:
            T_out_real = T_out_ideal
            
        return T_out_ideal, T_out_real
