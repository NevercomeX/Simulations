# -*- coding: utf-8 -*-
"""
Script de Pruebas de Verificación para el Problema 1
Autor: Antigravity AI
"""

from model import EsterificationSimulator

def test_simulator():
    print("Inicializando simulador...")
    sim = EsterificationSimulator()
    
    # 1. Resolver CSTR a 70 ºC, con F_A0 = 50 kmol/h y W = 1.0 kg
    T_reactor_C = 70.0
    F_A0_kmol_h = 50.0
    W_kg = 1.0
    
    print(f"Resolviendo CSTR a T = {T_reactor_C} ºC, F_A0 = {F_A0_kmol_h} kmol/h, W = {W_kg} kg...")
    X, F_out, rates = sim.solve_cstr(T_reactor_C, F_A0_kmol_h, W_kg)
    
    print("Resultados del Reactor:")
    print(f"  Conversión X: {X:.6f} ({X*100:.4f} %)")
    print(f"  Flujos de Salida (kmol/h): {F_out}")
    print(f"  Velocidad Directa (rf): {rates[0]:.6e} kmol/s")
    print(f"  Velocidad Reversa (rb): {rates[1]:.6e} kmol/s")
    print(f"  Velocidad Neta (r_net): {rates[2]:.6e} kmol/s")
    
    assert X > 0, "La conversión debería ser mayor a 0"
    
    # 2. Calcular Cargas Térmicas (Heat Duties)
    T_feed_C = 70.0
    print(f"\nCalculando cargas térmicas con T_feed = {T_feed_C} ºC...")
    dH_rxn, Q_rxn, Q_sensible, Q_total = sim.calculate_heat_duties(
        T_reactor_C, T_feed_C, F_A0_kmol_h, W_kg, X
    )
    print(f"  dH_rxn: {dH_rxn:.4f} kJ/mol")
    print(f"  Q_rxn: {Q_rxn:.4e} kW")
    print(f"  Q_sensible: {Q_sensible:.4e} kW")
    print(f"  Q_total: {Q_total:.4e} kW")
    
    # 3. Análisis de Sensibilidad
    print("\nEjecutando análisis de sensibilidad...")
    df_sens, T_opt, max_y = sim.run_sensitivity(F_A0_kmol_h, W_kg)
    print(f"  Temperatura óptima: {T_opt} ºC")
    print(f"  Fracción molar máxima de EtOAc: {max_y:.4f} %")
    
    assert len(df_sens) == 17, "El rango de 50 a 130 ºC con paso de 5ºC debería contener 17 puntos"
    print("\n¡Pruebas de verificación completadas con éxito!")

if __name__ == '__main__':
    test_simulator()
