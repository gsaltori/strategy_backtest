"""
Interfaz Gráfica Mejorada para Sistema de Backtesting
Permite probar diferentes estrategias de forma interactiva con múltiples indicadores
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import queue
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import MetaTrader5 as mt5
from typing import Optional, Dict, List
import json
import os
import sys

# Imports del proyecto
try:
    from config.settings import BacktestConfig, MT5Config, TIMEFRAMES
    from backtest_engine import BacktestEngine
    from data_manager import MT5DataManager
    
    # Intentar importar todas las estrategias disponibles
    from strategies.two_bearish_pattern_strategy import TwoBearishPatternStrategy
    
    try:
        from strategies.moving_average_crossover import MovingAverageCrossover
        MOVING_AVERAGE_AVAILABLE = True
    except ImportError:
        MOVING_AVERAGE_AVAILABLE = False
    
    try:
        from strategies.ny_range_breakout_strategy import NYRangeBreakout
        NY_RANGE_AVAILABLE = True
    except ImportError:
        NY_RANGE_AVAILABLE = False
    
    # Intentar importar optimizador ML
    try:
        from ml_optimizer import MLStrategyOptimizer
        ML_OPTIMIZER_AVAILABLE = True
    except ImportError:
        ML_OPTIMIZER_AVAILABLE = False
        print("⚠️ ML Optimizer no disponible (opcional)")
        
except ImportError as e:
    print(f"Error importando módulos: {e}")
    print("Asegúrate de ejecutar desde el directorio del proyecto")
    sys.exit(1)


# Diccionario de estrategias disponibles
AVAILABLE_STRATEGIES = {
    "Two Bearish Pattern": {
        "class": TwoBearishPatternStrategy,
        "description": "Patrón de dos velas bajistas consecutivas",
        "params": {
            "risk_reward_ratio": (1.0, 5.0, 2.0),
            "risk_per_trade": (0.5, 5.0, 2.0),
            "min_body_ratio": (0.3, 0.8, 0.5),
        }
    }
}

# Agregar Moving Average si está disponible
if MOVING_AVERAGE_AVAILABLE:
    AVAILABLE_STRATEGIES["Moving Average Crossover"] = {
        "class": MovingAverageCrossover,
        "description": "Cruce de medias móviles con filtro RSI",
        "params": {
            "fast_period": (5, 50, 10),
            "slow_period": (20, 200, 30),
            "rsi_period": (7, 21, 14),
        }
    }

# Agregar NY Range Breakout si está disponible
if NY_RANGE_AVAILABLE:
    AVAILABLE_STRATEGIES["NY Range Breakout"] = {
        "class": NYRangeBreakout,
        "description": "Breakout del rango de Nueva York (21:50-22:15)",
        "params": {
            "stop_loss_pips": (20, 50, 34),
            "take_profit_pips": (50, 150, 83),
            "min_range_pips": (3, 15, 5),
        }
    }

# Lista de pares de divisas disponibles
AVAILABLE_SYMBOLS = [
    "EURUSD",
    "GBPUSD",
    "USDJPY",
    "AUDUSD",
    "NZDUSD",
    "USDCAD",
    "USDCHF",
    "EURJPY",
    "GBPJPY",
    "EURGBP",
    "XAUUSD",  # Oro
    "XAGUSD",  # Plata
    "BTCUSD",  # Bitcoin (si está disponible)
    "US30",    # Dow Jones
    "NAS100",  # NASDAQ
    "SPX500",  # S&P 500
]

# Lista de indicadores técnicos disponibles
AVAILABLE_INDICATORS = [
    "SMA (Simple Moving Average)",
    "EMA (Exponential Moving Average)",
    "RSI (Relative Strength Index)",
    "MACD (Moving Average Convergence Divergence)",
    "Bollinger Bands",
    "ATR (Average True Range)",
    "Stochastic Oscillator",
    "ADX (Average Directional Index)",
    "CCI (Commodity Channel Index)",
    "Williams %R",
    "OBV (On Balance Volume)",
    "VWAP (Volume Weighted Average Price)"
]


class BacktestGUI:
    """
    Interfaz gráfica principal para el sistema de backtesting
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Backtesting - Trading Strategies v2.0")
        self.root.geometry("1400x900")
        
        # Configurar estilo
        self.setup_style()
        
        # Variables de estado
        self.backtest_running = False
        self.optimization_running = False
        self.current_strategy = None
        self.current_data = None
        self.results = None
        self.optimization_results = None
        self.message_queue = queue.Queue()
        self.data_manager = None
        
        # Crear interfaz
        self.create_widgets()
        
        # Iniciar procesamiento de mensajes
        self.process_queue()
        
        # Mostrar mensaje de bienvenida
        self.log("=" * 70)
        self.log("Sistema de Backtesting v2.0 - Iniciado")
        self.log(f"Estrategias disponibles: {len(AVAILABLE_STRATEGIES)}")
        self.log(f"Indicadores disponibles: {len(AVAILABLE_INDICATORS)}")
        self.log("=" * 70)
        
    def setup_style(self):
        """Configura el estilo visual de la interfaz"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colores modernos
        bg_color = '#1e1e1e'
        fg_color = '#e0e0e0'
        accent_color = '#0d7377'
        secondary_color = '#323232'
        
        # Configurar estilos
        style.configure('TFrame', background=bg_color)
        style.configure('TLabel', background=bg_color, foreground=fg_color, font=('Segoe UI', 9))
        style.configure('TButton', background=accent_color, foreground=fg_color, font=('Segoe UI', 9, 'bold'))
        style.configure('Header.TLabel', font=('Segoe UI', 14, 'bold'), foreground=accent_color)
        style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'), foreground=accent_color)
        style.configure('TCombobox', fieldbackground=secondary_color, background=secondary_color, 
                       foreground=fg_color, arrowcolor=fg_color)
        style.configure('TEntry', fieldbackground=secondary_color, foreground=fg_color)
        style.configure('TLabelframe', background=bg_color, foreground=fg_color, 
                       font=('Segoe UI', 10, 'bold'))
        style.configure('TLabelframe.Label', background=bg_color, foreground=accent_color, 
                       font=('Segoe UI', 10, 'bold'))
        
        self.root.configure(bg=bg_color)
        
    def create_widgets(self):
        """Crea todos los widgets de la interfaz"""
        
        # Frame principal con scroll
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Crear notebook para organizar pestañas
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña 1: Configuración y ejecución
        self.tab_config = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_config, text="⚙️ Configuración")
        
        # Pestaña 2: Análisis de Indicadores
        self.tab_indicators = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_indicators, text="📊 Indicadores")
        
        # Pestaña 3: Resultados
        self.tab_results = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_results, text="📈 Resultados")
        
        # Pestaña 4: Optimización (NUEVA)
        self.tab_optimization = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_optimization, text="🔬 Optimización")
        
        # Crear contenido de cada pestaña
        self.create_config_tab()
        self.create_indicators_tab()
        self.create_results_tab()
        self.create_optimization_tab()  # NUEVO
        
        # Panel inferior: Log
        self.create_log_panel(main_container)
        
    def create_config_tab(self):
        """Crea la pestaña de configuración"""
        
        # Scroll para la pestaña
        canvas = tk.Canvas(self.tab_config, bg='#1e1e1e', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.tab_config, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Título
        title = ttk.Label(scrollable_frame, text="Configuración del Backtest", style='Title.TLabel')
        title.grid(row=0, column=0, columnspan=3, pady=(10, 20), sticky='w')
        
        # --- SECCIÓN 1: Datos ---
        data_frame = ttk.LabelFrame(scrollable_frame, text="📥 Configuración de Datos", padding=15)
        data_frame.grid(row=1, column=0, columnspan=3, sticky='ew', padx=10, pady=5)
        
        # Símbolo (ahora con combobox)
        ttk.Label(data_frame, text="Símbolo:").grid(row=0, column=0, sticky='w', pady=5)
        self.symbol_var = tk.StringVar(value="EURUSD")
        symbol_combo = ttk.Combobox(
            data_frame,
            textvariable=self.symbol_var,
            values=AVAILABLE_SYMBOLS,
            state='normal',  # Permite editar pero sugiere valores
            width=18
        )
        symbol_combo.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        
        # Tooltip para el símbolo
        ttk.Label(
            data_frame,
            text="(Editable: puedes escribir otro símbolo)",
            foreground='#888888',
            font=('Segoe UI', 7)
        ).grid(row=0, column=2, sticky='w', padx=5)
        
        # Timeframe
        ttk.Label(data_frame, text="Timeframe:").grid(row=0, column=2, sticky='w', pady=5, padx=(20,0))
        self.timeframe_var = tk.StringVar(value="H1")
        timeframe_combo = ttk.Combobox(
            data_frame, 
            textvariable=self.timeframe_var,
            values=list(TIMEFRAMES.keys()),
            state='readonly',
            width=15
        )
        timeframe_combo.grid(row=0, column=3, padx=5, pady=5, sticky='w')
        
        # Fechas
        ttk.Label(data_frame, text="Fecha Inicio:").grid(row=1, column=0, sticky='w', pady=5)
        self.start_date_var = tk.StringVar(value=(datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"))
        start_entry = ttk.Entry(data_frame, textvariable=self.start_date_var, width=20)
        start_entry.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Label(data_frame, text="Fecha Fin:").grid(row=1, column=2, sticky='w', pady=5, padx=(20,0))
        self.end_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        end_entry = ttk.Entry(data_frame, textvariable=self.end_date_var, width=20)
        end_entry.grid(row=1, column=3, padx=5, pady=5, sticky='w')
        
        # Botón cargar datos
        load_btn = ttk.Button(data_frame, text="📥 Cargar Datos", command=self.load_data)
        load_btn.grid(row=2, column=0, columnspan=4, pady=10)
        
        # --- SECCIÓN 2: Estrategias ---
        strategy_frame = ttk.LabelFrame(scrollable_frame, text="🎯 Selección de Estrategia", padding=15)
        strategy_frame.grid(row=2, column=0, columnspan=3, sticky='ew', padx=10, pady=5)
        
        # Lista de estrategias disponibles
        ttk.Label(strategy_frame, text="Estrategias Disponibles:", style='Header.TLabel').grid(
            row=0, column=0, columnspan=2, sticky='w', pady=(0, 10)
        )
        
        # Frame para la lista de estrategias
        strategies_list_frame = ttk.Frame(strategy_frame)
        strategies_list_frame.grid(row=1, column=0, columnspan=2, sticky='ew', pady=5)
        
        row = 0
        for strategy_name, strategy_info in AVAILABLE_STRATEGIES.items():
            # Radio button para seleccionar estrategia
            if row == 0:
                self.strategy_var = tk.StringVar(value=strategy_name)
            
            radio = ttk.Radiobutton(
                strategies_list_frame,
                text=f"• {strategy_name}",
                variable=self.strategy_var,
                value=strategy_name,
                command=self.on_strategy_selected
            )
            radio.grid(row=row, column=0, sticky='w', pady=2)
            
            # Descripción
            desc_label = ttk.Label(
                strategies_list_frame,
                text=f"  └ {strategy_info['description']}",
                foreground='#888888',
                font=('Segoe UI', 8)
            )
            desc_label.grid(row=row+1, column=0, sticky='w', padx=(20, 0))
            
            row += 2
        
        # Frame para parámetros de estrategia (se llenará dinámicamente)
        self.strategy_params_frame = ttk.LabelFrame(scrollable_frame, text="🔧 Parámetros de Estrategia", padding=15)
        self.strategy_params_frame.grid(row=3, column=0, columnspan=3, sticky='ew', padx=10, pady=5)
        
        self.strategy_param_widgets = {}
        self.update_strategy_params()
        
        # --- SECCIÓN 3: Configuración de Backtest ---
        backtest_frame = ttk.LabelFrame(scrollable_frame, text="💰 Configuración de Backtest", padding=15)
        backtest_frame.grid(row=4, column=0, columnspan=3, sticky='ew', padx=10, pady=5)
        
        # Capital inicial
        ttk.Label(backtest_frame, text="Capital Inicial ($):").grid(row=0, column=0, sticky='w', pady=5)
        self.capital_var = tk.StringVar(value="10000")
        capital_entry = ttk.Entry(backtest_frame, textvariable=self.capital_var, width=20)
        capital_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        
        # Comisión
        ttk.Label(backtest_frame, text="Comisión (%):").grid(row=0, column=2, sticky='w', pady=5, padx=(20,0))
        self.commission_var = tk.StringVar(value="0.1")
        commission_entry = ttk.Entry(backtest_frame, textvariable=self.commission_var, width=20)
        commission_entry.grid(row=0, column=3, padx=5, pady=5, sticky='w')
        
        # Slippage
        ttk.Label(backtest_frame, text="Slippage (%):").grid(row=1, column=0, sticky='w', pady=5)
        self.slippage_var = tk.StringVar(value="0.05")
        slippage_entry = ttk.Entry(backtest_frame, textvariable=self.slippage_var, width=20)
        slippage_entry.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        
        # Usar spread
        self.use_spread_var = tk.BooleanVar(value=True)
        spread_check = ttk.Checkbutton(backtest_frame, text="Usar Spread Real", variable=self.use_spread_var)
        spread_check.grid(row=1, column=2, columnspan=2, sticky='w', pady=5, padx=(20,0))
        
        # --- SECCIÓN 4: Botones de Control ---
        control_frame = ttk.Frame(scrollable_frame)
        control_frame.grid(row=5, column=0, columnspan=3, pady=20)
        
        # Botón ejecutar
        self.run_btn = ttk.Button(
            control_frame,
            text="🚀 Ejecutar Backtest",
            command=self.run_backtest,
            width=25
        )
        self.run_btn.pack(side=tk.LEFT, padx=5)
        
        # Botón detener
        self.stop_btn = ttk.Button(
            control_frame,
            text="⏹ Detener",
            command=self.stop_backtest,
            width=25,
            state='disabled'
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
    def create_indicators_tab(self):
        """Crea la pestaña de análisis de indicadores"""
        
        # Frame principal
        main_frame = ttk.Frame(self.tab_indicators)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title = ttk.Label(main_frame, text="Análisis de Indicadores Técnicos", style='Title.TLabel')
        title.pack(pady=(0, 20))
        
        # Frame de selección
        select_frame = ttk.LabelFrame(main_frame, text="📊 Seleccionar Indicador", padding=15)
        select_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(select_frame, text="Indicador:").pack(side=tk.LEFT, padx=5)
        
        self.indicator_var = tk.StringVar(value=AVAILABLE_INDICATORS[0])
        indicator_combo = ttk.Combobox(
            select_frame,
            textvariable=self.indicator_var,
            values=AVAILABLE_INDICATORS,
            state='readonly',
            width=40
        )
        indicator_combo.pack(side=tk.LEFT, padx=5)
        
        calc_btn = ttk.Button(
            select_frame,
            text="📈 Calcular Indicador",
            command=self.calculate_indicator
        )
        calc_btn.pack(side=tk.LEFT, padx=5)
        
        # Frame de información del indicador
        info_frame = ttk.LabelFrame(main_frame, text="ℹ️ Información del Indicador", padding=15)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.indicator_info_text = scrolledtext.ScrolledText(
            info_frame,
            height=20,
            bg='#2b2b2b',
            fg='#e0e0e0',
            font=('Consolas', 10),
            wrap=tk.WORD
        )
        self.indicator_info_text.pack(fill=tk.BOTH, expand=True)
        
        # Información inicial
        self.show_indicator_info()
        
    def create_results_tab(self):
        """Crea la pestaña de resultados"""
        
        # Frame principal
        main_frame = ttk.Frame(self.tab_results)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title = ttk.Label(main_frame, text="Resultados del Backtest", style='Title.TLabel')
        title.pack(pady=(0, 20))
        
        # Frame de métricas principales
        metrics_frame = ttk.LabelFrame(main_frame, text="📊 Métricas Principales", padding=15)
        metrics_frame.pack(fill=tk.X, pady=10)
        
        # Grid de métricas (2 columnas)
        metrics_grid = ttk.Frame(metrics_frame)
        metrics_grid.pack(fill=tk.X)
        
        # Columna 1
        col1 = ttk.Frame(metrics_grid)
        col1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        self.total_trades_var = tk.StringVar(value="-")
        self.create_metric_display(col1, "Total Trades:", self.total_trades_var, 0)
        
        self.win_rate_var = tk.StringVar(value="-")
        self.create_metric_display(col1, "Win Rate:", self.win_rate_var, 1)
        
        self.total_return_var = tk.StringVar(value="-")
        self.create_metric_display(col1, "Total Return:", self.total_return_var, 2)
        
        # Columna 2
        col2 = ttk.Frame(metrics_grid)
        col2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        self.profit_factor_var = tk.StringVar(value="-")
        self.create_metric_display(col2, "Profit Factor:", self.profit_factor_var, 0)
        
        self.final_balance_var = tk.StringVar(value="-")
        self.create_metric_display(col2, "Final Balance:", self.final_balance_var, 1)
        
        self.max_dd_var = tk.StringVar(value="-")
        self.create_metric_display(col2, "Max Drawdown:", self.max_dd_var, 2)
        
        # Frame de acciones
        actions_frame = ttk.Frame(main_frame)
        actions_frame.pack(fill=tk.X, pady=20)
        
        save_btn = ttk.Button(
            actions_frame,
            text="💾 Guardar Resultados",
            command=self.save_results,
            width=25
        )
        save_btn.pack(side=tk.LEFT, padx=5)
        
        charts_btn = ttk.Button(
            actions_frame,
            text="📊 Mostrar Gráficos",
            command=self.show_charts,
            width=25
        )
        charts_btn.pack(side=tk.LEFT, padx=5)
        
    def create_metric_display(self, parent, label_text, var, row):
        """Crea un display de métrica"""
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=0, sticky='ew', pady=5)
        
        ttk.Label(frame, text=label_text, font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT)
        ttk.Label(frame, textvariable=var, font=('Segoe UI', 12), foreground='#0d7377').pack(side=tk.RIGHT)
    
    def create_optimization_tab(self):
        """Crea la pestaña de optimización de parámetros"""
        
        # Frame principal
        main_frame = ttk.Frame(self.tab_optimization)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title = ttk.Label(main_frame, text="Optimización de Parámetros", style='Title.TLabel')
        title.pack(pady=(0, 10))
        
        # Verificar disponibilidad de ML Optimizer
        if not ML_OPTIMIZER_AVAILABLE:
            warning_frame = ttk.Frame(main_frame)
            warning_frame.pack(fill=tk.X, pady=10)
            
            ttk.Label(
                warning_frame,
                text="⚠️ ML Optimizer no está disponible",
                font=('Segoe UI', 12, 'bold'),
                foreground='#ff8800'
            ).pack()
            
            ttk.Label(
                warning_frame,
                text="Para usar optimización avanzada, instala:\n"
                     "pip install scikit-learn scipy",
                foreground='#888888'
            ).pack(pady=5)
            
            ttk.Button(
                warning_frame,
                text="Usar Optimización Simple (Grid Search)",
                command=self.show_simple_optimization
            ).pack(pady=10)
            return
        
        # Frame de configuración
        config_frame = ttk.LabelFrame(main_frame, text="⚙️ Configuración de Optimización", padding=15)
        config_frame.pack(fill=tk.X, pady=10)
        
        # Método de optimización
        ttk.Label(config_frame, text="Método:").grid(row=0, column=0, sticky='w', pady=5)
        self.opt_method_var = tk.StringVar(value="Bayesian")
        method_combo = ttk.Combobox(
            config_frame,
            textvariable=self.opt_method_var,
            values=["Bayesian", "Grid Search", "Random Search"],
            state='readonly',
            width=25
        )
        method_combo.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        
        # Descripción del método
        self.opt_method_desc = tk.StringVar(value="Optimización bayesiana inteligente (recomendado)")
        ttk.Label(
            config_frame,
            textvariable=self.opt_method_desc,
            foreground='#888888',
            font=('Segoe UI', 8)
        ).grid(row=0, column=2, sticky='w', padx=10)
        
        # Bind para actualizar descripción
        method_combo.bind('<<ComboboxSelected>>', self.update_method_description)
        
        # Métrica objetivo
        ttk.Label(config_frame, text="Métrica Objetivo:").grid(row=1, column=0, sticky='w', pady=5)
        self.opt_metric_var = tk.StringVar(value="sharpe_ratio")
        metric_combo = ttk.Combobox(
            config_frame,
            textvariable=self.opt_metric_var,
            values=["sharpe_ratio", "total_return", "profit_factor", "win_rate"],
            state='readonly',
            width=25
        )
        metric_combo.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        
        # Número de iteraciones
        ttk.Label(config_frame, text="Iteraciones:").grid(row=2, column=0, sticky='w', pady=5)
        self.opt_iterations_var = tk.StringVar(value="30")
        iter_spinbox = ttk.Spinbox(
            config_frame,
            from_=10,
            to=100,
            textvariable=self.opt_iterations_var,
            width=23
        )
        iter_spinbox.grid(row=2, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Label(
            config_frame,
            text="Más iteraciones = mejor resultado pero más lento",
            foreground='#888888',
            font=('Segoe UI', 8)
        ).grid(row=2, column=2, sticky='w', padx=10)
        
        # Porcentaje de validación
        ttk.Label(config_frame, text="Validación (%):").grid(row=3, column=0, sticky='w', pady=5)
        self.opt_validation_var = tk.StringVar(value="30")
        val_spinbox = ttk.Spinbox(
            config_frame,
            from_=20,
            to=50,
            textvariable=self.opt_validation_var,
            width=23
        )
        val_spinbox.grid(row=3, column=1, padx=5, pady=5, sticky='w')
        
        # Botones de acción
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=20)
        
        self.opt_start_btn = ttk.Button(
            action_frame,
            text="🚀 Iniciar Optimización",
            command=self.start_optimization,
            width=30
        )
        self.opt_start_btn.pack(side=tk.LEFT, padx=5)
        
        self.opt_stop_btn = ttk.Button(
            action_frame,
            text="⏹ Detener",
            command=self.stop_optimization,
            width=30,
            state='disabled'
        )
        self.opt_stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Frame de resultados
        results_frame = ttk.LabelFrame(main_frame, text="📊 Resultados de Optimización", padding=15)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Progress bar
        ttk.Label(results_frame, text="Progreso:").pack(anchor='w', pady=5)
        self.opt_progress = ttk.Progressbar(
            results_frame,
            mode='determinate',
            length=500
        )
        self.opt_progress.pack(fill=tk.X, pady=5)
        
        # Área de texto para resultados
        self.opt_results_text = scrolledtext.ScrolledText(
            results_frame,
            height=15,
            bg='#2b2b2b',
            fg='#e0e0e0',
            font=('Consolas', 9),
            wrap=tk.WORD
        )
        self.opt_results_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Información inicial
        self.opt_results_text.insert('1.0', """
