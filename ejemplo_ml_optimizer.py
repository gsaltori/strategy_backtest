"""
Ejemplo: Optimización de Estrategia con Machine Learning

Este script demuestra cómo usar el optimizador ML para:
1. Encontrar parámetros óptimos automáticamente
2. Validar resultados con walk-forward analysis
3. Detectar overfitting
4. Comparar diferentes métodos de optimización
"""

from datetime import datetime, timedelta
from data_manager import MT5DataManager
from backtest_engine import BacktestEngine
from strategies.moving_average_crossover import MovingAverageCrossover
from ml_optimizer import MLStrategyOptimizer, optimize_strategy_ml
from analysis.reporting import ReportGenerator
from config.settings import BacktestConfig
import pandas as pd
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def ejemplo_1_optimizacion_bayesiana():
    """
    Ejemplo 1: Optimización Bayesiana (Recomendado)
    
    Usa algoritmos evolutivos para encontrar parámetros óptimos
    de manera eficiente.
    """
    print("\n" + "="*80)
    print("EJEMPLO 1: OPTIMIZACIÓN BAYESIANA")
    print("="*80)
    
    # Conectar y descargar datos
    data_manager = MT5DataManager()
    data_manager.connect()
    
    data = data_manager.get_historical_data(
        symbol="EURUSD",
        timeframe="H1",
        start_date=datetime.now() - timedelta(days=365),
        count=5000
    )
    
    symbol_info = data_manager.get_symbol_info("EURUSD")
    
    # Crear optimizador
    optimizer = MLStrategyOptimizer(
        strategy_class=MovingAverageCrossover,
        data=data,
        symbol_info=symbol_info,
        target_metric='sharpe_ratio',  # Métrica a optimizar
        n_iterations=50,                # Número de iteraciones
        validation_pct=0.3              # 30% para validación
    )
    
    # Ejecutar optimización
    result = optimizer.bayesian_optimization()
    
    # Mostrar resultados
    print("\n" + "="*80)
    print("RESULTADOS DE LA OPTIMIZACIÓN")
    print("="*80)
    print(f"\n📊 Mejores Parámetros Encontrados:")
    for param, value in result.best_params.items():
        print(f"   {param}: {value}")
    
    print(f"\n📈 Scores:")
    print(f"   Train Score:      {result.validation_metrics['train_score']:.4f}")
    print(f"   Validation Score: {result.best_score:.4f}")
    print(f"   Overfit Ratio:    {result.validation_metrics['overfit_ratio']:.2f}")
    
    print(f"\n🔍 Feature Importance:")
    for param, importance in sorted(result.feature_importance.items(), 
                                   key=lambda x: x[1], reverse=True):
        print(f"   {param}: {importance:.4f}")
    
    # Detectar overfitting
    is_overfit = optimizer.detect_overfitting(result)
    
    if not is_overfit:
        # Ejecutar backtest con mejores parámetros
        print(f"\n✅ Ejecutando backtest con parámetros optimizados...")
        
        strategy = MovingAverageCrossover(**result.best_params)
        config = BacktestConfig(initial_capital=10000.0)
        engine = BacktestEngine(config)
        
        backtest_result = engine.run(strategy, data, symbol_info)
        print(backtest_result.summary())
        
        # Generar reporte
        report = ReportGenerator(backtest_result)
        report.save_report_html('optimized_bayesian.html')
        print("\n📁 Reporte guardado: optimized_bayesian.html")
    else:
        print("\n⚠️  Overfitting detectado. Considera usar walk-forward analysis.")
    
    # Guardar resultados de optimización
    result.all_results.to_csv('optimization_bayesian_history.csv', 
                              index=False, encoding='utf-8')
    print("📁 Historial guardado: optimization_bayesian_history.csv")
    
    data_manager.disconnect()


