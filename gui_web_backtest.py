"""
Interfaz Web para Sistema de Backtesting usando Streamlit
Ejecutar con: streamlit run gui_web_backtest.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import MetaTrader5 as mt5
from datetime import datetime
import json

# Imports del proyecto
try:
    from config.settings import BacktestConfig
    from backtest_engine import BacktestEngine
    from strategies.two_bearish_pattern_strategy import TwoBearishPatternStrategy
    from reporting import ReportGenerator
except ImportError as e:
    st.error(f"Error importando módulos: {e}")
    st.stop()

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Backtesting",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #0d7377;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #0d7377;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
    .error-box {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Inicializa el estado de la sesión"""
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    if 'current_data' not in st.session_state:
        st.session_state.current_data = None
    if 'results' not in st.session_state:
        st.session_state.results = None
    if 'backtest_run' not in st.session_state:
        st.session_state.backtest_run = False


def load_mt5_data(symbol, timeframe_str, bars):
    """Carga datos desde MT5"""
    if not mt5.initialize():
        raise Exception("No se pudo inicializar MT5")
    
    try:
        timeframes = {
            'M1': mt5.TIMEFRAME_M1, 'M5': mt5.TIMEFRAME_M5,
            'M15': mt5.TIMEFRAME_M15, 'M30': mt5.TIMEFRAME_M30,
            'H1': mt5.TIMEFRAME_H1, 'H4': mt5.TIMEFRAME_H4,
            'D1': mt5.TIMEFRAME_D1, 'W1': mt5.TIMEFRAME_W1
        }
        
        timeframe = timeframes.get(timeframe_str, mt5.TIMEFRAME_H4)
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
        
        if rates is None or len(rates) == 0:
            raise Exception(f"No se obtuvieron datos para {symbol}")
        
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        
        return df
    finally:
        mt5.shutdown()


def run_backtest(strategy, data, config):
    """Ejecuta el backtest"""
    engine = BacktestEngine(config=config)
    results = engine.run(strategy=strategy, data=data)
    return results


def display_metrics(results):
    """Muestra las métricas principales"""
    metrics = results.metrics
    total_return = (results.final_capital / results.initial_capital) - 1
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Trades", metrics.get('total_trades', 0))
        st.metric("Win Rate", f"{metrics.get('win_rate', 0)*100:.1f}%")
    
    with col2:
        st.metric("Retorno Total", f"{total_return*100:.2f}%",
                 delta=f"${metrics.get('total_pnl', 0):,.2f}")
        st.metric("Profit Factor", f"{metrics.get('profit_factor', 0):.2f}")
    
    with col3:
        st.metric("Balance Final", f"${results.final_capital:,.2f}",
                 delta=f"${results.final_capital - results.initial_capital:,.2f}")
        st.metric("Sharpe Ratio", f"{metrics.get('sharpe_ratio', 0):.2f}")
    
    with col4:
        st.metric("Max Drawdown", f"{metrics.get('max_drawdown', 0)*100:.2f}%")
        st.metric("Expectancy", f"${metrics.get('expectancy', 0):.2f}")


def plot_equity_curve(results):
    """Crea gráfico de curva de equity"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=results.equity_curve.index,
        y=results.equity_curve.values,
        mode='lines',
        name='Equity',
        line=dict(color='#0d7377', width=2)
    ))
    
    fig.update_layout(
        title='Curva de Equity',
        xaxis_title='Tiempo',
        yaxis_title='Equity ($)',
        hovermode='x unified',
        template='plotly_white'
    )
    
    return fig


def plot_drawdown(results):
    """Crea gráfico de drawdown"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=results.drawdown_curve.index,
        y=results.drawdown_curve.values * 100,
        mode='lines',
        name='Drawdown',
        fill='tozeroy',
        line=dict(color='#dc3545', width=2)
    ))
    
    fig.update_layout(
        title='Drawdown',
        xaxis_title='Tiempo',
        yaxis_title='Drawdown (%)',
        hovermode='x unified',
        template='plotly_white'
    )
    
    return fig


def plot_trade_distribution(results):
    """Crea gráfico de distribución de trades"""
    trades_pnl = [trade.pnl for trade in results.trades]
    
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=trades_pnl,
        nbinsx=30,
        name='P&L Distribution',
        marker_color='#0d7377'
    ))
    
    fig.update_layout(
        title='Distribución de P&L por Trade',
        xaxis_title='P&L ($)',
        yaxis_title='Frecuencia',
        template='plotly_white'
    ))
    
    return fig