╔══════════════════════════════════════════════════════════════╗
║         OPTIMIZACIÓN DE PARÁMETROS CON MACHINE LEARNING      ║
╚══════════════════════════════════════════════════════════════╝

La optimización encuentra los mejores parámetros para tu estrategia
usando algoritmos inteligentes de Machine Learning.

📋 MÉTODOS DISPONIBLES:

• Bayesian Optimization (Recomendado)
  └─> Usa aprendizaje bayesiano para buscar eficientemente
  └─> Aprende de cada iteración para mejorar la búsqueda
  └─> Ideal para 20-50 iteraciones

• Grid Search
  └─> Prueba todas las combinaciones en una malla
  └─> Exhaustivo pero puede ser lento
  └─> Útil para espacios pequeños de parámetros

• Random Search
  └─> Prueba combinaciones aleatorias
  └─> Rápido y sorprendentemente efectivo
  └─> Bueno para exploración inicial

🎯 MÉTRICAS OBJETIVO:

• Sharpe Ratio: Retorno ajustado por riesgo (recomendado)
• Total Return: Retorno total del período
• Profit Factor: Ganancias / Pérdidas
• Win Rate: Porcentaje de trades ganadores

⚙️ PASOS:

1. Cargar datos primero en la pestaña "Configuración"
2. Seleccionar método y configuración
3. Clic en "Iniciar Optimización"
4. Esperar resultados (puede tardar varios minutos)
5. Los mejores parámetros se mostrarán aquí

