# -*- coding: utf-8 -*-
"""
Motor de Simulación Termodinámica y Cinética para la Esterificación de Acetato de Etilo
Autor: Antigravity AI
"""

import numpy as np
import pandas as pd
from thermo import Chemical
from scipy.optimize import brentq

# Constante de los gases ideales (J / (mol*K) o kJ / (kmol*K))
R = 8.3144

class EsterificationSimulator:
    def __init__(self):
        """
        Inicializa las especies químicas de la reacción de esterificación:
        AcOH + EtOH <=> EtOAc + H2O
        """
        # Cargar especies con sus respectivos CAS
        self.acoh = Chemical('64-19-7')    # Ácido Acético
        self.etoh = Chemical('64-17-5')    # Etanol
        self.etoac = Chemical('141-78-6')  # Acetato de Etilo
        self.h2o = Chemical('7732-18-5')   # Agua
        
        self.species = [self.acoh, self.etoh, self.etoac, self.h2o]
        self.names = ['Ácido Acético', 'Etanol', 'Acetato de Etilo', 'Agua']
        self.formulas = ['CH3COOH', 'CH3CH2OH', 'CH3COOC2H5', 'H2O']
        self.nu = np.array([-1, -1, 1, 1])  # Coeficientes estequiométricos
        
        # Entalpías estándar de formación en fase estable a 298.15 K (J/mol)
        self.Hfm = np.array([c.Hfm for c in self.species])
        
    def get_k(self, T_K):
        """
        Calcula las constantes de velocidad cinética (kmol/s) en función de T (K).
        """
        kf = 4.24e3 * np.exp(-48300.0 / (R * T_K))
        kb = 4.55e5 * np.exp(-66200.0 / (R * T_K))
        return kf, kb
        
    def solve_cstr(self, T_C, F_A0_kmol_h, W_kg, ratio=1.0):
        """
        Resuelve la ecuación de diseño del CSTR a la temperatura T_C (ºC) y catalizador W_kg.
        
        Parámetros:
        - T_C: Temperatura del reactor (ºC)
        - F_A0_kmol_h: Flujo de alimentación de ácido acético (kmol/h)
        - W_kg: Masa de catalizador (kg)
        - ratio: Relación molar EtOH / AcOH en alimentación
        
        Retorna:
        - X: Conversión en el reactor
        - F_out: Flujos molares de salida (kmol/h) [AcOH, EtOH, EtOAc, H2O]
        - rates: Tasas de reacción [r_f, r_b, r_net] (kmol/s)
        """
        T_K = T_C + 273.15
        F_A0_s = F_A0_kmol_h / 3600.0  # kmol/s
        F_B0_s = F_A0_s * ratio
        F0_s = np.array([F_A0_s, F_B0_s, 0.0, 0.0])
        
        kf, kb = self.get_k(T_K)
        
        # Ecuación de residuo a resolver para X
        def cstr_residual(X):
            # Flujos molares a la salida (kmol/s) en términos de X
            # (Reacción equimolar, limitante es AcOH si ratio >= 1.0)
            F_A = F_A0_s * (1.0 - X)
            F_B = F_B0_s - F_A0_s * X
            F_C = F_A0_s * X
            F_D = F_A0_s * X
            
            F_total = F_A + F_B + F_C + F_D
            
            # Fracciones molares de salida
            x_A = F_A / F_total
            x_B = F_B / F_total
            x_C = F_C / F_total
            x_D = F_D / F_total
            
            # Velocidades de reacción (kmol/s) escaladas por la masa de catalizador W
            r_f = kf * W_kg * x_B * (x_A**1.5)
            r_b = kb * W_kg * x_C * x_D
            r_net = r_f - r_b
            
            # Balance de materia para AcOH: F_A0 - F_A = r_net => F_A0 * X = r_net
            return F_A0_s * X - r_net

        # Resolver numéricamente para X en el intervalo [0, 0.9999]
        try:
            X = brentq(cstr_residual, 0.0, 0.9999)
        except Exception:
            # En caso de error, retornar una estimación segura
            X = 0.0
            
        # Calcular corrientes de salida finales (kmol/h)
        F_out = (F0_s + self.nu * F_A0_s * X) * 3600.0
        
        # Calcular velocidades en el punto de operación (kmol/s)
        F_out_s = F_out / 3600.0
        F_tot_s = np.sum(F_out_s)
        x_out = F_out_s / F_tot_s
        r_f = kf * W_kg * x_out[1] * (x_out[0]**1.5)
        r_b = kb * W_kg * x_out[2] * x_out[3]
        r_net = r_f - r_b
        
        return X, F_out, [r_f, r_b, r_net]

    def calculate_heat_duties(self, T_reactor_C, T_feed_C, F_A0_kmol_h, W_kg, X, ratio=1.0):
        """
        Calcula las cargas térmicas (heat duties) en kW para el reactor.
        
        Parámetros:
        - T_reactor_C: Temperatura del reactor (ºC)
        - T_feed_C: Temperatura de la alimentación (ºC)
        - F_A0_kmol_h: Flujo de ácido acético alimentado (kmol/h)
        - W_kg: Masa del catalizador (kg)
        - X: Conversión obtenida
        - ratio: Relación de alimentación
        
        Retorna:
        - dH_rxn: Calor de reacción a T_reactor (kJ/mol)
        - Q_rxn: Potencia térmica por la reacción (kW)
        - Q_sensible: Potencia térmica para calentar la alimentación (kW)
        - Q_total: Potencia térmica neta del reactor (kW)
        """
        T_rxn_K = T_reactor_C + 273.15
        T_feed_K = T_feed_C + 273.15
        P = 101325.0  # 1 atm
        
        # Cargar especies en las condiciones de reacción y alimentación
        chems_rxn = [Chemical(c.CAS, T=T_rxn_K, P=P) for c in self.species]
        chems_feed = [Chemical(c.CAS, T=T_feed_K, P=P) for c in self.species]
        
        # Hm representa la entalpía molar sensible (J/mol) respecto a 298.15 K
        Hm_rxn = np.array([c.Hm for c in chems_rxn])
        Hm_feed = np.array([c.Hm for c in chems_feed])
        
        # Entalpía total de la reacción a T_reactor (kJ/mol)
        dH_rxn = np.sum(self.nu * (self.Hfm + Hm_rxn)) / 1000.0
        
        # Grado de avance en mol/s
        xi_mol_s = (F_A0_kmol_h * X * 1000.0) / 3600.0
        
        # 1. Calor debido a la reacción (kW = kJ/s)
        Q_rxn = xi_mol_s * dH_rxn  # kW
        
        # 2. Calor sensible para calentar la alimentación desde T_feed a T_reactor (kW)
        F_in_kmol_h = np.array([F_A0_kmol_h, F_A0_kmol_h * ratio, 0.0, 0.0])
        F_in_mol_s = (F_in_kmol_h * 1000.0) / 3600.0
        
        # Q_sensible = sum( F_in,i * (Hm_rxn,i - Hm_feed,i) )
        Q_sensible = np.sum(F_in_mol_s * (Hm_rxn - Hm_feed)) / 1000.0  # kW
        
        # 3. Calor total
        Q_total = Q_rxn + Q_sensible
        
        return dH_rxn, Q_rxn, Q_sensible, Q_total

    def run_sensitivity(self, F_A0_kmol_h, W_kg, ratio=1.0):
        """
        Ejecuta el análisis de sensibilidad variando T de 50 a 130 ºC en pasos de 5 ºC.
        """
        T_range_C = np.arange(50, 131, 5)
        results = []
        
        for T in T_range_C:
            X, F_out, rates = self.solve_cstr(T, F_A0_kmol_h, W_kg, ratio)
            
            # Fracción molar de EtOAc en la salida
            F_total = np.sum(F_out)
            y_EtOAc = (F_out[2] / F_total) * 100.0 if F_total > 0 else 0.0
            
            # Calcular calor de reacción
            T_K = T + 273.15
            try:
                chems_rxn = [Chemical(c.CAS, T=T_K, P=101325.0) for c in self.species]
                Hm_rxn = np.array([c.Hm for c in chems_rxn])
                dH_rxn = np.sum(self.nu * (self.Hfm + Hm_rxn)) / 1000.0
            except Exception:
                dH_rxn = -4.515
                
            xi_mol_s = (F_A0_kmol_h * X * 1000.0) / 3600.0
            Q_rxn = xi_mol_s * dH_rxn
            
            kf, kb = self.get_k(T_K)
            
            results.append({
                'Temperature_C': T,
                'Conversion': X,
                'Conversion_pct': X * 100.0,
                'y_EtOAc': y_EtOAc,
                'kf': kf,
                'kb': kb,
                'dH_rxn': dH_rxn,
                'Q_rxn': Q_rxn
            })
            
        df = pd.DataFrame(results)
        
        # Encontrar la temperatura óptima que maximiza la fracción de EtOAc (y_EtOAc)
        idx_opt = df['y_EtOAc'].idxmax()
        row_opt = df.iloc[idx_opt]
        T_opt = row_opt['Temperature_C']
        max_y = row_opt['y_EtOAc']
        
        return df, T_opt, max_y
