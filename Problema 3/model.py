# -*- coding: utf-8 -*-
"""
Motor de Simulación Termodinámica y Cinética para la Hidrodesalquilación de Tolueno (PFR)
Autor: Antigravity AI
"""

import numpy as np
import pandas as pd
from thermo import Chemical

# Constante de los gases ideales (J / (mol*K))
R = 8.3144

class HydrodealkylationSimulator:
    def __init__(self):
        """
        Inicializa las especies químicas de la reacción:
        C6H5CH3 (Toluene) + H2 <=> C6H6 (Benzene) + CH4 (Methane)
        """
        # Cargar especies con sus respectivos CAS
        self.tol = Chemical('108-88-3')   # Tolueno
        self.h2 = Chemical('1333-74-0')   # Hidrógeno
        self.ben = Chemical('71-43-2')    # Benceno
        self.ch4 = Chemical('74-82-8')    # Metano
        
        self.species = [self.tol, self.h2, self.ben, self.ch4]
        self.names = ['Tolueno', 'Hidrógeno', 'Benceno', 'Metano']
        self.formulas = ['C6H5CH3', 'H2', 'C6H6', 'CH4']
        self.nu = np.array([-1, -1, 1, 1])  # Coeficientes estequiométricos
        
        # Entalpinas estándar de formación en fase gas a 298.15 K (J/mol)
        self.Hfm = np.array([c.Hfm for c in self.species])
        
    def get_k(self, T_K):
        """
        Calcula la constante de velocidad de reacción k (m^1.5 / (mol^0.5 * s)) en función de T (K).
        Fórmula: k = 3e10 * exp(-209213 / (R * T))
        """
        k = 3.0e10 * np.exp(-209213.0 / (R * T_K))
        return k
        
    def solve_pfr(self, T_reactor_C, P_bar, F_feed_kmol_h, tube_length_m, num_tubes, internal_diam_m, steps=100):
        """
        Resuelve la ecuación de diseño del PFR en fase gas mediante el método RK4.
        
        Parámetros:
        - T_reactor_C: Temperatura del reactor (ºC)
        - P_bar: Presión del reactor (bar)
        - F_feed_kmol_h: Lista de flujos de alimentación [F_Tol0, F_H20, F_CH40, F_B0] en kmol/h
        - tube_length_m: Longitud de cada tubo (m)
        - num_tubes: Número de tubos paralelos
        - internal_diam_m: Diámetro interno de cada tubo (m)
        - steps: Número de pasos de integración a lo largo del reactor
        
        Retorna:
        - df_profile: DataFrame con el perfil de flujos y conversión a lo largo del reactor
        - tau: Tiempo de residencia (s)
        - v0: Caudal volumétrico de entrada (m^3/s)
        """
        T_K = T_reactor_C + 273.15
        P_Pa = P_bar * 100000.0
        
        # Caudal molar alimentado en mol/s
        F_feed_mol_s = (np.array(F_feed_kmol_h) * 1000.0) / 3600.0
        F_Tol0_s, F_H20_s, F_CH40_s, F_B0_s = F_feed_mol_s
        F_total0_s = np.sum(F_feed_mol_s)
        
        # Geometría del reactor
        A_flow_per_tube = (np.pi / 4.0) * (internal_diam_m**2)  # m^2
        A_flow_total = A_flow_per_tube * num_tubes               # m^2
        V_total = A_flow_total * tube_length_m                   # m^3
        
        # Constante cinética y concentración total
        k = self.get_k(T_K)
        C_total = P_Pa / (R * T_K)  # mol/m^3
        
        # Integración RK4 a lo largo del volumen del reactor
        V_arr = np.linspace(0, V_total, steps)
        dV = V_total / (steps - 1)
        
        # Perfiles a rellenar
        V_profile = []
        X_profile = []
        F_Tol_profile = []
        F_H2_profile = []
        F_Ben_profile = []
        F_CH4_profile = []
        r_profile = []
        
        # Valores iniciales (V = 0)
        X = 0.0
        
        # Función para evaluar dX/dV
        def dX_dV_func(x):
            # Acotar conversión para evitar errores físicos o raíces cuadradas negativas
            x_bounded = min(max(x, 0.0), 1.0)
            
            F_Tol = F_Tol0_s * (1.0 - x_bounded)
            F_H2 = F_H20_s - F_Tol0_s * x_bounded
            
            # Concentraciones molares (mol/m^3)
            # Reacción en fase gas a T y P constantes, el número total de moles se conserva
            C_Tol = (F_Tol / F_total0_s) * C_total
            C_H2 = (F_H2 / F_total0_s) * C_total
            
            C_H2 = max(C_H2, 0.0)
            C_Tol = max(C_Tol, 0.0)
            
            r = k * C_Tol * (C_H2**0.5)  # mol/(m^3 * s)
            
            # dX/dV = r / F_Tol0
            return r / F_Tol0_s, r

        for i in range(steps):
            v_curr = V_arr[i]
            
            # Registrar estado actual
            dX_dV, r_curr = dX_dV_func(X)
            V_profile.append(v_curr)
            X_profile.append(X)
            
            # Flujos instantáneos (kmol/h)
            F_Tol_profile.append(F_Tol0_s * (1.0 - X) * 3600.0 / 1000.0)
            F_H2_profile.append((F_H20_s - F_Tol0_s * X) * 3600.0 / 1000.0)
            F_Ben_profile.append((F_B0_s + F_Tol0_s * X) * 3600.0 / 1000.0)
            F_CH4_profile.append((F_CH40_s + F_Tol0_s * X) * 3600.0 / 1000.0)
            r_profile.append(r_curr)
            
            if i < steps - 1:
                # Paso RK4 para calcular el siguiente X
                k1, _ = dX_dV_func(X)
                k2, _ = dX_dV_func(X + dV * k1 / 2.0)
                k3, _ = dX_dV_func(X + dV * k2 / 2.0)
                k4, _ = dX_dV_func(X + dV * k3)
                
                X = X + (dV / 6.0) * (k1 + 2.0*k2 + 2.0*k3 + k4)
                X = min(max(X, 0.0), 1.0)
                
        # Crear DataFrame del Perfil
        df_profile = pd.DataFrame({
            'Volume_m3': V_profile,
            'Length_m': (np.array(V_profile) / A_flow_total),
            'Conversion': X_profile,
            'Conversion_pct': np.array(X_profile) * 100.0,
            'F_Toluene': F_Tol_profile,
            'F_Hydrogen': F_H2_profile,
            'F_Benzene': F_Ben_profile,
            'F_Methane': F_CH4_profile,
            'Reaction_Rate': r_profile
        })
        
        # Tiempo de residencia (s)
        # v0 = F_total_s / C_total
        v0 = F_total0_s / C_total  # m^3/s
        tau = V_total / v0          # s
        
        return df_profile, tau, v0

    def calculate_heat_duties(self, T_reactor_C, T_feed_C, P_bar, F_feed_kmol_h, X):
        """
        Calcula las cargas térmicas del reactor (isotérmico a T_reactor, pero alimentado a T_feed).
        
        Retorna:
        - dH_rxn: Entalpía de reacción a T_reactor (kJ/mol)
        - Q_rxn: Potencia térmica generada/absorbida por la reacción (kW)
        - Q_sensible: Potencia térmica para calentar el gas de T_feed a T_reactor (kW)
        - Q_total: Potencia térmica total (kW)
        """
        T_rxn_K = T_reactor_C + 273.15
        T_feed_K = T_feed_C + 273.15
        P_Pa = P_bar * 100000.0
        
        # Cargar especies en condiciones de reacción y alimentación
        chems_rxn = [Chemical(c.CAS, T=T_rxn_K, P=P_Pa) for c in self.species]
        chems_feed = [Chemical(c.CAS, T=T_feed_K, P=P_Pa) for c in self.species]
        
        # Hm sensible respecto a 298.15 K
        Hm_rxn = np.array([c.Hm for c in chems_rxn])
        Hm_feed = np.array([c.Hm for c in chems_feed])
        
        # Entalpía total de reacción a T_reactor (kJ/mol)
        dH_rxn = np.sum(self.nu * (self.Hfm + Hm_rxn)) / 1000.0
        
        # Grado de avance (mol/s)
        F_Tol0_s = (F_feed_kmol_h[0] * 1000.0) / 3600.0
        xi_mol_s = F_Tol0_s * X
        
        # 1. Calor debido a la reacción (kW)
        Q_rxn = xi_mol_s * dH_rxn  # kW
        
        # 2. Calor sensible para llevar la alimentación de T_feed a T_reactor (kW)
        F_in_mol_s = (np.array(F_feed_kmol_h) * 1000.0) / 3600.0
        Q_sensible = np.sum(F_in_mol_s * (Hm_rxn - Hm_feed)) / 1000.0  # kW
        
        # 3. Calor total neta
        Q_total = Q_rxn + Q_sensible
        
        return dH_rxn, Q_rxn, Q_sensible, Q_total
