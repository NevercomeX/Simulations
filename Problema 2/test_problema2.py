# -*- coding: utf-8 -*-
"""
Script de Pruebas de Verificación para el Problema 2
Autor: Antigravity AI
"""

from model import NitrobenzeneSimulator

def test_simulator():
    print("Inicializando simulador de Hidrogenación...")
    sim = NitrobenzeneSimulator()
    
    # Parámetros estándar de prueba
    T_in_C = 300.0
    P_react_kPa = 500.0
    F_NB0 = 100.0
    H2_ratio = 10.0
    X = 0.99
    
    print(f"Calculando balance para F_NB0 = {F_NB0} kmol/h, H2_ratio = {H2_ratio}, X = {X}...")
    F0, F, y = sim.calculate_balance(F_NB0, H2_ratio, X)
    print("Balance de Materia:")
    print(f"  Flujo Entrada: {F0}")
    print(f"  Flujo Salida: {F}")
    print(f"  Fracciones Molares: {y}")
    
    assert F[0] == 1.0, "El nitrobenceno remanente debería ser 1.0 kmol/h (99% conversión de 100)"
    
    print("\nCalculando termodinámica a T_in = 300 ºC y P = 500 kPa...")
    dH_ideal, dH_real, Q_ideal, Q_real, chems_in = sim.calculate_thermodynamics(
        T_in_C, P_react_kPa, F_NB0, H2_ratio, X
    )
    print(f"  dH_rxn (Ideal): {dH_ideal/1e3:.4f} kJ/mol")
    print(f"  dH_rxn (Real): {dH_real/1e3:.4f} kJ/mol")
    print(f"  Heat Duty (Ideal): {Q_ideal:.4f} kW")
    print(f"  Heat Duty (Real): {Q_real:.4f} kW")
    
    print("\nResolviendo temperatura de reactor adiabático...")
    T_out_ideal, T_out_real = sim.solve_adiabatic(
        T_in_C, P_react_kPa, F_NB0, H2_ratio, X, chems_in
    )
    print(f"  T_out_adiabatic (Ideal): {T_out_ideal - 273.15:.2f} ºC")
    print(f"  T_out_adiabatic (Real): {T_out_real - 273.15:.2f} ºC")
    
    assert T_out_ideal > T_in_C + 273.15, "La reacción es altamente exotérmica, la temperatura debería elevarse"
    
    print("\n¡Pruebas de verificación para el Problema 2 completadas con éxito!")

if __name__ == '__main__':
    test_simulator()
