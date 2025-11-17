"""
Interfaz Gráfica para Sistema de Backtesting
Permite probar diferentes estrategias de forma interactiva
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import queue
from datetime import datetime
import pandas as pd
import MetaTrader5 as mt5
from typing import Optional, Dict, List
import json
import os

# Imports del proyecto
try:
    from config.settings import BacktestConfig
    from backtest_engine import BacktestEngine
    from strategies.two_bearish_pattern_strategy import TwoBearishPatternStrategy
except ImportError as e:
    print(f"Error importando módulos: {e}")
    print("Asegúrate de ejecutar desde el directorio del proyecto")


class BacktestGUI:
    """
    Interfaz gráfica principal para el sistema de backtesting
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Backtesting - Trading Strategies")
        self.root.geometry("1200x800")
        
        # Configurar estilo
        self.setup_style()
        
        # Variables de estado
        self.backtest_running = False
        self.current_strategy = None
        self.current_data = None
        self.results = None
        self.message_queue = queue.Queue()
        
        # Crear interfaz
        self.create_widgets()
        
        # Iniciar procesamiento de mensajes
        self.process_queue()
        
    def setup_style(self):
        """Configura el estilo visual de la interfaz"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colores
        bg_color = '#2b2b2b'
        fg_color = '#ffffff'
        accent_color = '#0d7377'
        
        # Configurar estilos
        style.configure('TFrame', background=bg_color)
        style.configure('TLabel', background=bg_color, foreground=fg_color)
        style.configure('TButton', background=accent_color, foreground=fg_color)
        style.configure('Header.TLabel', font=('Helvetica', 14, 'bold'))
        style.configure('Title.TLabel', font=('Helvetica', 16, 'bold'))
        
        self.root.configure(bg=bg_color)
        
    def create_widgets(self):
        """Crea todos los widgets de la interfaz"""
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # === SECCIÓN 1: CONFIGURACIÓN ===
        self.create_config_section(main_frame)
        
        # === SECCIÓN 2: ESTRATEGIA ===
        self.create_strategy_section(main_frame)
        
        # === SECCIÓN 3: DATOS ===
        self.create_data_section(main_frame)
        
        # === SECCIÓN 4: CONTROLES ===
        self.create_controls_section(main_frame)
        
        # === SECCIÓN 5: RESULTADOS ===
        self.create_results_section(main_frame)
        
        # === SECCIÓN 6: LOG ===
        self.create_log_section(main_frame)
        
    def create_config_section(self, parent):
        """Crea la sección de configuración del backtest"""
        config_frame = ttk.LabelFrame(parent, text="Configuración de Backtest", padding="10")
        config_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Capital Inicial
        ttk.Label(config_frame, text="Capital Inicial:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.capital_var = tk.StringVar(value="10000")
        ttk.Entry(config_frame, textvariable=self.capital_var, width=15).grid(row=0, column=1, padx=5)
        
        # Comisión
        ttk.Label(config_frame, text="Comisión (%):").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.commission_var = tk.StringVar(value="0.0")
        ttk.Entry(config_frame, textvariable=self.commission_var, width=10).grid(row=0, column=3, padx=5)
        
        # Slippage
        ttk.Label(config_frame, text="Slippage (%):").grid(row=0, column=4, sticky=tk.W, padx=5)
        self.slippage_var = tk.StringVar(value="1.0")
        ttk.Entry(config_frame, textvariable=self.slippage_var, width=10).grid(row=0, column=5, padx=5)
        
        # Usar Spread
        self.use_spread_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(config_frame, text="Usar Spread", variable=self.use_spread_var).grid(
            row=0, column=6, padx=5)
        
    def create_strategy_section(self, parent):
        """Crea la sección de selección y configuración de estrategia"""
        strategy_frame = ttk.LabelFrame(parent, text="Estrategia", padding="10")
        strategy_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=(0, 5))
        
        # Selector de estrategia
        ttk.Label(strategy_frame, text="Seleccionar Estrategia:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.strategy_var = tk.StringVar(value="Two Bearish Pattern")
        strategy_combo = ttk.Combobox(strategy_frame, textvariable=self.strategy_var, 
                                     values=["Two Bearish Pattern"], state="readonly", width=30)
        strategy_combo.grid(row=0, column=1, pady=5, sticky=(tk.W, tk.E))
        strategy_combo.bind('<<ComboboxSelected>>', self.on_strategy_selected)
        
        # Frame para parámetros de estrategia
        self.params_frame = ttk.Frame(strategy_frame)
        self.params_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Cargar parámetros de la estrategia inicial
        self.load_strategy_params()
        
    def create_data_section(self, parent):
        """Crea la sección de carga de datos"""
        data_frame = ttk.LabelFrame(parent, text="Datos", padding="10")
        data_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Fuente de datos
        ttk.Label(data_frame, text="Fuente:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.data_source_var = tk.StringVar(value="MetaTrader 5")
        data_source_combo = ttk.Combobox(data_frame, textvariable=self.data_source_var,
                                        values=["MetaTrader 5", "Archivo CSV"], 
                                        state="readonly", width=20)
        data_source_combo.grid(row=0, column=1, pady=5, sticky=(tk.W, tk.E))
        data_source_combo.bind('<<ComboboxSelected>>', self.on_data_source_changed)
        
        # Frame para MT5
        self.mt5_frame = ttk.Frame(data_frame)
        self.mt5_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        ttk.Label(self.mt5_frame, text="Símbolo:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.symbol_var = tk.StringVar(value="EURUSD")
        ttk.Entry(self.mt5_frame, textvariable=self.symbol_var, width=15).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(self.mt5_frame, text="Timeframe:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.timeframe_var = tk.StringVar(value="H4")
        ttk.Combobox(self.mt5_frame, textvariable=self.timeframe_var,
                    values=["M1", "M5", "M15", "M30", "H1", "H4", "D1", "W1"],
                    state="readonly", width=12).grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(self.mt5_frame, text="Barras:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.bars_var = tk.StringVar(value="1000")
        ttk.Entry(self.mt5_frame, textvariable=self.bars_var, width=15).grid(row=2, column=1, padx=5, pady=2)
        
        # Frame para CSV (oculto inicialmente)
        self.csv_frame = ttk.Frame(data_frame)
        
        ttk.Label(self.csv_frame, text="Archivo:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.csv_path_var = tk.StringVar(value="")
        ttk.Entry(self.csv_frame, textvariable=self.csv_path_var, width=25).grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(self.csv_frame, text="Buscar", command=self.browse_csv).grid(row=0, column=2, padx=5, pady=2)
        
        # Botón cargar datos
        ttk.Button(data_frame, text="Cargar Datos", command=self.load_data).grid(
            row=3, column=0, columnspan=2, pady=10)
        
        # Status de datos
        self.data_status_var = tk.StringVar(value="No hay datos cargados")
        ttk.Label(data_frame, textvariable=self.data_status_var, foreground="orange").grid(
            row=4, column=0, columnspan=2)
        
    def create_controls_section(self, parent):
        """Crea la sección de controles principales"""
        controls_frame = ttk.Frame(parent)
        controls_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Botones principales
        self.run_btn = ttk.Button(controls_frame, text="▶ Ejecutar Backtest", 
                                  command=self.run_backtest, width=20)
        self.run_btn.grid(row=0, column=0, padx=5)
        
        self.stop_btn = ttk.Button(controls_frame, text="⏹ Detener", 
                                   command=self.stop_backtest, state=tk.DISABLED, width=20)
        self.stop_btn.grid(row=0, column=1, padx=5)
        
        ttk.Button(controls_frame, text="💾 Guardar Resultados", 
                  command=self.save_results, width=20).grid(row=0, column=2, padx=5)
        
        ttk.Button(controls_frame, text="📊 Ver Gráficos", 
                  command=self.show_charts, width=20).grid(row=0, column=3, padx=5)
        
        ttk.Button(controls_frame, text="🔧 Optimizar", 
                  command=self.optimize_parameters, width=20).grid(row=0, column=4, padx=5)
        
    def create_results_section(self, parent):
        """Crea la sección de resultados"""
        results_frame = ttk.LabelFrame(parent, text="Resultados", padding="10")
        results_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        results_frame.columnconfigure(0, weight=1)
        results_frame.columnconfigure(1, weight=1)
        results_frame.columnconfigure(2, weight=1)
        
        # Métricas principales
        metrics_frame1 = ttk.Frame(results_frame)
        metrics_frame1.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        ttk.Label(metrics_frame1, text="Total Trades:", style='Header.TLabel').pack(anchor=tk.W)
        self.total_trades_var = tk.StringVar(value="-")
        ttk.Label(metrics_frame1, textvariable=self.total_trades_var, font=('Helvetica', 24)).pack(anchor=tk.W)
        
        ttk.Label(metrics_frame1, text="Win Rate:", style='Header.TLabel').pack(anchor=tk.W, pady=(10, 0))
        self.win_rate_var = tk.StringVar(value="-")
        ttk.Label(metrics_frame1, textvariable=self.win_rate_var, font=('Helvetica', 24)).pack(anchor=tk.W)
        
        metrics_frame2 = ttk.Frame(results_frame)
        metrics_frame2.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        ttk.Label(metrics_frame2, text="Retorno Total:", style='Header.TLabel').pack(anchor=tk.W)
        self.total_return_var = tk.StringVar(value="-")
        ttk.Label(metrics_frame2, textvariable=self.total_return_var, font=('Helvetica', 24)).pack(anchor=tk.W)
        
        ttk.Label(metrics_frame2, text="Profit Factor:", style='Header.TLabel').pack(anchor=tk.W, pady=(10, 0))
        self.profit_factor_var = tk.StringVar(value="-")
        ttk.Label(metrics_frame2, textvariable=self.profit_factor_var, font=('Helvetica', 24)).pack(anchor=tk.W)
        
        metrics_frame3 = ttk.Frame(results_frame)
        metrics_frame3.grid(row=0, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        ttk.Label(metrics_frame3, text="Balance Final:", style='Header.TLabel').pack(anchor=tk.W)
        self.final_balance_var = tk.StringVar(value="-")
        ttk.Label(metrics_frame3, textvariable=self.final_balance_var, font=('Helvetica', 24)).pack(anchor=tk.W)
        
        ttk.Label(metrics_frame3, text="Max Drawdown:", style='Header.TLabel').pack(anchor=tk.W, pady=(10, 0))
        self.max_dd_var = tk.StringVar(value="-")
        ttk.Label(metrics_frame3, textvariable=self.max_dd_var, font=('Helvetica', 24)).pack(anchor=tk.W)
        
    def create_log_section(self, parent):
        """Crea la sección de log"""
        log_frame = ttk.LabelFrame(parent, text="Log de Eventos", padding="10")
        log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Text widget con scrollbar
        log_scroll = ttk.Scrollbar(log_frame)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD, yscrollcommand=log_scroll.set,
                               bg='#1e1e1e', fg='#00ff00', font=('Courier', 9))
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scroll.config(command=self.log_text.yview)
        
        # Configurar grid weights para expansión
        parent.rowconfigure(4, weight=1)
        
    def load_strategy_params(self):
        """Carga los parámetros de la estrategia seleccionada"""
        # Limpiar frame
        for widget in self.params_frame.winfo_children():
            widget.destroy()
        
        strategy_name = self.strategy_var.get()
        
        if strategy_name == "Two Bearish Pattern":
            # Parámetros de Two Bearish Pattern
            self.strategy_params = {}
            
            params = [
                ("Risk/Reward Ratio:", "risk_reward_ratio", "2.0"),
                ("Risk per Trade (%):", "risk_per_trade", "2.0"),
                ("Min Body Ratio:", "min_body_ratio", "1.0"),
            ]
            
            for i, (label, key, default) in enumerate(params):
                ttk.Label(self.params_frame, text=label).grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)
                var = tk.StringVar(value=default)
                self.strategy_params[key] = var
                ttk.Entry(self.params_frame, textvariable=var, width=15).grid(row=i, column=1, padx=5, pady=2)
            
            # Trailing stop
            self.use_trailing_var = tk.BooleanVar(value=False)
            ttk.Checkbutton(self.params_frame, text="Usar Trailing Stop", 
                           variable=self.use_trailing_var).grid(row=len(params), column=0, columnspan=2, pady=5)
        
    def on_strategy_selected(self, event=None):
        """Callback cuando se selecciona una estrategia"""
        self.load_strategy_params()
        self.log(f"Estrategia seleccionada: {self.strategy_var.get()}")
        
    def on_data_source_changed(self, event=None):
        """Callback cuando cambia la fuente de datos"""
        source = self.data_source_var.get()
        
        if source == "MetaTrader 5":
            self.csv_frame.grid_forget()
            self.mt5_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))
        else:
            self.mt5_frame.grid_forget()
            self.csv_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        self.log(f"Fuente de datos cambiada a: {source}")
        
    def browse_csv(self):
        """Abre diálogo para seleccionar archivo CSV"""
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo CSV",
            filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))
        )
        if filename:
            self.csv_path_var.set(filename)
            self.log(f"Archivo seleccionado: {filename}")
            
    def load_data(self):
        """Carga los datos desde la fuente seleccionada"""
        self.log("Cargando datos...")
        
        source = self.data_source_var.get()
        
        try:
            if source == "MetaTrader 5":
                self.current_data = self.load_mt5_data()
            else:
                self.current_data = self.load_csv_data()
            
            if self.current_data is not None:
                self.data_status_var.set(f"✓ {len(self.current_data)} barras cargadas")
                self.log(f"Datos cargados exitosamente: {len(self.current_data)} barras")
            else:
                self.data_status_var.set("✗ Error al cargar datos")
                
        except Exception as e:
            self.log(f"ERROR al cargar datos: {str(e)}")
            messagebox.showerror("Error", f"No se pudieron cargar los datos:\n{str(e)}")
            
    def load_mt5_data(self) -> Optional[pd.DataFrame]:
        """Carga datos desde MetaTrader 5"""
        if not mt5.initialize():
            raise Exception("No se pudo inicializar MT5")
        
        try:
            symbol = self.symbol_var.get()
            tf_str = self.timeframe_var.get()
            bars = int(self.bars_var.get())
            
            # Mapeo de timeframes
            timeframes = {
                'M1': mt5.TIMEFRAME_M1, 'M5': mt5.TIMEFRAME_M5,
                'M15': mt5.TIMEFRAME_M15, 'M30': mt5.TIMEFRAME_M30,
                'H1': mt5.TIMEFRAME_H1, 'H4': mt5.TIMEFRAME_H4,
                'D1': mt5.TIMEFRAME_D1, 'W1': mt5.TIMEFRAME_W1
            }
            
            timeframe = timeframes.get(tf_str, mt5.TIMEFRAME_H4)
            
            rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
            
            if rates is None or len(rates) == 0:
                raise Exception(f"No se obtuvieron datos para {symbol}")
            
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df.set_index('time', inplace=True)
            
            return df
            
        finally:
            mt5.shutdown()
            
    def load_csv_data(self) -> Optional[pd.DataFrame]:
        """Carga datos desde archivo CSV"""
        filepath = self.csv_path_var.get()
        
        if not filepath:
            raise Exception("No se ha seleccionado ningún archivo")
        
        df = pd.DataFrame(filepath)
        
        # Intentar parsear columna de tiempo
        if 'time' in df.columns:
            df['time'] = pd.to_datetime(df['time'])
            df.set_index('time', inplace=True)
        elif 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
        
        return df
        
    def run_backtest(self):
        """Ejecuta el backtest en un thread separado"""
        if self.current_data is None:
            messagebox.showwarning("Advertencia", "Primero debes cargar los datos")
            return
        
        self.backtest_running = True
        self.run_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        # Ejecutar en thread separado
        thread = threading.Thread(target=self._run_backtest_thread)
        thread.daemon = True
        thread.start()
        
    def _run_backtest_thread(self):
        """Función que ejecuta el backtest (en thread separado)"""
        try:
            self.message_queue.put(("log", "Iniciando backtest..."))
            
            # Crear configuración
            config = BacktestConfig(
                initial_capital=float(self.capital_var.get()),
                commission_pct=float(self.commission_var.get()) / 100,
                slippage_pct=float(self.slippage_var.get()) / 100,
                use_spread=self.use_spread_var.get()
            )
            
            # Crear estrategia
            strategy_name = self.strategy_var.get()
            
            if strategy_name == "Two Bearish Pattern":
                strategy = TwoBearishPatternStrategy(
                    risk_reward_ratio=float(self.strategy_params['risk_reward_ratio'].get()),
                    risk_per_trade=float(self.strategy_params['risk_per_trade'].get()) / 100,
                    min_body_ratio=float(self.strategy_params['min_body_ratio'].get()),
                    use_trailing_stop=self.use_trailing_var.get()
                )
            
            self.message_queue.put(("log", f"Estrategia: {strategy.name}"))
            
            # Ejecutar backtest
            engine = BacktestEngine(config=config)
            self.results = engine.run(strategy=strategy, data=self.current_data)
            
            self.message_queue.put(("log", "Backtest completado"))
            self.message_queue.put(("results", self.results))
            
        except Exception as e:
            self.message_queue.put(("error", str(e)))
        finally:
            self.message_queue.put(("finished", None))
            
    def stop_backtest(self):
        """Detiene el backtest"""
        self.backtest_running = False
        self.log("Deteniendo backtest...")
        
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
        
        self.log(f"✓ Resultados actualizados")
        
    def save_results(self):
        """Guarda los resultados en un archivo"""
        if self.results is None:
            messagebox.showwarning("Advertencia", "No hay resultados para guardar")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
        )
        
        if filename:
            try:
                # Preparar datos para guardar
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
                
                self.log(f"Resultados guardados en: {filename}")
                messagebox.showinfo("Éxito", "Resultados guardados correctamente")
                
            except Exception as e:
                self.log(f"ERROR al guardar: {str(e)}")
                messagebox.showerror("Error", f"No se pudieron guardar los resultados:\n{str(e)}")
                
    def show_charts(self):
        """Muestra gráficos de los resultados"""
        if self.results is None:
            messagebox.showwarning("Advertencia", "No hay resultados para mostrar")
            return
        
        try:
            from reporting import ReportGenerator
            
            report = ReportGenerator(self.results)
            fig = report.create_full_report()
            fig.show()
            
            self.log("Gráficos mostrados")
            
        except Exception as e:
            self.log(f"ERROR al mostrar gráficos: {str(e)}")
            messagebox.showerror("Error", f"No se pudieron generar los gráficos:\n{str(e)}")
            
    def optimize_parameters(self):
        """Abre ventana de optimización de parámetros"""
        if self.current_data is None:
            messagebox.showwarning("Advertencia", "Primero debes cargar los datos")
            return
        
        # Crear ventana de optimización
        opt_window = OptimizationWindow(self.root, self)
        
    def log(self, message):
        """Añade un mensaje al log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        
    def process_queue(self):
        """Procesa mensajes de la cola"""
        try:
            while True:
                msg_type, data = self.message_queue.get_nowait()
                
                if msg_type == "log":
                    self.log(data)
                elif msg_type == "results":
                    self.show_results(data)
                elif msg_type == "error":
                    self.log(f"ERROR: {data}")
                    messagebox.showerror("Error", f"Error durante el backtest:\n{data}")
                elif msg_type == "finished":
                    self.backtest_running = False
                    self.run_btn.config(state=tk.NORMAL)
                    self.stop_btn.config(state=tk.DISABLED)
                    
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_queue)


class OptimizationWindow:
    """Ventana para optimización de parámetros"""
    
    def __init__(self, parent, main_app):
        self.main_app = main_app
        self.window = tk.Toplevel(parent)
        self.window.title("Optimización de Parámetros")
        self.window.geometry("600x400")
        
        # TODO: Implementar interfaz de optimización
        ttk.Label(self.window, text="Optimización de Parámetros", 
                 style='Title.TLabel').pack(pady=20)
        
        ttk.Label(self.window, text="(En desarrollo)").pack()
        
        ttk.Button(self.window, text="Cerrar", 
                  command=self.window.destroy).pack(pady=20)


def main():
    """Función principal"""
    root = tk.Tk()
    app = BacktestGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()