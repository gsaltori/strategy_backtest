"""
EJEMPLO DE INTEGRACIÓN CON GUI EXISTENTE

Este archivo muestra cómo integrar la estrategia ML con tu GUI de backtesting actual.
"""

import tkinter as tk
from tkinter import ttk

# ============================================================================
# OPCIÓN 1: Integración Simple - Agregar pestaña al Notebook
# ============================================================================

def ejemplo_integracion_simple():
    """
    Forma más simple: Agregar una nueva pestaña al notebook existente
    """
    
    from ml_strategy_gui_integration import integrate_ml_strategy_to_gui
    
    # En tu clase BacktestGUI existente:
    class BacktestGUI:
        def __init__(self, root):
            self.root = root
            self.root.title("Sistema de Backtesting")
            
            # Tu código existente...
            self.notebook = ttk.Notebook(root)
            self.notebook.pack(fill='both', expand=True)
            
            # Tus pestañas existentes
            self.create_config_tab()
            self.create_strategy_tab()
            self.create_data_tab()
            
            # ¡NUEVA! Pestaña de ML Strategy
            self.ml_integration = integrate_ml_strategy_to_gui(self.notebook)
            
            # Resto de tu código...
        
        def run_backtest(self):
            """Método existente modificado para soportar ML"""
            # Obtener estrategia seleccionada
            selected_strategy = self.strategy_var.get()
            
            if selected_strategy == "ML Advanced":
                # Obtener estrategia ML configurada desde la GUI
                strategy = self.ml_integration.get_strategy_instance()
            else:
                # Tu código existente para otras estrategias
                strategy = self.get_selected_strategy()
            
            # Tu código de backtest existente
            result = self.engine.run(strategy, self.data, self.symbol_info)
            
            # Actualizar estado del modelo ML si es estrategia ML
            if selected_strategy == "ML Advanced":
                self.ml_integration.update_status(strategy)


# ============================================================================
# OPCIÓN 2: Integración Manual - Agregar a lista de estrategias
# ============================================================================

def ejemplo_integracion_manual():
    """
    Agregar ML Strategy a tu selector de estrategias existente
    """
    
    from strategies.ml_advanced_strategy import MLAdvancedStrategy
    
    class BacktestGUI:
        def __init__(self, root):
            # ... tu código existente ...
            
            # Modificar tu diccionario de estrategias
            self.available_strategies = {
                'Moving Average Crossover': self.create_ma_crossover,
                'Two Bearish Pattern': self.create_two_bearish,
                'ML Advanced': self.create_ml_advanced,  # ← NUEVA
            }
        
        def create_ml_advanced(self):
            """Factory method para crear estrategia ML"""
            # Leer parámetros desde tu GUI
            params = {
                'prediction_threshold': self.ml_threshold_var.get(),
                'risk_per_trade': self.ml_risk_var.get(),
                'max_positions': self.ml_positions_var.get(),
                # ... más parámetros ...
            }
            return MLAdvancedStrategy(**params)
        
        def create_ml_params_ui(self, parent):
            """Crear UI para parámetros ML (alternativa a integración completa)"""
            frame = ttk.LabelFrame(parent, text="ML Parameters")
            frame.pack(fill='x', padx=5, pady=5)
            
            # Threshold
            ttk.Label(frame, text="Prediction Threshold:").grid(row=0, column=0)
            self.ml_threshold_var = tk.DoubleVar(value=0.55)
            ttk.Spinbox(frame, from_=0.5, to=0.95, increment=0.05,
                       textvariable=self.ml_threshold_var).grid(row=0, column=1)
            
            # Risk
            ttk.Label(frame, text="Risk per Trade:").grid(row=1, column=0)
            self.ml_risk_var = tk.DoubleVar(value=0.02)
            ttk.Spinbox(frame, from_=0.01, to=0.10, increment=0.01,
                       textvariable=self.ml_risk_var).grid(row=1, column=1)
            
            # Max Positions
            ttk.Label(frame, text="Max Positions:").grid(row=2, column=0)
            self.ml_positions_var = tk.IntVar(value=3)
            ttk.Spinbox(frame, from_=1, to=10,
                       textvariable=self.ml_positions_var).grid(row=2, column=1)


