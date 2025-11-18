"""
Integrador de Estrategia ML con GUI de Backtesting

Este módulo integra la estrategia ML avanzada con la GUI existente,
proporcionando:
1. Panel de configuración de parámetros ML
2. Visualización de métricas de ML en tiempo real
3. Monitoreo de predicciones y confianza
4. Análisis de features importance
5. Gráficos de rendimiento de modelos

Autor: Sistema de Trading Avanzado
Fecha: 2024
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import numpy as np
from typing import Dict, Optional, List
import logging
from datetime import datetime
import json

# Importaciones de la estrategia ML
from strategies.ml_advanced_strategy import MLAdvancedStrategy

logger = logging.getLogger(__name__)


class MLStrategyGUIIntegration:
    """
    Clase para integrar la estrategia ML con la GUI de backtesting
    """
    
    def __init__(self, parent_frame: ttk.Frame):
        """
        Inicializa la integración con la GUI
        
        Args:
            parent_frame: Frame padre de tkinter donde se agregará la UI
        """
        self.parent_frame = parent_frame
        self.strategy = None
        self.params_vars = {}
        
        # Variables de estado
        self.training_status = tk.StringVar(value="No entrenado")
        self.model_accuracy = tk.StringVar(value="N/A")
        self.current_regime = tk.StringVar(value="N/A")
        self.predictions_count = tk.StringVar(value="0")
        
        self._create_ui()
    
    def _create_ui(self):
        """Crea la interfaz de usuario para la estrategia ML"""
        
        # Frame principal
        main_frame = ttk.LabelFrame(
            self.parent_frame, 
            text="🤖 Estrategia ML Avanzada", 
            padding="10"
        )
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # ===== SECCIÓN 1: PARÁMETROS DE ML =====
        ml_params_frame = ttk.LabelFrame(main_frame, text="Parámetros de Machine Learning", padding="5")
        ml_params_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        row = 0
        
        # Lookback Period
        ttk.Label(ml_params_frame, text="Lookback Period:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.params_vars['lookback_period'] = tk.IntVar(value=60)
        ttk.Spinbox(
            ml_params_frame, 
            from_=20, to=200, 
            textvariable=self.params_vars['lookback_period'],
            width=15
        ).grid(row=row, column=1, sticky=tk.W, pady=2, padx=5)
        ttk.Label(ml_params_frame, text="barras", font=('', 8)).grid(row=row, column=2, sticky=tk.W)
        row += 1
        
        # Prediction Threshold
        ttk.Label(ml_params_frame, text="Prediction Threshold:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.params_vars['prediction_threshold'] = tk.DoubleVar(value=0.55)
        ttk.Spinbox(
            ml_params_frame, 
            from_=0.5, to=0.95, increment=0.05,
            textvariable=self.params_vars['prediction_threshold'],
            width=15
        ).grid(row=row, column=1, sticky=tk.W, pady=2, padx=5)
        ttk.Label(ml_params_frame, text="confianza mínima", font=('', 8)).grid(row=row, column=2, sticky=tk.W)
        row += 1
        
        # Retrain Frequency
        ttk.Label(ml_params_frame, text="Retrain Frequency:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.params_vars['retrain_frequency'] = tk.IntVar(value=100)
        ttk.Spinbox(
            ml_params_frame, 
            from_=50, to=500, increment=50,
            textvariable=self.params_vars['retrain_frequency'],
            width=15
        ).grid(row=row, column=1, sticky=tk.W, pady=2, padx=5)
        ttk.Label(ml_params_frame, text="barras", font=('', 8)).grid(row=row, column=2, sticky=tk.W)
        row += 1
        
        # Min Train Samples
        ttk.Label(ml_params_frame, text="Min Train Samples:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.params_vars['min_train_samples'] = tk.IntVar(value=500)
        ttk.Spinbox(
            ml_params_frame, 
            from_=200, to=2000, increment=100,
            textvariable=self.params_vars['min_train_samples'],
            width=15
        ).grid(row=row, column=1, sticky=tk.W, pady=2, padx=5)
        ttk.Label(ml_params_frame, text="muestras", font=('', 8)).grid(row=row, column=2, sticky=tk.W)
        row += 1
        
        # ===== SECCIÓN 2: FEATURES =====
        features_frame = ttk.LabelFrame(main_frame, text="Features a Utilizar", padding="5")
        features_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.params_vars['use_price_features'] = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            features_frame, 
            text="Price Features", 
            variable=self.params_vars['use_price_features']
        ).grid(row=0, column=0, sticky=tk.W, padx=5)
        
        self.params_vars['use_volume_features'] = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            features_frame, 
            text="Volume Features", 
            variable=self.params_vars['use_volume_features']
        ).grid(row=0, column=1, sticky=tk.W, padx=5)
        
        self.params_vars['use_volatility_features'] = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            features_frame, 
            text="Volatility Features", 
            variable=self.params_vars['use_volatility_features']
        ).grid(row=1, column=0, sticky=tk.W, padx=5)
        
        self.params_vars['use_pattern_features'] = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            features_frame, 
            text="Pattern Features", 
            variable=self.params_vars['use_pattern_features']
        ).grid(row=1, column=1, sticky=tk.W, padx=5)
        
        # ===== SECCIÓN 3: GESTIÓN DE RIESGO =====
        risk_frame = ttk.LabelFrame(main_frame, text="Gestión de Riesgo", padding="5")
        risk_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        row = 0
        
        # Risk per Trade
        ttk.Label(risk_frame, text="Risk per Trade:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.params_vars['risk_per_trade'] = tk.DoubleVar(value=0.02)
        ttk.Spinbox(
            risk_frame, 
            from_=0.01, to=0.10, increment=0.01,
            textvariable=self.params_vars['risk_per_trade'],
            width=15
        ).grid(row=row, column=1, sticky=tk.W, pady=2, padx=5)
        ttk.Label(risk_frame, text="% del capital", font=('', 8)).grid(row=row, column=2, sticky=tk.W)
        row += 1
        
        # Max Positions
        ttk.Label(risk_frame, text="Max Positions:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.params_vars['max_positions'] = tk.IntVar(value=3)
        ttk.Spinbox(
            risk_frame, 
            from_=1, to=10,
            textvariable=self.params_vars['max_positions'],
            width=15
        ).grid(row=row, column=1, sticky=tk.W, pady=2, padx=5)
        ttk.Label(risk_frame, text="simultáneas", font=('', 8)).grid(row=row, column=2, sticky=tk.W)
        row += 1
        
        # ATR Multiplier
        ttk.Label(risk_frame, text="ATR Multiplier:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.params_vars['atr_multiplier'] = tk.DoubleVar(value=2.0)
        ttk.Spinbox(
            risk_frame, 
            from_=1.0, to=5.0, increment=0.5,
            textvariable=self.params_vars['atr_multiplier'],
            width=15
        ).grid(row=row, column=1, sticky=tk.W, pady=2, padx=5)
        ttk.Label(risk_frame, text="para SL/TP", font=('', 8)).grid(row=row, column=2, sticky=tk.W)
        row += 1
        
        # Use Dynamic Stops
        self.params_vars['use_dynamic_stops'] = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            risk_frame, 
            text="Usar Stops Dinámicos (basados en volatilidad ML)", 
            variable=self.params_vars['use_dynamic_stops']
        ).grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=2)
        row += 1
        
        # ===== SECCIÓN 4: FILTROS =====
        filters_frame = ttk.LabelFrame(main_frame, text="Filtros de Trading", padding="5")
        filters_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        row = 0
        
        # Min Volatility
        ttk.Label(filters_frame, text="Min Volatility:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.params_vars['min_volatility'] = tk.DoubleVar(value=0.0005)
        ttk.Entry(
            filters_frame, 
            textvariable=self.params_vars['min_volatility'],
            width=15
        ).grid(row=row, column=1, sticky=tk.W, pady=2, padx=5)
        row += 1
        
        # Max Volatility
        ttk.Label(filters_frame, text="Max Volatility:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.params_vars['max_volatility'] = tk.DoubleVar(value=0.05)
        ttk.Entry(
            filters_frame, 
            textvariable=self.params_vars['max_volatility'],
            width=15
        ).grid(row=row, column=1, sticky=tk.W, pady=2, padx=5)
        row += 1
        
        # Min Volume Ratio
        ttk.Label(filters_frame, text="Min Volume Ratio:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.params_vars['min_volume_ratio'] = tk.DoubleVar(value=0.5)
        ttk.Spinbox(
            filters_frame, 
            from_=0.1, to=2.0, increment=0.1,
            textvariable=self.params_vars['min_volume_ratio'],
            width=15
        ).grid(row=row, column=1, sticky=tk.W, pady=2, padx=5)
        row += 1
        
        # Detect Regime
        self.params_vars['detect_regime'] = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            filters_frame, 
            text="Detectar Régimen de Mercado", 
            variable=self.params_vars['detect_regime']
        ).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2)
        row += 1
        
        # Regime Window
        ttk.Label(filters_frame, text="Regime Window:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.params_vars['regime_window'] = tk.IntVar(value=50)
        ttk.Spinbox(
            filters_frame, 
            from_=20, to=200,
            textvariable=self.params_vars['regime_window'],
            width=15
        ).grid(row=row, column=1, sticky=tk.W, pady=2, padx=5)
        row += 1
        
        # ===== SECCIÓN 5: ESTADO Y MÉTRICAS =====
        status_frame = ttk.LabelFrame(main_frame, text="Estado del Modelo ML", padding="5")
        status_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Training Status
        ttk.Label(status_frame, text="Estado:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Label(
            status_frame, 
            textvariable=self.training_status,
            font=('', 9, 'bold')
        ).grid(row=0, column=1, sticky=tk.W, pady=2, padx=5)
        
        # Model Accuracy
        ttk.Label(status_frame, text="Precisión:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Label(
            status_frame, 
            textvariable=self.model_accuracy,
            font=('', 9)
        ).grid(row=1, column=1, sticky=tk.W, pady=2, padx=5)
        
        # Current Regime
        ttk.Label(status_frame, text="Régimen Actual:").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Label(
            status_frame, 
            textvariable=self.current_regime,
            font=('', 9)
        ).grid(row=2, column=1, sticky=tk.W, pady=2, padx=5)
        
        # Predictions Count
        ttk.Label(status_frame, text="Predicciones:").grid(row=3, column=0, sticky=tk.W, pady=2)
        ttk.Label(
            status_frame, 
            textvariable=self.predictions_count,
            font=('', 9)
        ).grid(row=3, column=1, sticky=tk.W, pady=2, padx=5)
        
        # ===== BOTONES DE ACCIÓN =====
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Button(
            buttons_frame,
            text="💾 Guardar Configuración",
            command=self.save_config
        ).grid(row=0, column=0, padx=5)
        
        ttk.Button(
            buttons_frame,
            text="📂 Cargar Configuración",
            command=self.load_config
        ).grid(row=0, column=1, padx=5)
        
        ttk.Button(
            buttons_frame,
            text="🔄 Restablecer Default",
            command=self.reset_to_default
        ).grid(row=0, column=2, padx=5)
        
        # ===== INFORMACIÓN Y AYUDA =====
        info_frame = ttk.LabelFrame(main_frame, text="ℹ️ Información", padding="5")
        info_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        info_text = (
            "Esta estrategia utiliza Machine Learning avanzado con:\n"
            "• Ensemble de modelos (Random Forest, XGBoost, LightGBM)\n"
            "• 50+ features técnicos e ingenieriles\n"
            "• Predicción de dirección y volatilidad\n"
            "• Gestión dinámica de riesgo\n"
            "• Detección automática de regímenes de mercado\n"
            "• Auto-reentrenamiento periódico\n\n"
            "Requiere mínimo 500 barras de datos históricos para entrenar."
        )
        
        ttk.Label(
            info_frame,
            text=info_text,
            justify=tk.LEFT,
            font=('', 8)
        ).grid(row=0, column=0, sticky=tk.W)
    
    def get_strategy_instance(self) -> MLAdvancedStrategy:
        """
        Crea una instancia de la estrategia con los parámetros actuales
        
        Returns:
            Instancia de MLAdvancedStrategy configurada
        """
        params = {
            'lookback_period': self.params_vars['lookback_period'].get(),
            'min_train_samples': self.params_vars['min_train_samples'].get(),
            'retrain_frequency': self.params_vars['retrain_frequency'].get(),
            'prediction_threshold': self.params_vars['prediction_threshold'].get(),
            'use_price_features': self.params_vars['use_price_features'].get(),
            'use_volume_features': self.params_vars['use_volume_features'].get(),
            'use_volatility_features': self.params_vars['use_volatility_features'].get(),
            'use_pattern_features': self.params_vars['use_pattern_features'].get(),
            'risk_per_trade': self.params_vars['risk_per_trade'].get(),
            'max_positions': self.params_vars['max_positions'].get(),
            'use_dynamic_stops': self.params_vars['use_dynamic_stops'].get(),
            'atr_multiplier': self.params_vars['atr_multiplier'].get(),
            'min_volatility': self.params_vars['min_volatility'].get(),
            'max_volatility': self.params_vars['max_volatility'].get(),
            'min_volume_ratio': self.params_vars['min_volume_ratio'].get(),
            'detect_regime': self.params_vars['detect_regime'].get(),
            'regime_window': self.params_vars['regime_window'].get()
        }
        
        self.strategy = MLAdvancedStrategy(**params)
        return self.strategy
    
    def update_status(self, strategy: MLAdvancedStrategy):
        """
        Actualiza el estado mostrado en la UI
        
        Args:
            strategy: Instancia de la estrategia para obtener el estado
        """
        if strategy.is_trained:
            self.training_status.set("✅ Entrenado")
        else:
            self.training_status.set("❌ No entrenado")
        
        # Actualizar régimen
        self.current_regime.set(strategy.current_regime.replace('_', ' ').title())
        
        # Actualizar contador de predicciones
        if hasattr(strategy, 'prediction_accuracy'):
            self.predictions_count.set(str(len(strategy.prediction_accuracy)))
            
            # Calcular accuracy si hay predicciones
            if len(strategy.prediction_accuracy) > 0:
                acc = np.mean(strategy.prediction_accuracy) * 100
                self.model_accuracy.set(f"{acc:.1f}%")
    
    def save_config(self):
        """Guarda la configuración actual en un archivo JSON"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Guardar Configuración ML"
            )
            
            if not filename:
                return
            
            config = {}
            for key, var in self.params_vars.items():
                config[key] = var.get()
            
            with open(filename, 'w') as f:
                json.dump(config, f, indent=4)
            
            messagebox.showinfo(
                "Éxito",
                f"Configuración guardada en:\n{filename}"
            )
            
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Error al guardar configuración:\n{str(e)}"
            )
    
    def load_config(self):
        """Carga una configuración desde un archivo JSON"""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Cargar Configuración ML"
            )
            
            if not filename:
                return
            
            with open(filename, 'r') as f:
                config = json.load(f)
            
            # Actualizar variables
            for key, value in config.items():
                if key in self.params_vars:
                    self.params_vars[key].set(value)
            
            messagebox.showinfo(
                "Éxito",
                f"Configuración cargada desde:\n{filename}"
            )
            
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Error al cargar configuración:\n{str(e)}"
            )
    
    def reset_to_default(self):
        """Restablece todos los parámetros a sus valores por defecto"""
        defaults = {
            'lookback_period': 60,
            'min_train_samples': 500,
            'retrain_frequency': 100,
            'prediction_threshold': 0.55,
            'use_price_features': True,
            'use_volume_features': True,
            'use_volatility_features': True,
            'use_pattern_features': True,
            'risk_per_trade': 0.02,
            'max_positions': 3,
            'use_dynamic_stops': True,
            'atr_multiplier': 2.0,
            'min_volatility': 0.0005,
            'max_volatility': 0.05,
            'min_volume_ratio': 0.5,
            'detect_regime': True,
            'regime_window': 50
        }
        
        for key, value in defaults.items():
            if key in self.params_vars:
                self.params_vars[key].set(value)
        
        messagebox.showinfo(
            "Éxito",
            "Parámetros restablecidos a valores por defecto"
        )
    
    def get_config_dict(self) -> Dict:
        """
        Obtiene la configuración actual como diccionario
        
        Returns:
            Diccionario con todos los parámetros
        """
        config = {}
        for key, var in self.params_vars.items():
            config[key] = var.get()
        return config
    
    def validate_parameters(self) -> Tuple[bool, str]:
        """
        Valida los parámetros actuales
        
        Returns:
            Tupla de (es_válido, mensaje_error)
        """
        try:
            # Validar lookback period
            if self.params_vars['lookback_period'].get() < 20:
                return False, "Lookback period debe ser al menos 20"
            
            # Validar min train samples
            if self.params_vars['min_train_samples'].get() < 200:
                return False, "Min train samples debe ser al menos 200"
            
            # Validar prediction threshold
            threshold = self.params_vars['prediction_threshold'].get()
            if threshold < 0.5 or threshold > 0.95:
                return False, "Prediction threshold debe estar entre 0.5 y 0.95"
            
            # Validar risk per trade
            risk = self.params_vars['risk_per_trade'].get()
            if risk <= 0 or risk > 0.2:
                return False, "Risk per trade debe estar entre 0.01 y 0.20"
            
            # Validar volatility range
            min_vol = self.params_vars['min_volatility'].get()
            max_vol = self.params_vars['max_volatility'].get()
            if min_vol >= max_vol:
                return False, "Min volatility debe ser menor que max volatility"
            
            return True, "Parámetros válidos"
            
        except Exception as e:
            return False, f"Error en validación: {str(e)}"


def integrate_ml_strategy_to_gui(parent_notebook: ttk.Notebook) -> MLStrategyGUIIntegration:
    """
    Integra la estrategia ML a un Notebook de tkinter
    
    Args:
        parent_notebook: Notebook de tkinter donde agregar la pestaña
        
    Returns:
        Instancia de MLStrategyGUIIntegration
    """
    # Crear frame para la estrategia ML
    ml_frame = ttk.Frame(parent_notebook)
    parent_notebook.add(ml_frame, text="🤖 ML Strategy")
    
    # Crear integración
    integration = MLStrategyGUIIntegration(ml_frame)
    
    return integration