def ejemplo_2_random_forest():
    """
    Ejemplo 2: Optimización con Random Forest
    
    Usa ML para predecir el rendimiento de parámetros
    y encontrar óptimos de manera inteligente.
    """
    print("\n" + "="*80)
    print("EJEMPLO 2: OPTIMIZACIÓN CON RANDOM FOREST")
    print("="*80)
    
    # Conectar y descargar datos
    data_manager = MT5DataManager()
    data_manager.connect()
    
    data = data_manager.get_historical_data(
        symbol="EURUSD",
        timeframe="H1",
        start_date=datetime.now() - timedelta(days=365),
        count=5000
    )
    
    symbol_info = data_manager.get_symbol_info("EURUSD")
    
    # Crear optimizador
    optimizer = MLStrategyOptimizer(
        strategy_class=MovingAverageCrossover,
        data=data,
        symbol_info=symbol_info,
        target_metric='sharpe_ratio',
        n_iterations=60,  # Más iteraciones para RF
        validation_pct=0.3
    )
    
    # Ejecutar optimización RF
    result = optimizer.random_forest_optimization()
    
    # Mostrar resultados
    print("\n" + "="*80)
    print("RESULTADOS RANDOM FOREST")
    print("="*80)
    print(f"\n📊 Mejores Parámetros:")
    for param, value in result.best_params.items():
        print(f"   {param}: {value}")
    
    print(f"\n📈 Scores:")
    print(f"   Train Score:      {result.validation_metrics['train_score']:.4f}")
    print(f"   Validation Score: {result.best_score:.4f}")
    print(f"   Model R²:         {result.validation_metrics['model_r2']:.4f}")
    
    print(f"\n🌲 Feature Importance (Random Forest):")
    for param, importance in sorted(result.feature_importance.items(), 
                                   key=lambda x: x[1], reverse=True):
        print(f"   {param}: {importance:.4f}")
    
    # Ejecutar backtest
    strategy = MovingAverageCrossover(**result.best_params)
    config = BacktestConfig(initial_capital=10000.0)
    engine = BacktestEngine(config)
    
    backtest_result = engine.run(strategy, data, symbol_info)
    print(backtest_result.summary())
    
    # Generar reporte
    report = ReportGenerator(backtest_result)
    report.save_report_html('optimized_random_forest.html')
    print("\n📁 Reporte guardado: optimized_random_forest.html")
    
    data_manager.disconnect()


def ejemplo_3_walk_forward():
    """
    Ejemplo 3: Walk-Forward Analysis
    
    Simula trading en tiempo real optimizando en ventanas
    temporales y validando en la siguiente.
    """
    print("\n" + "="*80)
    print("EJEMPLO 3: WALK-FORWARD ANALYSIS")
    print("="*80)
    
    # Conectar y descargar datos
    data_manager = MT5DataManager()
    data_manager.connect()
    
    data = data_manager.get_historical_data(
        symbol="EURUSD",
        timeframe="H1",
        start_date=datetime.now() - timedelta(days=365),
        count=5000
    )
    
    symbol_info = data_manager.get_symbol_info("EURUSD")
    
    # Crear optimizador
    optimizer = MLStrategyOptimizer(
        strategy_class=MovingAverageCrossover,
        data=data,
        symbol_info=symbol_info,
        target_metric='sharpe_ratio',
        n_iterations=30
    )
    
    # Ejecutar walk-forward
    wf_results = optimizer.walk_forward_optimization(
        n_windows=5,      # 5 ventanas temporales
        train_pct=0.7     # 70% train, 30% test por ventana
    )
    
    # Mostrar resultados
    print("\n" + "="*80)
    print("RESULTADOS WALK-FORWARD")
    print("="*80)
    
    df_results = wf_results['results_by_window']
    
    print("\n📊 Resultados por Ventana:")
    print(df_results[['window', 'train_score', 'test_score', 'overfit_ratio']].to_string(index=False))
    
    print(f"\n📈 Resumen Agregado:")
    print(f"   Avg Train Score:  {wf_results['avg_train_score']:.4f}")
    print(f"   Avg Test Score:   {wf_results['avg_test_score']:.4f}")
    print(f"   Avg Overfit:      {wf_results['avg_overfit_ratio']:.2f}")
    print(f"   Stability Score:  {wf_results['stability_score']:.4f}")
    
    print(f"\n🏆 Mejor Ventana:")
    best_window = wf_results['best_window']
    print(f"   Window:      {best_window['window']}")
    print(f"   Test Score:  {best_window['test_score']:.4f}")
    print(f"   Parámetros:  {best_window['best_params']}")
    
    # Guardar resultados
    df_results.to_csv('walk_forward_results.csv', index=False, encoding='utf-8')
    print("\n📁 Resultados guardados: walk_forward_results.csv")
    
    data_manager.disconnect()