# ============================================================================
# OPCIÓN 3: Integración Completa - Reemplazar sección de estrategia
# ============================================================================

def ejemplo_integracion_completa():
    """
    Reemplazar completamente la sección de estrategia con soporte ML
    """
    
    from ml_strategy_gui_integration import MLStrategyGUIIntegration
    
    class BacktestGUI:
        def __init__(self, root):
            # ... tu código ...
            
            # Crear frames principales
            self.create_config_frame()
            self.create_strategy_frame()  # ← Modificado para ML
            self.create_data_frame()
            self.create_results_frame()
        
        def create_strategy_frame(self):
            """Frame de estrategia con soporte ML completo"""
            strategy_frame = ttk.LabelFrame(self.root, text="Estrategia")
            strategy_frame.pack(fill='both', expand=True, padx=5, pady=5)
            
            # Notebook para diferentes estrategias
            strategy_notebook = ttk.Notebook(strategy_frame)
            strategy_notebook.pack(fill='both', expand=True)
            
            # Pestaña 1: Estrategias tradicionales
            traditional_frame = ttk.Frame(strategy_notebook)
            strategy_notebook.add(traditional_frame, text="Tradicionales")
            self.create_traditional_strategies(traditional_frame)
            
            # Pestaña 2: ML Strategy con UI completa
            ml_frame = ttk.Frame(strategy_notebook)
            strategy_notebook.add(ml_frame, text="ML Advanced")
            self.ml_integration = MLStrategyGUIIntegration(ml_frame)


# ============================================================================
# EJEMPLO COMPLETO DE USO
# ============================================================================