def display_trades_table(results):
    """Muestra tabla de trades"""
    if len(results.trades) == 0:
        st.warning("No hay trades para mostrar")
        return
    
    trades_data = []
    for trade in results.trades:
        trades_data.append({
            'Entry Time': trade.entry_time.strftime('%Y-%m-%d %H:%M'),
            'Exit Time': trade.exit_time.strftime('%Y-%m-%d %H:%M'),
            'Type': trade.trade_type,
            'Entry Price': f"{trade.entry_price:.5f}",
            'Exit Price': f"{trade.exit_price:.5f}",
            'P&L': f"${trade.pnl:.2f}",
            'P&L %': f"{trade.pnl_pct*100:.2f}%",
            'Exit Reason': trade.exit_reason
        })
    
    df_trades = pd.DataFrame(trades_data)
    st.dataframe(df_trades, use_container_width=True)


def main():
    """Función principal"""
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">📈 Sistema de Backtesting de Estrategias</h1>', 
                unsafe_allow_html=True)
    
    # Sidebar - Configuración
    with st.sidebar:
        st.header("⚙️ Configuración")
        
        # === SECCIÓN DE DATOS ===
        st.subheader("📊 Datos")
        
        data_source = st.selectbox(
            "Fuente de Datos",
            ["MetaTrader 5", "Archivo CSV"]
        )
        
        if data_source == "MetaTrader 5":
            symbol = st.text_input("Símbolo", value="EURUSD")
            timeframe = st.selectbox(
                "Timeframe",
                ["M1", "M5", "M15", "M30", "H1", "H4", "D1", "W1"],
                index=5  # H4 por defecto
            )
            bars = st.number_input("Número de Barras", min_value=100, max_value=10000, 
                                  value=1000, step=100)
            
            if st.button("🔄 Cargar Datos"):
                with st.spinner("Cargando datos desde MT5..."):
                    try:
                        data = load_mt5_data(symbol, timeframe, bars)
                        st.session_state.current_data = data
                        st.session_state.data_loaded = True
                        st.success(f"✅ {len(data)} barras cargadas")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
        else:
            uploaded_file = st.file_uploader("Subir archivo CSV", type=['csv'])
            if uploaded_file is not None:
                try:
                    data = pd.read_csv(uploaded_file)
                    if 'time' in data.columns:
                        data['time'] = pd.to_datetime(data['time'])
                        data.set_index('time', inplace=True)
                    st.session_state.current_data = data
                    st.session_state.data_loaded = True
                    st.success(f"✅ {len(data)} barras cargadas")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        st.divider()
        
        # === CONFIGURACIÓN DE BACKTEST ===
        st.subheader("💰 Backtest")
        
        initial_capital = st.number_input(
            "Capital Inicial ($)",
            min_value=1000.0,
            max_value=1000000.0,
            value=10000.0,
            step=1000.0
        )
        
        commission_pct = st.number_input(
            "Comisión (%)",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            step=0.01
        )
        
        slippage_pct = st.number_input(
            "Slippage (%)",
            min_value=0.0,
            max_value=5.0,
            value=1.0,
            step=0.1
        )
        
        use_spread = st.checkbox("Usar Spread", value=False)
        
        st.divider()
        
        # === SELECCIÓN DE ESTRATEGIA ===
        st.subheader("🎯 Estrategia")
        
        strategy_name = st.selectbox(
            "Seleccionar Estrategia",
            ["Two Bearish Pattern"]
        )
        
        if strategy_name == "Two Bearish Pattern":
            st.write("**Parámetros:**")
            
            risk_reward = st.slider(
                "Risk/Reward Ratio",
                min_value=1.0,
                max_value=5.0,
                value=2.0,
                step=0.5
            )
            
            risk_per_trade = st.slider(
                "Risk per Trade (%)",
                min_value=0.5,
                max_value=5.0,
                value=2.0,
                step=0.5
            )
            
            min_body_ratio = st.slider(
                "Min Body Ratio",
                min_value=0.5,
                max_value=2.0,
                value=1.0,
                step=0.1
            )
            
            use_trailing = st.checkbox("Usar Trailing Stop", value=False)
    
    # Main Content
    if not st.session_state.data_loaded:
        st.info("👈 Por favor, carga los datos desde el panel lateral")
        
        # Mostrar información de ejemplo
        st.subheader("📚 Cómo usar esta aplicación")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            ### 1️⃣ Cargar Datos
            - Selecciona la fuente (MT5 o CSV)
            - Configura los parámetros
            - Haz clic en "Cargar Datos"
            """)
        
        with col2:
            st.markdown("""
            ### 2️⃣ Configurar
            - Ajusta el capital inicial
            - Configura comisiones y slippage
            - Selecciona y configura estrategia
            """)
        
        with col3:
            st.markdown("""
            ### 3️⃣ Ejecutar
            - Haz clic en "Ejecutar Backtest"
            - Revisa los resultados
            - Analiza los gráficos
            """)
        
        return
    
    # Mostrar información de datos cargados
    st.success(f"✅ Datos cargados: {len(st.session_state.current_data)} barras")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write(f"**Periodo:** {st.session_state.current_data.index[0]} a {st.session_state.current_data.index[-1]}")
    
    with col2:
        if st.button("🚀 Ejecutar Backtest", type="primary", use_container_width=True):
            with st.spinner("Ejecutando backtest..."):
                try:
                    # Crear configuración
                    config = BacktestConfig(
                        initial_capital=initial_capital,
                        commission_pct=commission_pct / 100,
                        slippage_pct=slippage_pct / 100,
                        use_spread=use_spread
                    )
                    
                    # Crear estrategia
                    if strategy_name == "Two Bearish Pattern":
                        strategy = TwoBearishPatternStrategy(
                            risk_reward_ratio=risk_reward,
                            risk_per_trade=risk_per_trade / 100,
                            min_body_ratio=min_body_ratio,
                            use_trailing_stop=use_trailing
                        )
                    
                    # Ejecutar backtest
                    results = run_backtest(strategy, st.session_state.current_data, config)
                    st.session_state.results = results
                    st.session_state.backtest_run = True
                    
                    st.success("✅ Backtest completado!")
                    
                except Exception as e:
                    st.error(f"❌ Error durante el backtest: {str(e)}")
                    return
    
    # Mostrar resultados si existen
    if st.session_state.backtest_run and st.session_state.results is not None:
        st.divider()
        
        # Tabs para organizar resultados
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Resumen", "📈 Gráficos", "📋 Trades", "💾 Exportar"])
        
        with tab1:
            st.subheader("Métricas Principales")
            display_metrics(st.session_state.results)
            
            st.divider()
            
            # Métricas detalladas
            st.subheader("Métricas Detalladas")
            
            metrics = st.session_state.results.metrics
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write("**Operaciones:**")
                st.write(f"- Total: {metrics.get('total_trades', 0)}")
                st.write(f"- Ganadoras: {metrics.get('winning_trades', 0)}")
                st.write(f"- Perdedoras: {metrics.get('losing_trades', 0)}")
                st.write(f"- Win Rate: {metrics.get('win_rate', 0)*100:.1f}%")
            
            with col2:
                st.write("**P&L:**")
                st.write(f"- Total: ${metrics.get('total_pnl', 0):,.2f}")
                st.write(f"- Ganancia Promedio: ${metrics.get('avg_win', 0):,.2f}")
                st.write(f"- Pérdida Promedio: ${metrics.get('avg_loss', 0):,.2f}")
                st.write(f"- Expectancy: ${metrics.get('expectancy', 0):,.2f}")
            
            with col3:
                st.write("**Riesgo:**")
                st.write(f"- Max Drawdown: {metrics.get('max_drawdown', 0)*100:.2f}%")
                st.write(f"- Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}")
                st.write(f"- Recovery Factor: {metrics.get('recovery_factor', 0):.2f}")
                st.write(f"- Calmar Ratio: {metrics.get('calmar_ratio', 0):.2f}")
        
        with tab2:
            st.subheader("Curva de Equity")
            st.plotly_chart(plot_equity_curve(st.session_state.results), 
                          use_container_width=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Drawdown")
                st.plotly_chart(plot_drawdown(st.session_state.results), 
                              use_container_width=True)
            
            with col2:
                st.subheader("Distribución de P&L")
                st.plotly_chart(plot_trade_distribution(st.session_state.results), 
                              use_container_width=True)
        
        with tab3:
            st.subheader("Historial de Trades")
            display_trades_table(st.session_state.results)
        
        with tab4:
            st.subheader("Exportar Resultados")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Exportar métricas JSON
                if st.button("📄 Descargar Métricas (JSON)", use_container_width=True):
                    metrics_data = {
                        'timestamp': datetime.now().isoformat(),
                        'strategy': strategy_name,
                        'metrics': st.session_state.results.metrics,
                        'initial_capital': st.session_state.results.initial_capital,
                        'final_capital': st.session_state.results.final_capital,
                        'total_trades': len(st.session_state.results.trades)
                    }
                    
                    st.download_button(
                        label="Descargar",
                        data=json.dumps(metrics_data, indent=2, default=str),
                        file_name=f"backtest_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
            
            with col2:
                # Exportar trades CSV
                if st.button("📊 Descargar Trades (CSV)", use_container_width=True):
                    trades_data = []
                    for trade in st.session_state.results.trades:
                        trades_data.append({
                            'entry_time': trade.entry_time,
                            'exit_time': trade.exit_time,
                            'type': trade.trade_type,
                            'entry_price': trade.entry_price,
                            'exit_price': trade.exit_price,
                            'pnl': trade.pnl,
                            'pnl_pct': trade.pnl_pct,
                            'exit_reason': trade.exit_reason
                        })
                    
                    df_trades = pd.DataFrame(trades_data)
                    csv = df_trades.to_csv(index=False)
                    
                    st.download_button(
                        label="Descargar",
                        data=csv,
                        file_name=f"trades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )


if __name__ == "__main__":
    main()