def ejemplo_4_comparacion_metodos():
    """
    Ejemplo 4: Comparar Diferentes Métodos
    
    Compara Bayesian vs Random Forest para ver cuál funciona mejor.
    """
    print("\n" + "="*80)
    print("EJEMPLO 4: COMPARACIÓN DE MÉTODOS")
    print("="*80)
    
    # Conectar y descargar datos
    data_manager = MT5DataManager()
    data_manager.connect()
    
    data = data_manager.get_historical_data(
        symbol="EURUSD",
        timeframe="H1",
        start_date=datetime.now() - timedelta(days=365),
        count=5000
    )
    
    symbol_info = data_manager.get_symbol_info("EURUSD")
    
    resultados = []
    
    # Método 1: Bayesian
    print("\n🔍 Ejecutando Bayesian Optimization...")
    result_bayesian = optimize_strategy_ml(
        data=data,
        symbol_info=symbol_info,
        method='bayesian',
        target_metric='sharpe_ratio',
        n_iterations=40
    )
    
    resultados.append({
        'Método': 'Bayesian',
        'Validation Score': result_bayesian.best_score,
        'Overfit Ratio': result_bayesian.validation_metrics['overfit_ratio'],
        'Parámetros': result_bayesian.best_params
    })
    
    # Método 2: Random Forest
    print("\n🌲 Ejecutando Random Forest Optimization...")
    result_rf = optimize_strategy_ml(
        data=data,
        symbol_info=symbol_info,
        method='random_forest',
        target_metric='sharpe_ratio',
        n_iterations=50
    )
    
    resultados.append({
        'Método': 'Random Forest',
        'Validation Score': result_rf.best_score,
        'Overfit Ratio': result_rf.validation_metrics['overfit_ratio'],
        'Parámetros': result_rf.best_params
    })
    
    # Comparar
    print("\n" + "="*80)
    print("COMPARACIÓN DE RESULTADOS")
    print("="*80)
    
    df_comp = pd.DataFrame(resultados)
    print("\n", df_comp[['Método', 'Validation Score', 'Overfit Ratio']].to_string(index=False))
    
    # Mejor método
    mejor_idx = df_comp['Validation Score'].idxmax()
    mejor_metodo = df_comp.iloc[mejor_idx]
    
    print(f"\n🏆 Mejor Método: {mejor_metodo['Método']}")
    print(f"   Score: {mejor_metodo['Validation Score']:.4f}")
    print(f"   Parámetros: {mejor_metodo['Parámetros']}")
    
    # Ejecutar backtest con el mejor
    print(f"\n✅ Ejecutando backtest con mejor método ({mejor_metodo['Método']})...")
    
    strategy = MovingAverageCrossover(**mejor_metodo['Parámetros'])
    config = BacktestConfig(initial_capital=10000.0)
    engine = BacktestEngine(config)
    
    backtest_result = engine.run(strategy, data, symbol_info)
    print(backtest_result.summary())
    
    # Generar reporte
    report = ReportGenerator(backtest_result)
    report.save_report_html('optimized_best_method.html')
    print("\n📁 Reporte guardado: optimized_best_method.html")
    
    data_manager.disconnect()