def ejemplo_uso_completo():
    """
    Ejemplo completo de cómo usar la estrategia ML en tu GUI
    """
    
    import tkinter as tk
    from tkinter import ttk, messagebox
    from strategies.ml_advanced_strategy import MLAdvancedStrategy
    from ml_strategy_gui_integration import integrate_ml_strategy_to_gui
    from backtest_engine import BacktestEngine
    from config.settings import BacktestConfig
    
    class BacktestGUI:
        def __init__(self, root):
            self.root = root
            self.root.title("Trading Backtest System - Con ML")
            self.root.geometry("1200x800")
            
            # Variables
            self.data = None
            self.symbol_info = None
            
            # Crear UI
            self.create_ui()
        
        def create_ui(self):
            """Crea la interfaz de usuario"""
            # Notebook principal
            self.notebook = ttk.Notebook(self.root)
            self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
            
            # Pestaña 1: Configuración
            config_frame = ttk.Frame(self.notebook)
            self.notebook.add(config_frame, text="⚙️ Configuración")
            self.create_config_section(config_frame)
            
            # Pestaña 2: Estrategias Tradicionales
            traditional_frame = ttk.Frame(self.notebook)
            self.notebook.add(traditional_frame, text="📊 Estrategias")
            self.create_traditional_section(traditional_frame)
            
            # Pestaña 3: ML Strategy (¡NUEVA!)
            self.ml_integration = integrate_ml_strategy_to_gui(self.notebook)
            
            # Pestaña 4: Datos
            data_frame = ttk.Frame(self.notebook)
            self.notebook.add(data_frame, text="📁 Datos")
            self.create_data_section(data_frame)
            
            # Pestaña 5: Resultados
            results_frame = ttk.Frame(self.notebook)
            self.notebook.add(results_frame, text="📈 Resultados")
            self.create_results_section(results_frame)
            
            # Botón de ejecución (abajo)
            button_frame = ttk.Frame(self.root)
            button_frame.pack(fill='x', padx=5, pady=5)
            
            ttk.Button(
                button_frame,
                text="▶️ Ejecutar Backtest",
                command=self.run_backtest,
                style='Accent.TButton'
            ).pack(side='left', padx=5)
            
            ttk.Button(
                button_frame,
                text="📊 Ver Reportes",
                command=self.show_reports
            ).pack(side='left', padx=5)
        
        def create_config_section(self, parent):
            """Sección de configuración del backtest"""
            # Capital inicial
            ttk.Label(parent, text="Capital Inicial:").grid(row=0, column=0, sticky='w', pady=5)
            self.capital_var = tk.DoubleVar(value=10000.0)
            ttk.Entry(parent, textvariable=self.capital_var).grid(row=0, column=1, pady=5)
            
            # Comisión
            ttk.Label(parent, text="Comisión (%):").grid(row=1, column=0, sticky='w', pady=5)
            self.commission_var = tk.DoubleVar(value=0.01)
            ttk.Entry(parent, textvariable=self.commission_var).grid(row=1, column=1, pady=5)
            
            # Slippage
            ttk.Label(parent, text="Slippage (%):").grid(row=2, column=0, sticky='w', pady=5)
            self.slippage_var = tk.DoubleVar(value=0.05)
            ttk.Entry(parent, textvariable=self.slippage_var).grid(row=2, column=1, pady=5)
        
        def create_traditional_section(self, parent):
            """Sección de estrategias tradicionales"""
            ttk.Label(parent, text="Selecciona una estrategia:").pack(pady=10)
            
            self.traditional_strategy_var = tk.StringVar()
            strategies = ["MA Crossover", "RSI", "MACD", "Bollinger Bands"]
            
            for strategy in strategies:
                ttk.Radiobutton(
                    parent,
                    text=strategy,
                    variable=self.traditional_strategy_var,
                    value=strategy
                ).pack(anchor='w', padx=20)
        
        def create_data_section(self, parent):
            """Sección de carga de datos"""
            ttk.Label(parent, text="Fuente de datos:").pack(pady=10)
            
            self.data_source_var = tk.StringVar(value="MT5")
            ttk.Radiobutton(parent, text="MetaTrader 5", variable=self.data_source_var, 
                          value="MT5").pack(anchor='w', padx=20)
            ttk.Radiobutton(parent, text="Archivo CSV", variable=self.data_source_var,
                          value="CSV").pack(anchor='w', padx=20)
            ttk.Radiobutton(parent, text="Datos de Muestra", variable=self.data_source_var,
                          value="Sample").pack(anchor='w', padx=20)
            
            ttk.Button(parent, text="📂 Cargar Datos", 
                      command=self.load_data).pack(pady=20)
        
        def create_results_section(self, parent):
            """Sección de resultados"""
            # Text widget para mostrar resultados
            self.results_text = tk.Text(parent, wrap='word', height=30)
            self.results_text.pack(fill='both', expand=True, padx=5, pady=5)
            
            # Scrollbar
            scrollbar = ttk.Scrollbar(parent, command=self.results_text.yview)
            scrollbar.pack(side='right', fill='y')
            self.results_text.config(yscrollcommand=scrollbar.set)
        
        def load_data(self):
            """Carga datos según la fuente seleccionada"""
            source = self.data_source_var.get()
            
            if source == "Sample":
                # Generar datos de muestra
                from run_ml_strategy import generate_sample_data
                self.data = generate_sample_data(days=365)
                
                self.symbol_info = {
                    'point': 0.01,
                    'digits': 2,
                    'trade_contract_size': 100.0
                }
                
                messagebox.showinfo("Éxito", 
                    f"Datos de muestra cargados: {len(self.data)} barras")
            
            elif source == "MT5":
                # Tu código existente para cargar de MT5
                pass
            
            elif source == "CSV":
                # Tu código existente para cargar de CSV
                pass
        
        def run_backtest(self):
            """Ejecuta el backtest"""
            if self.data is None:
                messagebox.showerror("Error", "Primero carga los datos")
                return
            
            # Determinar qué estrategia usar
            current_tab = self.notebook.index(self.notebook.select())
            
            if current_tab == 2:  # Pestaña de ML Strategy
                # Obtener estrategia ML configurada
                strategy = self.ml_integration.get_strategy_instance()
                strategy_name = "ML Advanced"
            else:
                # Estrategia tradicional
                strategy_name = self.traditional_strategy_var.get()
                strategy = self.get_traditional_strategy(strategy_name)
            
            # Configurar backtest
            config = BacktestConfig(
                initial_capital=self.capital_var.get(),
                commission_pct=self.commission_var.get() / 100,
                slippage_pct=self.slippage_var.get() / 100
            )
            
            # Ejecutar
            try:
                engine = BacktestEngine(config)
                result = engine.run(strategy, self.data, self.symbol_info)
                
                # Actualizar estado si es ML
                if strategy_name == "ML Advanced":
                    self.ml_integration.update_status(strategy)
                
                # Mostrar resultados
                self.display_results(result, strategy_name)
                
                messagebox.showinfo("Éxito", 
                    f"Backtest completado: {result.total_trades} trades")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error en backtest: {str(e)}")
        
        def get_traditional_strategy(self, name):
            """Obtiene estrategia tradicional por nombre"""
            # Tu código existente para crear estrategias tradicionales
            pass
        
        def display_results(self, result, strategy_name):
            """Muestra resultados en el text widget"""
            self.results_text.delete(1.0, tk.END)
            
            text = f"""
╔══════════════════════════════════════════════════════════════╗
║              RESULTADOS DEL BACKTEST                         ║
╚══════════════════════════════════════════════════════════════╝

Estrategia: {strategy_name}

{result.summary()}
"""
            self.results_text.insert(1.0, text)
        
        def show_reports(self):
            """Muestra reportes HTML generados"""
            messagebox.showinfo("Reportes", 
                "Los reportes HTML están en: ml_backtest_results/")
    
    
    # Ejecutar aplicación
    if __name__ == '__main__':
        root = tk.Tk()
        app = BacktestGUI(root)
        root.mainloop()


