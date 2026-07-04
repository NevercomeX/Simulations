# -*- coding: utf-8 -*-
"""
Script de Pruebas de Verificación para el Problema 3
Autor: Antigravity AI
"""

from model import HydrodealkylationSimulator

def test_simulator():
    print("Inicializando simulador del PFR...")
    sim = HydrodealkylationSimulator()
    
    # Parámetros estándar del problema
    T_reactor_C = 815.0
    T_feed_C = 750.0
    P_bar = 26.0
    F_feed_kmol_h = [70.0, 370.0, 160.0, 4.0]
    
    tube_length_m = 10.0
    num_tubes = 500
    internal_diam_m = 0.02
    
    print("Ejecutando integración del PFR...")
    df_profile, tau, v0 = sim.solve_pfr(
        T_reactor_C, P_bar, F_feed_kmol_h, tube_length_m, num_tubes, internal_diam_m
    )
    
    # Comprobar resultados finales
    last_row = df_profile.iloc[-1]
    X_final = last_row['Conversion']
    
    print("\nResultados del PFR:")
    print(f"  Conversión de Tolueno (X): {X_final*100.0:.4f} %")
    print(f"  Tiempo de Residencia (tau): {tau:.4f} s")
    print(f"  Caudal Volumétrico (v0): {v0:.4f} m³/s")
    print(f"  Flujo Final de Tolueno: {last_row['F_Toluene']:.4f} kmol/h")
    print(f"  Flujo Final de Benceno: {last_row['F_Benzene']:.4f} kmol/h")
    
    assert X_final > 0.99, "La conversión a 815ºC debería ser cercana al 100%"
    assert abs(tau - 2.6905) < 0.05, "El tiempo de residencia debería ser de aprox. 2.69 s"
    
    print("\nCalculando cargas térmicas...")
    dH_rxn, Q_rxn, Q_sensible, Q_total = sim.calculate_heat_duties(
        T_reactor_C, T_feed_C, P_bar, F_feed_kmol_h, X_final
    )
    print(f"  dH_rxn: {dH_rxn:.4f} kJ/mol")
    print(f"  Q_rxn: {Q_rxn:.4f} kW")
    print(f"  Q_sensible: {Q_sensible:.4f} kW")
    print(f"  Q_total: {Q_total:.4f} kW")
    
    print("\n¡Pruebas de verificación para el Problema 3 completadas con éxito!")

if __name__ == '__main__':
    test_simulator()