def ejemplo_5_cross_validation():
    """
    Ejemplo 5: Validación Cruzada
    
    Valida parámetros usando validación cruzada temporal.
    """
    print("\n" + "="*80)
    print("EJEMPLO 5: VALIDACIÓN CRUZADA")
    print("="*80)
    
    # Conectar y descargar datos
    data_manager = MT5DataManager()
    data_manager.connect()
    
    data = data_manager.get_historical_data(
        symbol="EURUSD",
        timeframe="H1",
        start_date=datetime.now() - timedelta(days=365),
        count=5000
    )
    
    symbol_info = data_manager.get_symbol_info("EURUSD")
    
    # Primero optimizar
    print("\n🔍 Optimizando parámetros...")
    optimizer = MLStrategyOptimizer(
        strategy_class=MovingAverageCrossover,
        data=data,
        symbol_info=symbol_info,
        target_metric='sharpe_ratio',
        n_iterations=30,
        cv_splits=5
    )
    
    result = optimizer.bayesian_optimization()
    
    # Validación cruzada
    print("\n🔄 Ejecutando validación cruzada...")
    cv_results = optimizer.cross_validation(result.best_params)
    
    print("\n" + "="*80)
    print("RESULTADOS VALIDACIÓN CRUZADA")
    print("="*80)
    print(f"\n📊 Parámetros Validados:")
    for param, value in result.best_params.items():
        print(f"   {param}: {value}")
    
    print(f"\n📈 Cross-Validation Scores:")
    print(f"   Train Mean: {cv_results['train_mean']:.4f} ± {cv_results['train_std']:.4f}")
    print(f"   Test Mean:  {cv_results['test_mean']:.4f} ± {cv_results['test_std']:.4f}")
    print(f"   Overfit:    {cv_results['overfit_ratio']:.2f}")
    
    print(f"\n📊 Scores por Fold:")
    for i, (train, test) in enumerate(zip(cv_results['train_scores'], 
                                          cv_results['test_scores'])):
        print(f"   Fold {i+1}: Train={train:.4f}, Test={test:.4f}")
    
    # Si pasa validación, ejecutar backtest completo
    if cv_results['overfit_ratio'] < 1.3:
        print(f"\n✅ Validación exitosa. Ejecutando backtest completo...")
        
        strategy = MovingAverageCrossover(**result.best_params)
        config = BacktestConfig(initial_capital=10000.0)
        engine = BacktestEngine(config)
        
        backtest_result = engine.run(strategy, data, symbol_info)
        print(backtest_result.summary())
        
        report = ReportGenerator(backtest_result)
        report.save_report_html('optimized_cv_validated.html')
        print("\n📁 Reporte guardado: optimized_cv_validated.html")
    else:
        print(f"\n⚠️  Alto overfit ratio ({cv_results['overfit_ratio']:.2f}). "
              "Considera más datos o menos parámetros.")
    
    data_manager.disconnect()


def menu_principal():
    """Menú interactivo"""
    print("\n" + "="*80)
    print(" "*20 + "OPTIMIZADOR ML DE ESTRATEGIAS")
    print("="*80)
    print("\nSelecciona un ejemplo:")
    print("1. Optimización Bayesiana (Recomendado)")
    print("2. Optimización Random Forest")
    print("3. Walk-Forward Analysis")
    print("4. Comparación de Métodos")
    print("5. Validación Cruzada")
    print("6. Ejecutar todos los ejemplos")
    print("0. Salir")
    
    return input("\nElige una opción (0-6): ").strip()


if __name__ == "__main__":
    while True:
        opcion = menu_principal()
        
        try:
            if opcion == '1':
                ejemplo_1_optimizacion_bayesiana()
            elif opcion == '2':
                ejemplo_2_random_forest()
            elif opcion == '3':
                ejemplo_3_walk_forward()
            elif opcion == '4':
                ejemplo_4_comparacion_metodos()
            elif opcion == '5':
                ejemplo_5_cross_validation()
            elif opcion == '6':
                ejemplo_1_optimizacion_bayesiana()
                ejemplo_2_random_forest()
                ejemplo_3_walk_forward()
                ejemplo_4_comparacion_metodos()
                ejemplo_5_cross_validation()
            elif opcion == '0':
                print("\n👋 ¡Hasta luego!")
                break
            else:
                print("\n❌ Opción no válida")
                continue
            
            input("\n\nPresiona Enter para continuar...")
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrumpido por el usuario")
            break
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            print(f"\n❌ Error: {e}")
            input("\nPresiona Enter para continuar...")