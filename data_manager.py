"""
Gestor de Datos para MetaTrader 5
Maneja la conexión, descarga y procesamiento de datos históricos
"""
import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Tuple
import logging
from config.settings import MT5Config, TIMEFRAMES

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MT5DataManager:
    """
    Administrador de datos de MetaTrader 5
    
    Gestiona conexión, descarga de datos históricos, validación de símbolos
    y procesamiento de datos OHLC y ticks.
    """
    
    def __init__(self, config: Optional[MT5Config] = None):
        """
        Inicializa el gestor de datos MT5
        
        Args:
            config: Configuración de conexión MT5
        """
        self.config = config or MT5Config()
        self.connected = False
        self.available_symbols = []
        
    def connect(self) -> bool:
        """
        Conecta con MetaTrader 5
        
        Returns:
            True si la conexión fue exitosa, False en caso contrario
        """
        try:
            # Intentar inicializar MT5
            if self.config.path:
                initialized = mt5.initialize(
                    path=self.config.path,
                    timeout=self.config.timeout,
                    portable=self.config.portable
                )
            else:
                initialized = mt5.initialize(
                    timeout=self.config.timeout,
                    portable=self.config.portable
                )
            
            if not initialized:
                logger.error(f"MT5 initialization failed: {mt5.last_error()}")
                return False
            
            # Login si se proporcionan credenciales
            if all([self.config.login, self.config.password, self.config.server]):
                authorized = mt5.login(
                    login=self.config.login,
                    password=self.config.password,
                    server=self.config.server
                )
                
                if not authorized:
                    logger.error(f"MT5 login failed: {mt5.last_error()}")
                    mt5.shutdown()
                    return False
            
            self.connected = True
            
            # Cargar símbolos disponibles
            self._load_available_symbols()
            
            # Información de la terminal
            terminal_info = mt5.terminal_info()
            account_info = mt5.account_info()
            
            if terminal_info and account_info:
                logger.info(f"Connected to MT5 Terminal: {terminal_info.name}")
                logger.info(f"Account: {account_info.login} | Server: {account_info.server}")
                logger.info(f"Balance: {account_info.balance} {account_info.currency}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to MT5: {e}")
            return False
    
    def disconnect(self) -> None:
        """Desconecta de MetaTrader 5"""
        if self.connected:
            mt5.shutdown()
            self.connected = False
            logger.info("Disconnected from MT5")
    
    def _load_available_symbols(self) -> None:
        """Carga la lista de símbolos disponibles"""
        try:
            symbols = mt5.symbols_get()
            if symbols:
                self.available_symbols = [s.name for s in symbols]
                logger.info(f"Loaded {len(self.available_symbols)} available symbols")
        except Exception as e:
            logger.error(f"Error loading symbols: {e}")
            self.available_symbols = []
    
    def validate_symbol(self, symbol: str) -> bool:
        """
        Valida si un símbolo está disponible
        
        Args:
            symbol: Nombre del símbolo
            
        Returns:
            True si el símbolo está disponible
        """
        if not self.connected:
            logger.error("Not connected to MT5")
            return False
        
        # Intentar obtener información del símbolo
        symbol_info = mt5.symbol_info(symbol)
        
        if symbol_info is None:
            logger.warning(f"Symbol {symbol} not found")
            return False
        
        # Verificar si el símbolo está visible
        if not symbol_info.visible:
            logger.info(f"Symbol {symbol} is not visible, attempting to show it")
            if not mt5.symbol_select(symbol, True):
                logger.error(f"Failed to select symbol {symbol}")
                return False
        
        logger.info(f"Symbol {symbol} validated successfully")
        return True
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict]:
        """
        Obtiene información detallada de un símbolo
        
        Args:
            symbol: Nombre del símbolo
            
        Returns:
            Diccionario con información del símbolo o None
        """
        if not self.validate_symbol(symbol):
            return None
        
        symbol_info = mt5.symbol_info(symbol)
        
        return {
            'name': symbol_info.name,
            'description': symbol_info.description,
            'point': symbol_info.point,
            'digits': symbol_info.digits,
            'spread': symbol_info.spread,
            'trade_contract_size': symbol_info.trade_contract_size,
            'trade_tick_size': symbol_info.trade_tick_size,
            'trade_tick_value': symbol_info.trade_tick_value,
            'volume_min': symbol_info.volume_min,
            'volume_max': symbol_info.volume_max,
            'volume_step': symbol_info.volume_step,
            'currency_base': symbol_info.currency_base,
            'currency_profit': symbol_info.currency_profit,
            'currency_margin': symbol_info.currency_margin,
            'bid': symbol_info.bid,
            'ask': symbol_info.ask,
            'last': symbol_info.last,
            'time': datetime.fromtimestamp(symbol_info.time)
        }
    
    def get_historical_data(
        self,
        symbol: str,
        timeframe: str,
        start_date: datetime,
        end_date: Optional[datetime] = None,
        count: Optional[int] = None
    ) -> Optional[pd.DataFrame]:
        """
        Descarga datos históricos OHLC
        
        Args:
            symbol: Símbolo a descargar
            timeframe: Timeframe (ej: 'H1', 'D1', 'M15')
            start_date: Fecha de inicio
            end_date: Fecha de fin (opcional si se usa count)
            count: Número de barras (opcional si se usa end_date)
            
        Returns:
            DataFrame con datos OHLC o None
        """
        if not self.connected:
            logger.error("Not connected to MT5")
            return None
        
        if not self.validate_symbol(symbol):
            return None
        
        # Convertir timeframe a constante MT5
        tf = self._get_mt5_timeframe(timeframe)
        if tf is None:
            logger.error(f"Invalid timeframe: {timeframe}")
            return None
        
        try:
            # Descargar datos
            if end_date:
                rates = mt5.copy_rates_range(symbol, tf, start_date, end_date)
            elif count:
                rates = mt5.copy_rates_from(symbol, tf, start_date, count)
            else:
                logger.error("Must provide either end_date or count")
                return None
            
            if rates is None or len(rates) == 0:
                logger.error(f"No data retrieved for {symbol}")
                return None
            
            # Convertir a DataFrame
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df.set_index('time', inplace=True)
            
            # Renombrar columnas
            df.columns = ['open', 'high', 'low', 'close', 'tick_volume', 'spread', 'real_volume']
            
            # Validar calidad de datos
            if not self._validate_data_quality(df, symbol, timeframe):
                logger.warning(f"Data quality issues detected for {symbol}")
            
            logger.info(f"Downloaded {len(df)} bars for {symbol} ({timeframe})")
            return df
            
        except Exception as e:
            logger.error(f"Error downloading data: {e}")
            return None
    
    def get_tick_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: Optional[datetime] = None,
        count: Optional[int] = None
    ) -> Optional[pd.DataFrame]:
        """
        Descarga datos de ticks
        
        Args:
            symbol: Símbolo a descargar
            start_date: Fecha de inicio
            end_date: Fecha de fin (opcional si se usa count)
            count: Número de ticks (opcional si se usa end_date)
            
        Returns:
            DataFrame con datos de ticks o None
        """
        if not self.connected:
            logger.error("Not connected to MT5")
            return None
        
        if not self.validate_symbol(symbol):
            return None
        
        try:
            # Descargar ticks
            if end_date:
                ticks = mt5.copy_ticks_range(symbol, start_date, end_date, mt5.COPY_TICKS_ALL)
            elif count:
                ticks = mt5.copy_ticks_from(symbol, start_date, count, mt5.COPY_TICKS_ALL)
            else:
                logger.error("Must provide either end_date or count")
                return None
            
            if ticks is None or len(ticks) == 0:
                logger.error(f"No tick data retrieved for {symbol}")
                return None
            
            # Convertir a DataFrame
            df = pd.DataFrame(ticks)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df['time_msc'] = pd.to_datetime(df['time_msc'], unit='ms')
            df.set_index('time_msc', inplace=True)
            
            logger.info(f"Downloaded {len(df)} ticks for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Error downloading tick data: {e}")
            return None
    
    def _get_mt5_timeframe(self, timeframe: str) -> Optional[int]:
        """
        Convierte string de timeframe a constante MT5
        
        Args:
            timeframe: String del timeframe (ej: 'H1', 'D1')
            
        Returns:
            Constante MT5 del timeframe o None
        """
        timeframe_map = {
            'M1': mt5.TIMEFRAME_M1,
            'M2': mt5.TIMEFRAME_M2,
            'M3': mt5.TIMEFRAME_M3,
            'M4': mt5.TIMEFRAME_M4,
            'M5': mt5.TIMEFRAME_M5,
            'M6': mt5.TIMEFRAME_M6,
            'M10': mt5.TIMEFRAME_M10,
            'M12': mt5.TIMEFRAME_M12,
            'M15': mt5.TIMEFRAME_M15,
            'M20': mt5.TIMEFRAME_M20,
            'M30': mt5.TIMEFRAME_M30,
            'H1': mt5.TIMEFRAME_H1,
            'H2': mt5.TIMEFRAME_H2,
            'H3': mt5.TIMEFRAME_H3,
            'H4': mt5.TIMEFRAME_H4,
            'H6': mt5.TIMEFRAME_H6,
            'H8': mt5.TIMEFRAME_H8,
            'H12': mt5.TIMEFRAME_H12,
            'D1': mt5.TIMEFRAME_D1,
            'W1': mt5.TIMEFRAME_W1,
            'MN1': mt5.TIMEFRAME_MN1,
        }
        return timeframe_map.get(timeframe)
    
    def _validate_data_quality(self, df: pd.DataFrame, symbol: str, timeframe: str) -> bool:
        """
        Valida la calidad de los datos descargados
        
        Args:
            df: DataFrame con datos
            symbol: Símbolo
            timeframe: Timeframe
            
        Returns:
            True si los datos son de buena calidad
        """
        issues = []
        
        # Verificar datos nulos
        null_counts = df.isnull().sum()
        if null_counts.any():
            issues.append(f"Null values found: {null_counts[null_counts > 0].to_dict()}")
        
        # Verificar duplicados
        duplicates = df.index.duplicated().sum()
        if duplicates > 0:
            issues.append(f"Found {duplicates} duplicate timestamps")
        
        # Verificar OHLC lógicos
        invalid_ohlc = ((df['high'] < df['low']) | 
                        (df['high'] < df['open']) | 
                        (df['high'] < df['close']) |
                        (df['low'] > df['open']) | 
                        (df['low'] > df['close'])).sum()
        
        if invalid_ohlc > 0:
            issues.append(f"Found {invalid_ohlc} bars with invalid OHLC relationships")
        
        # Verificar gaps en tiempo
        if len(df) > 1:
            time_diffs = df.index.to_series().diff()
            expected_diff = self._get_expected_time_diff(timeframe)
            large_gaps = (time_diffs > expected_diff * 3).sum()  # Gaps > 3x esperado
            
            if large_gaps > 0:
                issues.append(f"Found {large_gaps} large time gaps")
        
        # Reportar problemas
        if issues:
            for issue in issues:
                logger.warning(f"{symbol} quality check: {issue}")
            return False
        
        return True
    
    def _get_expected_time_diff(self, timeframe: str) -> timedelta:
        """
        Obtiene la diferencia de tiempo esperada para un timeframe
        
        Args:
            timeframe: String del timeframe
            
        Returns:
            timedelta esperado entre barras
        """
        minutes = TIMEFRAMES.get(timeframe, 60)
        return timedelta(minutes=minutes)
    
    def resample_data(
        self,
        df: pd.DataFrame,
        target_timeframe: str,
        source_timeframe: str
    ) -> pd.DataFrame:
        """
        Resamplea datos a un timeframe diferente
        
        Args:
            df: DataFrame con datos originales
            target_timeframe: Timeframe objetivo
            source_timeframe: Timeframe original
            
        Returns:
            DataFrame resampleado
        """
        # Calcular el factor de resampleo
        target_minutes = TIMEFRAMES.get(target_timeframe)
        source_minutes = TIMEFRAMES.get(source_timeframe)
        
        if not target_minutes or not source_minutes:
            logger.error("Invalid timeframe for resampling")
            return df
        
        if target_minutes < source_minutes:
            logger.error("Cannot resample to smaller timeframe")
            return df
        
        # Resamplear
        rule = f'{target_minutes}T'
        
        resampled = df.resample(rule).agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'tick_volume': 'sum',
            'real_volume': 'sum'
        })
        
        # Eliminar filas con NaN
        resampled.dropna(inplace=True)
        
        logger.info(f"Resampled from {source_timeframe} to {target_timeframe}: {len(df)} -> {len(resampled)} bars")
        
        return resampled
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