💡 CONSEJO:

Para resultados confiables:
- Usa al menos 6 meses de datos
- Configura validación de 30%
- Usa 30-50 iteraciones
- Verifica que no haya overfitting
        """)
        
        # Botones de exportación
        export_frame = ttk.Frame(results_frame)
        export_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(
            export_frame,
            text="💾 Guardar Resultados",
            command=self.save_optimization_results
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            export_frame,
            text="📊 Aplicar Mejores Parámetros",
            command=self.apply_best_parameters
        ).pack(side=tk.LEFT, padx=5)
        
    def create_log_panel(self, parent):
        """Crea el panel de log"""
        log_frame = ttk.LabelFrame(parent, text="📝 Log de Eventos", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Crear scrolled text para el log
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=10,
            bg='#1e1e1e',
            fg='#00ff00',
            font=('Consolas', 9),
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Configurar tags para colores
        self.log_text.tag_config('error', foreground='#ff4444')
        self.log_text.tag_config('warning', foreground='#ffaa00')
        self.log_text.tag_config('success', foreground='#00ff00')
        self.log_text.tag_config('info', foreground='#00aaff')
        
    def on_strategy_selected(self):
        """Se llama cuando se selecciona una estrategia"""
        self.update_strategy_params()
        
    def update_strategy_params(self):
        """Actualiza los parámetros mostrados según la estrategia seleccionada"""
        # Limpiar widgets anteriores
        for widget in self.strategy_params_frame.winfo_children():
            widget.destroy()
        
        self.strategy_param_widgets.clear()
        
        strategy_name = self.strategy_var.get()
        if strategy_name not in AVAILABLE_STRATEGIES:
            return
        
        strategy_info = AVAILABLE_STRATEGIES[strategy_name]
        params = strategy_info['params']
        
        row = 0
        for param_name, (min_val, max_val, default_val) in params.items():
            # Label
            label_text = param_name.replace('_', ' ').title() + ":"
            ttk.Label(self.strategy_params_frame, text=label_text).grid(
                row=row, column=0, sticky='w', pady=5, padx=5
            )
            
            # Entry
            var = tk.StringVar(value=str(default_val))
            entry = ttk.Entry(self.strategy_params_frame, textvariable=var, width=15)
            entry.grid(row=row, column=1, pady=5, padx=5, sticky='w')
            
            # Info
            info_text = f"({min_val} - {max_val})"
            ttk.Label(
                self.strategy_params_frame,
                text=info_text,
                foreground='#888888',
                font=('Segoe UI', 8)
            ).grid(row=row, column=2, sticky='w', padx=5)
            
            self.strategy_param_widgets[param_name] = var
            row += 1
        
    def log(self, message: str, level: str = 'info'):
        """
        Añade un mensaje al log
        
        Args:
            message: Mensaje a mostrar
            level: Nivel del mensaje ('info', 'success', 'warning', 'error')
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, formatted_message, level)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def process_queue(self):
        """Procesa mensajes de la cola"""
        try:
            while True:
                msg_type, data = self.message_queue.get_nowait()
                
                if msg_type == "log":
                    self.log(data, 'info')
                elif msg_type == "error":
                    self.log(f"ERROR: {data}", 'error')
                    messagebox.showerror("Error", data)
                elif msg_type == "results":
                    self.show_results(data)
                elif msg_type == "finished":
                    self.backtest_running = False
                    self.run_btn.config(state='normal')
                    self.stop_btn.config(state='disabled')
                elif msg_type == "opt_log":
                    self.opt_results_text.insert(tk.END, f"{data}\n")
                    self.opt_results_text.see(tk.END)
                elif msg_type == "opt_progress":
                    self.opt_progress['value'] = data
                elif msg_type == "opt_error":
                    self.opt_results_text.insert(tk.END, f"\n❌ ERROR: {data}\n", 'error')
                    messagebox.showerror("Error de Optimización", data)
                elif msg_type == "opt_finished":
                    self.optimization_running = False
                    self.opt_start_btn.config(state='normal')
                    self.opt_stop_btn.config(state='disabled')
                    
        except queue.Empty:
            pass
        
        self.root.after(100, self.process_queue)
        
    def load_data(self):
        """Carga datos desde MT5 o genera datos de muestra"""
        try:
            symbol = self.symbol_var.get()
            timeframe = self.timeframe_var.get()
            start_date = datetime.strptime(self.start_date_var.get(), "%Y-%m-%d")
            end_date = datetime.strptime(self.end_date_var.get(), "%Y-%m-%d")
            
            self.log(f"Cargando datos: {symbol} - {timeframe}")
            self.log(f"Periodo: {start_date.date()} a {end_date.date()}")
            
            # Intentar conectar a MT5
            if self.data_manager is None:
                self.data_manager = MT5DataManager()
            
            if self.data_manager.connect():
                self.log("✓ Conexión MT5 establecida", 'success')
                
                # Validar símbolo primero
                if not self.data_manager.validate_symbol(symbol):
                    raise Exception(f"Símbolo {symbol} no disponible en MT5")
                
                # Calcular número de barras aproximado según el timeframe
                days_diff = (end_date - start_date).days
                
                # Estimar barras según timeframe
                if timeframe == 'M1':
                    count = days_diff * 1440  # 1440 minutos por día
                elif timeframe == 'M5':
                    count = days_diff * 288   # 288 barras de 5 min por día
                elif timeframe == 'M15':
                    count = days_diff * 96    # 96 barras de 15 min por día
                elif timeframe == 'M30':
                    count = days_diff * 48    # 48 barras de 30 min por día
                elif timeframe == 'H1':
                    count = days_diff * 24    # 24 horas por día
                elif timeframe == 'H4':
                    count = days_diff * 6     # 6 barras de 4 horas por día
                elif timeframe == 'D1':
                    count = days_diff         # 1 barra por día
                else:
                    count = 5000  # Default
                
                # Limitar a 50000 barras máximo
                count = min(count, 50000)
                
                self.log(f"Descargando aproximadamente {count} barras...")
                
                # Descargar datos usando count en lugar de end_date
                # Esto es más confiable con MT5
                data = self.data_manager.get_historical_data(
                    symbol=symbol,
                    timeframe=timeframe,
                    start_date=start_date,
                    count=count
                )
                
                if data is not None and len(data) > 0:
                    # Filtrar datos hasta end_date si es necesario
                    data = data[data.index <= end_date]
                    
                    if len(data) > 0:
                        self.current_data = data
                        self.log(f"✓ Datos cargados: {len(data)} barras", 'success')
                        self.log(f"Rango real: {data.index[0]} a {data.index[-1]}")
                        messagebox.showinfo(
                            "Éxito", 
                            f"Datos cargados correctamente\n"
                            f"Barras: {len(data)}\n"
                            f"Desde: {data.index[0].strftime('%Y-%m-%d')}\n"
                            f"Hasta: {data.index[-1].strftime('%Y-%m-%d')}"
                        )
                    else:
                        raise Exception("No hay datos en el rango especificado")
                else:
                    raise Exception("No se pudieron obtener datos de MT5")
                    
            else:
                # Si MT5 no está disponible, generar datos de muestra
                self.log("⚠ MT5 no disponible, generando datos de muestra", 'warning')
                self.current_data = self.generate_sample_data(start_date, end_date)
                self.log(f"✓ Datos de muestra generados: {len(self.current_data)} barras", 'success')
                messagebox.showinfo(
                    "Datos de Muestra",
                    f"MT5 no disponible\nSe generaron {len(self.current_data)} barras de muestra"
                )
                
        except Exception as e:
            self.log(f"Error cargando datos: {str(e)}", 'error')
            
            # Si falló MT5, ofrecer datos de muestra
            if "MT5" in str(e) or "No se pudieron obtener" in str(e):
                respuesta = messagebox.askyesno(
                    "Error con MT5",
                    f"No se pudieron cargar datos desde MT5:\n{str(e)}\n\n"
                    "¿Desea generar datos de muestra para probar?"
                )
                
                if respuesta:
                    try:
                        start_date = datetime.strptime(self.start_date_var.get(), "%Y-%m-%d")
                        end_date = datetime.strptime(self.end_date_var.get(), "%Y-%m-%d")
                        self.current_data = self.generate_sample_data(start_date, end_date)
                        self.log(f"✓ Datos de muestra generados: {len(self.current_data)} barras", 'success')
                        messagebox.showinfo("Éxito", f"Datos de muestra generados\n{len(self.current_data)} barras")
                    except Exception as e2:
                        messagebox.showerror("Error", f"No se pudieron generar datos de muestra:\n{str(e2)}")
            else:
                messagebox.showerror("Error", f"No se pudieron cargar los datos:\n{str(e)}")
            
    def generate_sample_data(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Genera datos de muestra para testing"""
        num_bars = int((end_date - start_date).total_seconds() / 3600)  # Barras horarias
        
        dates = pd.date_range(start=start_date, end=end_date, periods=num_bars)
        
        # Generar precios sintéticos
        np.random.seed(42)
        base_price = 1.1000
        returns = np.random.normal(0, 0.0005, num_bars)
        prices = base_price * (1 + returns).cumprod()
        
        # Crear OHLC
        data = pd.DataFrame({
            'time': dates,
            'open': prices,
            'high': prices * (1 + np.abs(np.random.normal(0, 0.0003, num_bars))),
            'low': prices * (1 - np.abs(np.random.normal(0, 0.0003, num_bars))),
            'close': prices * (1 + np.random.normal(0, 0.0002, num_bars)),
            'volume': np.random.randint(1000, 10000, num_bars)
        })
        
        data.set_index('time', inplace=True)
        return data
        
    def run_backtest(self):
        """Ejecuta el backtest en un hilo separado"""
        if self.current_data is None:
            messagebox.showwarning("Advertencia", "Primero debes cargar los datos")
            return
        
        if self.backtest_running:
            messagebox.showwarning("Advertencia", "Ya hay un backtest en ejecución")
            return
        
        # Validar parámetros
        try:
            initial_capital = float(self.capital_var.get())
            commission_pct = float(self.commission_var.get()) / 100
            slippage_pct = float(self.slippage_var.get()) / 100
        except ValueError:
            messagebox.showerror("Error", "Los valores numéricos son inválidos")
            return
        
        # Cambiar estado
        self.backtest_running = True
        self.run_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        
        # Ejecutar en hilo separado
        thread = threading.Thread(target=self._run_backtest_thread, args=(
            initial_capital,
            commission_pct,
            slippage_pct
        ))
        thread.daemon = True
        thread.start()
        
    def _run_backtest_thread(self, initial_capital: float, commission_pct: float, slippage_pct: float):
        """Ejecuta el backtest (función del hilo)"""
        try:
            self.message_queue.put(("log", "Iniciando backtest..."))
            
            # Crear configuración
            config = BacktestConfig(
                initial_capital=initial_capital,
                commission_pct=commission_pct,
                slippage_pct=slippage_pct,
                use_spread=self.use_spread_var.get()
            )
            
            # Obtener estrategia seleccionada
            strategy_name = self.strategy_var.get()
            strategy_class = AVAILABLE_STRATEGIES[strategy_name]['class']
            
            # Obtener parámetros
            params = {}
            for param_name, var in self.strategy_param_widgets.items():
                try:
                    value = float(var.get())
                    params[param_name] = value
                except ValueError:
                    self.message_queue.put(("error", f"Valor inválido para {param_name}"))
                    return
            
            # Crear estrategia
            self.message_queue.put(("log", f"Creando estrategia: {strategy_name}"))
            self.current_strategy = strategy_class(**params)
            
            # Crear motor de backtest
            engine = BacktestEngine(config)
            
            # Ejecutar backtest
            self.message_queue.put(("log", "Ejecutando simulación..."))
            self.results = engine.run(self.current_strategy, self.current_data)
            
            # Mostrar resumen
            metrics = self.results.metrics
            self.message_queue.put(("log", "=" * 50))
            self.message_queue.put(("log", "RESULTADOS:"))
            self.message_queue.put(("log", f"Total Trades: {metrics.get('total_trades', 0)}"))
            self.message_queue.put(("log", f"Win Rate: {metrics.get('win_rate', 0)*100:.1f}%"))
            self.message_queue.put(("log", f"Profit Factor: {metrics.get('profit_factor', 0):.2f}"))
            self.message_queue.put(("log", f"Max Drawdown: {metrics.get('max_drawdown', 0)*100:.2f}%"))
            self.message_queue.put(("log", "=" * 50))
            
            self.message_queue.put(("log", "Backtest completado"))
            self.message_queue.put(("results", self.results))
            
        except Exception as e:
            self.message_queue.put(("error", str(e)))
        finally:
            self.message_queue.put(("finished", None))
            
    def stop_backtest(self):
        """Detiene el backtest"""
        self.backtest_running = False
        self.log("Deteniendo backtest...", 'warning')
        
    def show_results(self, results):
        """Muestra los resultados en la interfaz"""
        metrics = results.metrics
        
        # Calcular retorno
        total_return = (results.final_capital / results.initial_capital) - 1
        
        # Actualizar variables
        self.total_trades_var.set(str(metrics.get('total_trades', 0)))
        self.win_rate_var.set(f"{metrics.get('win_rate', 0)*100:.1f}%")
        self.total_return_var.set(f"{total_return*100:.2f}%")
        self.profit_factor_var.set(f"{metrics.get('profit_factor', 0):.2f}")
        self.final_balance_var.set(f"${results.final_capital:,.2f}")
        self.max_dd_var.set(f"{metrics.get('max_drawdown', 0)*100:.2f}%")
        
        # Cambiar a la pestaña de resultados
        self.notebook.select(self.tab_results)
        
        self.log("✓ Resultados actualizados", 'success')
        
    def save_results(self):
        """Guarda los resultados en un archivo"""
        if self.results is None:
            messagebox.showwarning("Advertencia", "No hay resultados para guardar")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=(("JSON files", "*.json"), ("CSV files", "*.csv"), ("All files", "*.*"))
        )
        
        if filename:
            try:
                if filename.endswith('.json'):
                    # Guardar como JSON
                    data = {
                        'timestamp': datetime.now().isoformat(),
                        'strategy': self.strategy_var.get(),
                        'metrics': self.results.metrics,
                        'initial_capital': self.results.initial_capital,
                        'final_capital': self.results.final_capital,
                        'total_trades': len(self.results.trades)
                    }
                    
                    with open(filename, 'w') as f:
                        json.dump(data, f, indent=2, default=str)
                        
                elif filename.endswith('.csv'):
                    # Guardar trades como CSV
                    trades_data = []
                    for trade in self.results.trades:
                        trades_data.append({
                            'entry_time': trade.entry_time,
                            'exit_time': trade.exit_time,
                            'type': trade.type.value,
                            'entry_price': trade.entry_price,
                            'exit_price': trade.exit_price,
                            'size': trade.size,
                            'pnl': trade.pnl,
                            'pnl_pct': trade.pnl_pct
                        })
                    
                    df = pd.DataFrame(trades_data)
                    df.to_csv(filename, index=False)
                
                self.log(f"Resultados guardados en: {filename}", 'success')
                messagebox.showinfo("Éxito", "Resultados guardados correctamente")
                
            except Exception as e:
                self.log(f"ERROR al guardar: {str(e)}", 'error')
                messagebox.showerror("Error", f"No se pudieron guardar los resultados:\n{str(e)}")
                
    def show_charts(self):
        """Muestra gráficos de los resultados"""
        if self.results is None:
            messagebox.showwarning("Advertencia", "No hay resultados para mostrar")
            return
        
        try:
            # Importar módulo de reportes (corregido)
            from analysis.reporting import ReportGenerator
            
            self.log("Generando gráficos...", 'info')
            
            # Crear generador de reportes
            # NOTA: ReportGenerator solo acepta 'result' como parámetro
            report_gen = ReportGenerator(self.results)
            
            # Opción 1: Generar reporte HTML completo (recomendado)
            report_file = 'backtest_report_gui.html'
            report_gen.save_report_html(report_file)
            
            self.log(f"✓ Reporte generado: {report_file}", 'success')
            
            # Abrir en navegador
            import webbrowser
            webbrowser.open(f'file://{os.path.abspath(report_file)}')
            
            messagebox.showinfo(
                "Éxito",
                f"Reporte generado correctamente\n\n"
                f"Archivo: {report_file}\n"
                f"El reporte se abrirá en tu navegador"
            )
            
        except ImportError as e:
            self.log(f"ERROR: Módulo 'reporting' no encontrado", 'error')
            messagebox.showerror(
                "Error",
                "No se pudo importar el módulo de reportes.\n\n"
                "Asegúrate de que existe el archivo:\n"
                "analysis/reporting.py"
            )
        except Exception as e:
            self.log(f"ERROR al generar gráficos: {str(e)}", 'error')
            messagebox.showerror(
                "Error", 
                f"No se pudieron generar los gráficos:\n\n{str(e)}\n\n"
                f"Verifica que Plotly esté instalado:\n"
                f"pip install plotly"
            )
            
    def calculate_indicator(self):
        """Calcula y muestra información del indicador seleccionado"""
        if self.current_data is None:
            messagebox.showwarning("Advertencia", "Primero debes cargar los datos")
            return
        
        indicator_name = self.indicator_var.get()
        
        try:
            self.log(f"Calculando indicador: {indicator_name}", 'info')
            
            # Calcular el indicador según la selección
            if "SMA" in indicator_name:
                result = self.calculate_sma()
            elif "EMA" in indicator_name:
                result = self.calculate_ema()
            elif "RSI" in indicator_name:
                result = self.calculate_rsi()
            elif "MACD" in indicator_name:
                result = self.calculate_macd()
            elif "Bollinger" in indicator_name:
                result = self.calculate_bollinger_bands()
            elif "ATR" in indicator_name:
                result = self.calculate_atr()
            elif "Stochastic" in indicator_name:
                result = self.calculate_stochastic()
            elif "ADX" in indicator_name:
                result = self.calculate_adx()
            else:
                result = "Indicador no implementado aún"
            
            # Mostrar resultado
            self.indicator_info_text.delete('1.0', tk.END)
            self.indicator_info_text.insert('1.0', result)
            
            self.log(f"✓ Indicador calculado", 'success')
            
        except Exception as e:
            self.log(f"ERROR calculando indicador: {str(e)}", 'error')
            messagebox.showerror("Error", f"No se pudo calcular el indicador:\n{str(e)}")
            
    def show_indicator_info(self):
        """Muestra información sobre indicadores técnicos"""
        info = """
╔════════════════════════════════════════════════════════════════╗
║           INDICADORES TÉCNICOS DISPONIBLES                     ║
╚════════════════════════════════════════════════════════════════╝

Selecciona un indicador del menú desplegable y haz clic en 
"Calcular Indicador" para ver sus valores actuales basados en 
los datos cargados.

📊 INDICADORES DISPONIBLES:

• SMA (Simple Moving Average)
  - Media móvil simple
  - Suaviza la acción del precio
  - Útil para identificar tendencias

• EMA (Exponential Moving Average)
  - Media móvil exponencial
  - Más peso a precios recientes
  - Responde más rápido a cambios

• RSI (Relative Strength Index)
  - Índice de fuerza relativa
  - Rango: 0-100
  - >70: Sobrecompra, <30: Sobreventa

• MACD (Moving Average Convergence Divergence)
  - Convergencia/Divergencia de medias móviles
  - Identifica cambios de tendencia
  - Componentes: MACD, Signal, Histogram

• Bollinger Bands
  - Bandas de volatilidad
  - Banda superior, media e inferior
  - Miden volatilidad del mercado

• ATR (Average True Range)
  - Rango verdadero promedio
  - Mide volatilidad del mercado
  - Mayor ATR = Mayor volatilidad

• Stochastic Oscillator
  - Oscilador estocástico
  - Compara precio de cierre con rango
  - >80: Sobrecompra, <20: Sobreventa

• ADX (Average Directional Index)
  - Índice direccional promedio
  - Mide fuerza de la tendencia
  - >25: Tendencia fuerte

═══════════════════════════════════════════════════════════════

💡 CONSEJO: Carga datos primero para poder calcular indicadores
        """
        
        self.indicator_info_text.delete('1.0', tk.END)
        self.indicator_info_text.insert('1.0', info)
        
    def calculate_sma(self, period: int = 20) -> str:
        """Calcula SMA y devuelve información"""
        sma = self.current_data['close'].rolling(window=period).mean()
        
        current_price = self.current_data['close'].iloc[-1]
        current_sma = sma.iloc[-1]
        
        result = f"""
═══════════════════════════════════════════════════════════════
SMA (Simple Moving Average) - Período {period}
═══════════════════════════════════════════════════════════════

Precio Actual:     {current_price:.5f}
SMA Actual:        {current_sma:.5f}
Diferencia:        {current_price - current_sma:.5f} ({((current_price/current_sma - 1)*100):.2f}%)

Posición:          {'ARRIBA de la SMA (Alcista)' if current_price > current_sma else 'DEBAJO de la SMA (Bajista)'}

Últimos 10 valores:
{'='*60}
"""
        for i in range(-10, 0):
            result += f"{self.current_data.index[i].strftime('%Y-%m-%d %H:%M')} | SMA: {sma.iloc[i]:.5f}\n"
        
        return result
        
    def calculate_ema(self, period: int = 20) -> str:
        """Calcula EMA y devuelve información"""
        ema = self.current_data['close'].ewm(span=period, adjust=False).mean()
        
        current_price = self.current_data['close'].iloc[-1]
        current_ema = ema.iloc[-1]
        
        result = f"""
═══════════════════════════════════════════════════════════════
EMA (Exponential Moving Average) - Período {period}
═══════════════════════════════════════════════════════════════

Precio Actual:     {current_price:.5f}
EMA Actual:        {current_ema:.5f}
Diferencia:        {current_price - current_ema:.5f} ({((current_price/current_ema - 1)*100):.2f}%)

Posición:          {'ARRIBA de la EMA (Alcista)' if current_price > current_ema else 'DEBAJO de la EMA (Bajista)'}

Últimos 10 valores:
{'='*60}
"""
        for i in range(-10, 0):
            result += f"{self.current_data.index[i].strftime('%Y-%m-%d %H:%M')} | EMA: {ema.iloc[i]:.5f}\n"
        
        return result
        
    def calculate_rsi(self, period: int = 14) -> str:
        """Calcula RSI y devuelve información"""
        delta = self.current_data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        current_rsi = rsi.iloc[-1]
        
        # Determinar estado
        if current_rsi > 70:
            estado = "SOBRECOMPRA (Posible corrección bajista)"
        elif current_rsi < 30:
            estado = "SOBREVENTA (Posible corrección alcista)"
        else:
            estado = "NEUTRAL"
        
        result = f"""
═══════════════════════════════════════════════════════════════
RSI (Relative Strength Index) - Período {period}
═══════════════════════════════════════════════════════════════

RSI Actual:        {current_rsi:.2f}
Estado:            {estado}

Niveles:
  Sobrecompra:     > 70
  Neutral:         30 - 70
  Sobreventa:      < 30

Últimos 10 valores:
{'='*60}
"""
        for i in range(-10, 0):
            rsi_val = rsi.iloc[i]
            estado_val = "📈 Sobrecompra" if rsi_val > 70 else "📉 Sobreventa" if rsi_val < 30 else "  Neutral"
            result += f"{self.current_data.index[i].strftime('%Y-%m-%d %H:%M')} | RSI: {rsi_val:.2f} {estado_val}\n"
        
        return result
        
    def calculate_macd(self) -> str:
        """Calcula MACD y devuelve información"""
        exp1 = self.current_data['close'].ewm(span=12, adjust=False).mean()
        exp2 = self.current_data['close'].ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        histogram = macd - signal
        
        current_macd = macd.iloc[-1]
        current_signal = signal.iloc[-1]
        current_hist = histogram.iloc[-1]
        
        # Determinar señal
        if current_macd > current_signal:
            tendencia = "ALCISTA (MACD > Signal)"
        else:
            tendencia = "BAJISTA (MACD < Signal)"
        
        result = f"""
═══════════════════════════════════════════════════════════════
MACD (Moving Average Convergence Divergence)
═══════════════════════════════════════════════════════════════

MACD Actual:       {current_macd:.5f}
Signal Actual:     {current_signal:.5f}
Histogram:         {current_hist:.5f}

Tendencia:         {tendencia}

Últimos 10 valores:
{'='*60}
"""
        for i in range(-10, 0):
            macd_val = macd.iloc[i]
            signal_val = signal.iloc[i]
            hist_val = histogram.iloc[i]
            result += f"{self.current_data.index[i].strftime('%Y-%m-%d %H:%M')} | MACD: {macd_val:.5f} | Signal: {signal_val:.5f} | Hist: {hist_val:.5f}\n"
        
        return result
        
    def calculate_bollinger_bands(self, period: int = 20, std_dev: float = 2) -> str:
        """Calcula Bandas de Bollinger y devuelve información"""
        sma = self.current_data['close'].rolling(window=period).mean()
        std = self.current_data['close'].rolling(window=period).std()
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        current_price = self.current_data['close'].iloc[-1]
        current_upper = upper_band.iloc[-1]
        current_sma = sma.iloc[-1]
        current_lower = lower_band.iloc[-1]
        
        # Determinar posición
        if current_price > current_upper:
            posicion = "ARRIBA de banda superior (Posible sobrecompra)"
        elif current_price < current_lower:
            posicion = "DEBAJO de banda inferior (Posible sobreventa)"
        else:
            posicion = "DENTRO de las bandas"
        
        # Calcular ancho de banda
        bandwidth = ((current_upper - current_lower) / current_sma) * 100
        
        result = f"""
═══════════════════════════════════════════════════════════════
Bollinger Bands - Período {period}, Desv. Est. {std_dev}
═══════════════════════════════════════════════════════════════

Precio Actual:     {current_price:.5f}
Banda Superior:    {current_upper:.5f}
SMA (Media):       {current_sma:.5f}
Banda Inferior:    {current_lower:.5f}

Ancho de Banda:    {bandwidth:.2f}%
Posición:          {posicion}

Últimos 10 valores:
{'='*60}
"""
        for i in range(-10, 0):
            price_val = self.current_data['close'].iloc[i]
            upper_val = upper_band.iloc[i]
            sma_val = sma.iloc[i]
            lower_val = lower_band.iloc[i]
            result += f"{self.current_data.index[i].strftime('%Y-%m-%d %H:%M')} | Price: {price_val:.5f} | Upper: {upper_val:.5f} | Lower: {lower_val:.5f}\n"
        
        return result
        
    def calculate_atr(self, period: int = 14) -> str:
        """Calcula ATR y devuelve información"""
        high = self.current_data['high']
        low = self.current_data['low']
        close = self.current_data['close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        current_atr = atr.iloc[-1]
        current_price = close.iloc[-1]
        
        atr_pct = (current_atr / current_price) * 100
        
        result = f"""
═══════════════════════════════════════════════════════════════
ATR (Average True Range) - Período {period}
═══════════════════════════════════════════════════════════════

ATR Actual:        {current_atr:.5f}
ATR % del Precio:  {atr_pct:.2f}%
Precio Actual:     {current_price:.5f}

Interpretación:
  ATR Alto    = Alta volatilidad
  ATR Bajo    = Baja volatilidad

Últimos 10 valores:
{'='*60}
"""
        for i in range(-10, 0):
            atr_val = atr.iloc[i]
            price_val = close.iloc[i]
            atr_pct_val = (atr_val / price_val) * 100
            result += f"{self.current_data.index[i].strftime('%Y-%m-%d %H:%M')} | ATR: {atr_val:.5f} ({atr_pct_val:.2f}%)\n"
        
        return result
        
    def calculate_stochastic(self, period: int = 14) -> str:
        """Calcula Oscilador Estocástico y devuelve información"""
        high = self.current_data['high']
        low = self.current_data['low']
        close = self.current_data['close']
        
        lowest_low = low.rolling(window=period).min()
        highest_high = high.rolling(window=period).max()
        
        k = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d = k.rolling(window=3).mean()
        
        current_k = k.iloc[-1]
        current_d = d.iloc[-1]
        
        # Determinar estado
        if current_k > 80:
            estado = "SOBRECOMPRA (Posible corrección bajista)"
        elif current_k < 20:
            estado = "SOBREVENTA (Posible corrección alcista)"
        else:
            estado = "NEUTRAL"
        
        result = f"""
═══════════════════════════════════════════════════════════════
Stochastic Oscillator - Período {period}
═══════════════════════════════════════════════════════════════

%K Actual:         {current_k:.2f}
%D Actual:         {current_d:.2f}
Estado:            {estado}

Niveles:
  Sobrecompra:     > 80
  Neutral:         20 - 80
  Sobreventa:      < 20

Últimos 10 valores:
{'='*60}
"""
        for i in range(-10, 0):
            k_val = k.iloc[i]
            d_val = d.iloc[i]
            estado_val = "📈 Sobrecompra" if k_val > 80 else "📉 Sobreventa" if k_val < 20 else "  Neutral"
            result += f"{self.current_data.index[i].strftime('%Y-%m-%d %H:%M')} | %K: {k_val:.2f} | %D: {d_val:.2f} {estado_val}\n"
        
        return result
        
    def calculate_adx(self, period: int = 14) -> str:
        """Calcula ADX y devuelve información"""
        high = self.current_data['high']
        low = self.current_data['low']
        close = self.current_data['close']
        
        # Calcular +DM y -DM
        plus_dm = high.diff()
        minus_dm = -low.diff()
        
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0
        
        # Calcular ATR
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        # Calcular +DI y -DI
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
        
        # Calcular DX y ADX
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()
        
        current_adx = adx.iloc[-1]
        current_plus_di = plus_di.iloc[-1]
        current_minus_di = minus_di.iloc[-1]
        
        # Determinar fuerza de tendencia
        if current_adx > 25:
            fuerza = "FUERTE"
        elif current_adx > 20:
            fuerza = "MODERADA"
        else:
            fuerza = "DÉBIL"
        
        # Determinar dirección
        if current_plus_di > current_minus_di:
            direccion = "ALCISTA (+DI > -DI)"
        else:
            direccion = "BAJISTA (-DI > +DI)"
        
        result = f"""
═══════════════════════════════════════════════════════════════
ADX (Average Directional Index) - Período {period}
═══════════════════════════════════════════════════════════════

ADX Actual:        {current_adx:.2f}
+DI:               {current_plus_di:.2f}
-DI:               {current_minus_di:.2f}

Fuerza Tendencia:  {fuerza}
Dirección:         {direccion}

Interpretación ADX:
  < 20:  Tendencia débil o sin tendencia
  20-25: Tendencia emergente
  25-50: Tendencia fuerte
  > 50:  Tendencia muy fuerte

Últimos 10 valores:
{'='*60}
"""
        for i in range(-10, 0):
            adx_val = adx.iloc[i]
            plus_di_val = plus_di.iloc[i]
            minus_di_val = minus_di.iloc[i]
            result += f"{self.current_data.index[i].strftime('%Y-%m-%d %H:%M')} | ADX: {adx_val:.2f} | +DI: {plus_di_val:.2f} | -DI: {minus_di_val:.2f}\n"
        
        return result
    
    # ========================================================================
    # MÉTODOS DE OPTIMIZACIÓN
    # ========================================================================
    
    def update_method_description(self, event=None):
        """Actualiza la descripción del método seleccionado"""
        method = self.opt_method_var.get()
        
        descriptions = {
            "Bayesian": "Optimización bayesiana inteligente (recomendado)",
            "Grid Search": "Busca en malla exhaustiva (lento pero completo)",
            "Random Search": "Búsqueda aleatoria rápida (exploración inicial)"
        }
        
        self.opt_method_desc.set(descriptions.get(method, ""))
    
    def show_simple_optimization(self):
        """Muestra interfaz de optimización simple sin ML"""
        messagebox.showinfo(
            "Optimización Simple",
            "La optimización simple (Grid Search) está disponible.\n\n"
            "Para optimización avanzada con ML, instala:\n"
            "pip install scikit-learn scipy"
        )
    
    def start_optimization(self):
        """Inicia el proceso de optimización"""
        if self.current_data is None:
            messagebox.showwarning(
                "Advertencia",
                "Primero debes cargar los datos en la pestaña 'Configuración'"
            )
            return
        
        if self.current_strategy is None:
            messagebox.showwarning(
                "Advertencia",
                "Primero debes seleccionar una estrategia en la pestaña 'Configuración'"
            )
            return
        
        if self.optimization_running:
            messagebox.showwarning("Advertencia", "Ya hay una optimización en curso")
            return
        
        # Cambiar estado
        self.optimization_running = True
        self.opt_start_btn.config(state='disabled')
        self.opt_stop_btn.config(state='normal')
        self.opt_progress['value'] = 0
        
        # Limpiar resultados anteriores
        self.opt_results_text.delete('1.0', tk.END)
        self.opt_results_text.insert('1.0', "Iniciando optimización...\n")
        
        # Ejecutar en hilo separado
        thread = threading.Thread(target=self._run_optimization_thread)
        thread.daemon = True
        thread.start()
    
    def _run_optimization_thread(self):
        """Ejecuta la optimización en un hilo separado"""
        try:
            self.message_queue.put(("opt_log", "\n" + "="*70))
            self.message_queue.put(("opt_log", "OPTIMIZACIÓN DE PARÁMETROS"))
            self.message_queue.put(("opt_log", "="*70 + "\n"))
            
            # Obtener configuración
            method = self.opt_method_var.get()
            metric = self.opt_metric_var.get()
            iterations = int(self.opt_iterations_var.get())
            validation_pct = float(self.opt_validation_var.get()) / 100
            
            self.message_queue.put(("opt_log", f"Método: {method}"))
            self.message_queue.put(("opt_log", f"Métrica objetivo: {metric}"))
            self.message_queue.put(("opt_log", f"Iteraciones: {iterations}"))
            self.message_queue.put(("opt_log", f"Validación: {validation_pct*100:.0f}%\n"))
            
            # Obtener clase de estrategia
            strategy_name = self.strategy_var.get()
            strategy_class = AVAILABLE_STRATEGIES[strategy_name]['class']
            
            # Crear symbol_info básico si no está disponible
            symbol_info = {
                'name': self.symbol_var.get(),
                'point': 0.00001,
                'digits': 5,
                'spread': 2,
                'trade_contract_size': 100000,
            }
            
            if not ML_OPTIMIZER_AVAILABLE:
                # Optimización simple (Grid Search)
                self.message_queue.put(("opt_log", "Usando optimización Grid Search simple...\n"))
                result = self._simple_grid_search(
                    strategy_class,
                    metric,
                    iterations
                )
            else:
                # Optimización con ML
                self.message_queue.put(("opt_log", "Creando optimizador ML...\n"))
                
                optimizer = MLStrategyOptimizer(
                    strategy_class=strategy_class,
                    data=self.current_data,
                    symbol_info=symbol_info,
                    target_metric=metric,
                    n_iterations=iterations,
                    validation_pct=validation_pct
                )
                
                self.message_queue.put(("opt_log", "Ejecutando optimización bayesiana...\n"))
                self.message_queue.put(("opt_progress", 20))
                
                result = optimizer.bayesian_optimization()
                
                self.message_queue.put(("opt_progress", 100))
            
            # Guardar resultados
            self.optimization_results = result
            
            # Mostrar resultados
            self.message_queue.put(("opt_log", "\n" + "="*70))
            self.message_queue.put(("opt_log", "RESULTADOS FINALES"))
            self.message_queue.put(("opt_log", "="*70 + "\n"))
            
            self.message_queue.put(("opt_log", "🏆 MEJORES PARÁMETROS ENCONTRADOS:\n"))
            for param, value in result.best_params.items():
                self.message_queue.put(("opt_log", f"   {param}: {value:.4f}" if isinstance(value, float) else f"   {param}: {value}"))
            
            if hasattr(result, 'validation_metrics'):
                self.message_queue.put(("opt_log", "\n📈 MÉTRICAS:\n"))
                self.message_queue.put(("opt_log", f"   Score (train): {result.validation_metrics.get('train_score', 0):.4f}"))
                self.message_queue.put(("opt_log", f"   Score (validation): {result.best_score:.4f}"))
                self.message_queue.put(("opt_log", f"   Ratio Overfitting: {result.validation_metrics.get('overfit_ratio', 0):.2f}"))
                
                # Advertencia de overfitting
                if result.validation_metrics.get('overfit_ratio', 0) > 1.5:
                    self.message_queue.put(("opt_log", "\n⚠️  ADVERTENCIA: Posible overfitting detectado"))
                    self.message_queue.put(("opt_log", "   Considera usar más datos o menos iteraciones"))
            
            if hasattr(result, 'feature_importance') and result.feature_importance:
                self.message_queue.put(("opt_log", "\n🔍 IMPORTANCIA DE PARÁMETROS:\n"))
                sorted_importance = sorted(
                    result.feature_importance.items(),
                    key=lambda x: x[1],
                    reverse=True
                )
                for param, importance in sorted_importance:
                    self.message_queue.put(("opt_log", f"   {param}: {importance:.4f}"))
            
            self.message_queue.put(("opt_log", "\n✅ Optimización completada!"))
            self.message_queue.put(("opt_log", "\nPuedes aplicar estos parámetros con el botón"))
            self.message_queue.put(("opt_log", "'Aplicar Mejores Parámetros' y ejecutar un nuevo backtest."))
            
        except Exception as e:
            self.message_queue.put(("opt_error", str(e)))
        finally:
            self.message_queue.put(("opt_finished", None))
    
    def _simple_grid_search(self, strategy_class, metric, max_combinations):
        """Implementa un grid search simple sin ML"""
        from itertools import product
        
        # Obtener rangos de parámetros de la estrategia
        strategy_name = self.strategy_var.get()
        params_config = AVAILABLE_STRATEGIES[strategy_name]['params']
        
        # Crear malla de búsqueda limitada
        param_grid = {}
        for param_name, (min_val, max_val, default_val) in params_config.items():
            # Crear 5 valores en el rango
            step = (max_val - min_val) / 4
            values = [min_val + i * step for i in range(5)]
            param_grid[param_name] = values
        
        # Generar combinaciones
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())
        combinations = list(product(*param_values))
        
        # Limitar combinaciones
        if len(combinations) > max_combinations:
            import random
            combinations = random.sample(combinations, max_combinations)
        
        self.message_queue.put(("opt_log", f"Probando {len(combinations)} combinaciones...\n"))
        
        best_score = -999
        best_params = None
        all_results = []
        
        config = BacktestConfig(
            initial_capital=float(self.capital_var.get()),
            commission_pct=float(self.commission_var.get()) / 100,
            slippage_pct=float(self.slippage_var.get()) / 100
        )
        
        for i, combination in enumerate(combinations):
            if not self.optimization_running:
                break
            
            # Crear parámetros
            params = dict(zip(param_names, combination))
            
            # Crear estrategia y ejecutar
            try:
                strategy = strategy_class(**params)
                engine = BacktestEngine(config)
                result = engine.run(strategy, self.current_data, {
                    'name': self.symbol_var.get(),
                    'point': 0.00001,
                    'digits': 5,
                    'spread': 2,
                    'trade_contract_size': 100000,
                })
                
                score = result.metrics.get(metric, 0)
                
                all_results.append({
                    'params': params.copy(),
                    'score': score
                })
                
                if score > best_score:
                    best_score = score
                    best_params = params.copy()
                    self.message_queue.put(("opt_log", f"Iteración {i+1}/{len(combinations)}: Nuevo mejor score = {score:.4f}"))
                
                # Actualizar progreso
                progress = int((i + 1) / len(combinations) * 100)
                self.message_queue.put(("opt_progress", progress))
                
            except Exception as e:
                self.message_queue.put(("opt_log", f"Error en iteración {i+1}: {str(e)}"))
        
        # Crear resultado simple
        class SimpleResult:
            def __init__(self, best_params, best_score):
                self.best_params = best_params
                self.best_score = best_score
                self.all_results = pd.DataFrame(all_results)
                self.validation_metrics = {}
                self.feature_importance = {}
        
        return SimpleResult(best_params, best_score)
    
    def stop_optimization(self):
        """Detiene la optimización"""
        self.optimization_running = False
        self.log("Deteniendo optimización...", 'warning')
    
    def save_optimization_results(self):
        """Guarda los resultados de la optimización"""
        if self.optimization_results is None:
            messagebox.showwarning("Advertencia", "No hay resultados de optimización para guardar")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=(("JSON files", "*.json"), ("CSV files", "*.csv"), ("All files", "*.*"))
        )
        
        if filename:
            try:
                if filename.endswith('.json'):
                    data = {
                        'timestamp': datetime.now().isoformat(),
                        'strategy': self.strategy_var.get(),
                        'best_params': self.optimization_results.best_params,
                        'best_score': self.optimization_results.best_score,
                    }
                    
                    if hasattr(self.optimization_results, 'validation_metrics'):
                        data['validation_metrics'] = self.optimization_results.validation_metrics
                    
                    if hasattr(self.optimization_results, 'feature_importance'):
                        data['feature_importance'] = self.optimization_results.feature_importance
                    
                    with open(filename, 'w') as f:
                        json.dump(data, f, indent=2, default=str)
                        
                elif filename.endswith('.csv'):
                    if hasattr(self.optimization_results, 'all_results'):
                        self.optimization_results.all_results.to_csv(filename, index=False)
                
                self.log(f"Resultados de optimización guardados en: {filename}", 'success')
                messagebox.showinfo("Éxito", "Resultados guardados correctamente")
                
            except Exception as e:
                self.log(f"ERROR al guardar: {str(e)}", 'error')
                messagebox.showerror("Error", f"No se pudieron guardar los resultados:\n{str(e)}")
    
    def apply_best_parameters(self):
        """Aplica los mejores parámetros encontrados a la configuración"""
        if self.optimization_results is None:
            messagebox.showwarning("Advertencia", "No hay resultados de optimización disponibles")
            return
        
        try:
            # Actualizar los widgets de parámetros
            for param_name, value in self.optimization_results.best_params.items():
                if param_name in self.strategy_param_widgets:
                    self.strategy_param_widgets[param_name].set(f"{value:.2f}" if isinstance(value, float) else str(value))
            
            self.log("✓ Mejores parámetros aplicados a la estrategia", 'success')
            self.notebook.select(self.tab_config)  # Cambiar a pestaña de configuración
            
            messagebox.showinfo(
                "Parámetros Aplicados",
                "Los mejores parámetros han sido aplicados a la estrategia.\n\n"
                "Ahora puedes ejecutar un nuevo backtest con estos parámetros\n"
                "en la pestaña 'Configuración'."
            )
            
        except Exception as e:
            self.log(f"ERROR al aplicar parámetros: {str(e)}", 'error')
            messagebox.showerror("Error", f"No se pudieron aplicar los parámetros:\n{str(e)}")


def main():
    """Función principal"""
    root = tk.Tk()
    app = BacktestGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()