# ============================================================================
# CÓDIGO PARA COPIAR Y PEGAR
# ============================================================================

"""
PASO 1: Importar al inicio de tu archivo gui_backtest.py
"""

# Agregar al inicio de tu archivo:
from ml_strategy_gui_integration import integrate_ml_strategy_to_gui
from strategies.ml_advanced_strategy import MLAdvancedStrategy


"""
PASO 2: En tu __init__, agregar la integración
"""

# Dentro de tu __init__:
def __init__(self, root):
    # ... tu código existente ...
    
    # ¡AGREGAR ESTO!
    self.ml_integration = integrate_ml_strategy_to_gui(self.notebook)


"""
PASO 3: Modificar tu método run_backtest
"""

# Modificar tu método existente:
def run_backtest(self):
    # Detectar si es estrategia ML
    if self.strategy_var.get() == "ML Advanced":
        # Obtener estrategia ML desde la GUI
        strategy = self.ml_integration.get_strategy_instance()
    else:
        # Tu código existente
        strategy = self.get_selected_strategy()
    
    # Ejecutar backtest normalmente
    result = self.engine.run(strategy, self.data, self.symbol_info)
    
    # Actualizar UI de ML si corresponde
    if isinstance(strategy, MLAdvancedStrategy):
        self.ml_integration.update_status(strategy)
    
    # Tu código existente para mostrar resultados
    self.display_results(result)


"""
PASO 4: Agregar ML a tu lista de estrategias
"""

# En tu combobox o lista de estrategias, agregar:
STRATEGIES = [
    "Moving Average Crossover",
    "RSI Strategy",
    "MACD Strategy",
    "ML Advanced",  # ← AGREGAR
]


# ============================================================================
# ¡ESO ES TODO!
# ============================================================================

print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     INTEGRACIÓN COMPLETA - 4 PASOS SIMPLES                  ║
║                                                              ║
║  1. Importar módulos ML                                     ║
║  2. Agregar integrate_ml_strategy_to_gui(notebook)          ║
║  3. Modificar run_backtest()                                ║
║  4. Agregar "ML Advanced" a lista de estrategias            ║
║                                                              ║
║                  ¡LISTO! 🚀                                 ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")
