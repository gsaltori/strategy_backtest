"""
Módulo de reportes y visualizaciones
Genera gráficos interactivos y reportes PDF
"""
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from typing import Dict, List, Optional
import logging
from backtest_engine import BacktestResult
from analysis.performance import PerformanceAnalyzer

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Generador de reportes y visualizaciones para backtesting
    """
    
    def __init__(self, result: BacktestResult):
        """
        Inicializa el generador de reportes
        
        Args:
            result: Resultado del backtesting
        """
        self.result = result
        self.analyzer = PerformanceAnalyzer(
            result.trades,
            result.equity_curve,
            result.initial_capital
        )
    
    def create_full_report(self, filename: Optional[str] = None) -> go.Figure:
        """
        Crea un reporte visual completo
        
        Args:
            filename: Nombre del archivo para guardar (opcional)
            
        Returns:
            Figura de Plotly
        """
        # Crear subplots
        fig = make_subplots(
            rows=4, cols=2,
            subplot_titles=(
                'Price & Signals',
                'Equity Curve',
                'Drawdown',
                'Trade P&L Distribution',
                'Cumulative Returns',
                'Monthly Returns',
                'Win/Loss Analysis',
                'Trade Duration'
            ),
            specs=[
                [{'secondary_y': True}, {'type': 'scatter'}],
                [{'type': 'scatter'}, {'type': 'histogram'}],
                [{'type': 'bar'}, {'type': 'bar'}],
                [{'type': 'box'}, {'type': 'histogram'}]
            ],
            vertical_spacing=0.08,
            horizontal_spacing=0.1
        )
        
        # 1. Price & Signals
        self._add_price_signals_plot(fig, row=1, col=1)
        
        # 2. Equity Curve
        self._add_equity_curve_plot(fig, row=1, col=2)
        
        # 3. Drawdown
        self._add_drawdown_plot(fig, row=2, col=1)
        
        # 4. Trade P&L Distribution
        self._add_pnl_distribution_plot(fig, row=2, col=2)
        
        # 5. Cumulative Returns
        self._add_cumulative_returns_plot(fig, row=3, col=1)
        
        # 6. Monthly Returns
        self._add_monthly_returns_plot(fig, row=3, col=2)
        
        # 7. Win/Loss Analysis
        self._add_win_loss_analysis_plot(fig, row=4, col=1)
        
        # 8. Trade Duration
        self._add_duration_analysis_plot(fig, row=4, col=2)
        
        # Update layout
        fig.update_layout(
            height=1800,
            width=1600,
            showlegend=True,
            title_text=f"Backtest Report - {self.result.metrics.get('total_trades', 0)} Trades",
            title_font_size=20
        )
        
        if filename:
            fig.write_html(filename)
            logger.info(f"Report saved to {filename}")
        
        return fig
    
    def _add_price_signals_plot(self, fig: go.Figure, row: int, col: int) -> None:
        """Añade gráfico de precio con señales"""
        data = self.result.data_with_signals
        
        # Candlestick
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data['open'],
                high=data['high'],
                low=data['low'],
                close=data['close'],
                name='Price',
                increasing_line_color='green',
                decreasing_line_color='red'
            ),
            row=row, col=col, secondary_y=False
        )
        
        # Señales de compra
        buy_signals = data[data['signal'] == 1]
        fig.add_trace(
            go.Scatter(
                x=buy_signals.index,
                y=buy_signals['low'] * 0.995,
                mode='markers',
                marker=dict(symbol='triangle-up', size=12, color='lime'),
                name='Buy Signal'
            ),
            row=row, col=col, secondary_y=False
        )
        
        # Señales de venta
        sell_signals = data[data['signal'] == -1]
        fig.add_trace(
            go.Scatter(
                x=sell_signals.index,
                y=sell_signals['high'] * 1.005,
                mode='markers',
                marker=dict(symbol='triangle-down', size=12, color='red'),
                name='Sell Signal'
            ),
            row=row, col=col, secondary_y=False
        )
        
        # Indicadores si están disponibles
        if 'fast_ma' in data.columns:
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['fast_ma'],
                    mode='lines',
                    name='Fast MA',
                    line=dict(color='blue', width=1)
                ),
                row=row, col=col, secondary_y=False
            )
        
        if 'slow_ma' in data.columns:
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['slow_ma'],
                    mode='lines',
                    name='Slow MA',
                    line=dict(color='orange', width=1)
                ),
                row=row, col=col, secondary_y=False
            )
        
        # RSI en eje secundario
        if 'rsi' in data.columns:
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['rsi'],
                    mode='lines',
                    name='RSI',
                    line=dict(color='purple', width=1, dash='dot')
                ),
                row=row, col=col, secondary_y=True
            )
            
            # Líneas de sobrecompra/sobreventa
            fig.add_hline(y=70, line_dash="dash", line_color="red", 
                         row=row, col=col, secondary_y=True)
            fig.add_hline(y=30, line_dash="dash", line_color="green", 
                         row=row, col=col, secondary_y=True)
    
    def _add_equity_curve_plot(self, fig: go.Figure, row: int, col: int) -> None:
        """Añade gráfico de equity curve"""
        fig.add_trace(
            go.Scatter(
                x=self.result.equity_curve.index,
                y=self.result.equity_curve.values,
                mode='lines',
                name='Equity',
                line=dict(color='blue', width=2),
                fill='tozeroy',
                fillcolor='rgba(0, 100, 255, 0.1)'
            ),
            row=row, col=col
        )
        
        # Línea de capital inicial
        fig.add_hline(
            y=self.result.initial_capital,
            line_dash="dash",
            line_color="gray",
            annotation_text="Initial Capital",
            row=row, col=col
        )
    
    def _add_drawdown_plot(self, fig: go.Figure, row: int, col: int) -> None:
        """Añade gráfico de drawdown"""
        fig.add_trace(
            go.Scatter(
                x=self.result.drawdown_curve.index,
                y=self.result.drawdown_curve.values * 100,
                mode='lines',
                name='Drawdown %',
                line=dict(color='red', width=2),
                fill='tozeroy',
                fillcolor='rgba(255, 0, 0, 0.2)'
            ),
            row=row, col=col
        )
    
    def _add_pnl_distribution_plot(self, fig: go.Figure, row: int, col: int) -> None:
        """Añade histograma de distribución de P&L"""
        pnls = [t.pnl for t in self.result.trades]
        
        fig.add_trace(
            go.Histogram(
                x=pnls,
                nbinsx=30,
                name='P&L Distribution',
                marker_color='lightblue',
                marker_line_color='darkblue',
                marker_line_width=1
            ),
            row=row, col=col
        )
        
        # Línea vertical en 0
        fig.add_vline(x=0, line_dash="dash", line_color="red", row=row, col=col)
    
    def _add_cumulative_returns_plot(self, fig: go.Figure, row: int, col: int) -> None:
        """Añade gráfico de retornos acumulados"""
        returns = self.result.equity_curve.pct_change().fillna(0)
        cumulative_returns = (1 + returns).cumprod() - 1
        
        fig.add_trace(
            go.Scatter(
                x=cumulative_returns.index,
                y=cumulative_returns.values * 100,
                mode='lines',
                name='Cumulative Returns %',
                line=dict(color='green', width=2)
            ),
            row=row, col=col
        )
    
    def _add_monthly_returns_plot(self, fig: go.Figure, row: int, col: int) -> None:
        """Añade gráfico de retornos mensuales"""
        monthly_returns = self.result.equity_curve.resample('ME').last().pct_change().dropna()
        
        colors = ['green' if r > 0 else 'red' for r in monthly_returns.values]
        
        fig.add_trace(
            go.Bar(
                x=monthly_returns.index,
                y=monthly_returns.values * 100,
                name='Monthly Returns %',
                marker_color=colors
            ),
            row=row, col=col
        )
    
    def _add_win_loss_analysis_plot(self, fig: go.Figure, row: int, col: int) -> None:
        """Añade gráfico de análisis win/loss"""
        wins = [t.pnl for t in self.result.trades if t.pnl > 0]
        losses = [t.pnl for t in self.result.trades if t.pnl <= 0]
        
        fig.add_trace(
            go.Box(
                y=wins,
                name='Wins',
                marker_color='green',
                boxmean='sd'
            ),
            row=row, col=col
        )
        
        fig.add_trace(
            go.Box(
                y=losses,
                name='Losses',
                marker_color='red',
                boxmean='sd'
            ),
            row=row, col=col
        )
    
    def _add_duration_analysis_plot(self, fig: go.Figure, row: int, col: int) -> None:
        """Añade histograma de duración de trades"""
        durations = [t.duration_bars for t in self.result.trades]
        
        fig.add_trace(
            go.Histogram(
                x=durations,
                nbinsx=20,
                name='Trade Duration (bars)',
                marker_color='lightgreen',
                marker_line_color='darkgreen',
                marker_line_width=1
            ),
            row=row, col=col
        )
    
    def create_metrics_table(self) -> pd.DataFrame:
        """
        Crea una tabla con todas las métricas
        
        Returns:
            DataFrame con métricas
        """
        # Métricas básicas
        basic_metrics = {
            'Initial Capital': f"${self.result.initial_capital:,.2f}",
            'Final Capital': f"${self.result.final_capital:,.2f}",
            'Net P&L': f"${self.result.final_capital - self.result.initial_capital:,.2f}",
            'Return %': f"{((self.result.final_capital/self.result.initial_capital - 1) * 100):.2f}%",
            'Total Trades': self.result.metrics.get('total_trades', 0),
            'Winning Trades': self.result.metrics.get('winning_trades', 0),
            'Losing Trades': self.result.metrics.get('losing_trades', 0),
            'Win Rate': f"{self.result.metrics.get('win_rate', 0):.2%}",
        }
        
        # Métricas de riesgo
        risk_metrics = {
            'Profit Factor': f"{self.result.metrics.get('profit_factor', 0):.2f}",
            'Sharpe Ratio': f"{self.result.metrics.get('sharpe_ratio', 0):.2f}",
            'Max Drawdown': f"{self.result.metrics.get('max_drawdown', 0):.2%}",
            'Recovery Factor': f"{self.result.metrics.get('recovery_factor', 0):.2f}",
            'Calmar Ratio': f"{self.result.metrics.get('calmar_ratio', 0):.2f}",
        }
        
        # Métricas de trades
        trade_metrics = {
            'Average Win': f"${self.result.metrics.get('avg_win', 0):.2f}",
            'Average Loss': f"${self.result.metrics.get('avg_loss', 0):.2f}",
            'Expectancy': f"${self.result.metrics.get('expectancy', 0):.2f}",
            'Avg Risk/Reward': f"{self.result.metrics.get('avg_risk_reward', 0):.2f}",
            'Avg MAE': f"{self.result.metrics.get('avg_mae', 0):.2%}",
            'Avg MFE': f"{self.result.metrics.get('avg_mfe', 0):.2%}",
        }
        
        # Métricas avanzadas
        advanced_metrics = self.analyzer.calculate_advanced_metrics()
        advanced_formatted = {
            'Sortino Ratio': f"{advanced_metrics.get('sortino_ratio', 0):.2f}",
            'Omega Ratio': f"{advanced_metrics.get('omega_ratio', 0):.2f}",
            'Kelly Criterion': f"{advanced_metrics.get('kelly_criterion', 0):.2%}",
            'Max Consecutive Wins': advanced_metrics.get('max_consecutive_wins', 0),
            'Max Consecutive Losses': advanced_metrics.get('max_consecutive_losses', 0),
        }
        
        # Combinar todas las métricas
        all_metrics = {**basic_metrics, **risk_metrics, **trade_metrics, **advanced_formatted}
        
        df = pd.DataFrame(list(all_metrics.items()), columns=['Metric', 'Value'])
        
        return df
    
    def create_trades_dataframe(self) -> pd.DataFrame:
        """
        Crea un DataFrame con información de todos los trades
        
        Returns:
            DataFrame con trades
        """
        if not self.result.trades:
            return pd.DataFrame()
        
        trades_data = []
        for i, trade in enumerate(self.result.trades, 1):
            trades_data.append({
                'Trade #': i,
                'Entry Time': trade.entry_time,
                'Exit Time': trade.exit_time,
                'Type': trade.trade_type,
                'Entry Price': trade.entry_price,
                'Exit Price': trade.exit_price,
                'Size': trade.size,
                'P&L': trade.pnl,
                'P&L %': trade.pnl_pct * 100,
                'Exit Reason': trade.exit_reason,
                'Duration (bars)': trade.duration_bars,
                'MAE %': trade.mae * 100,
                'MFE %': trade.mfe * 100,
                'Commission': trade.commission,
                'Slippage': trade.slippage,
            })
        
        df = pd.DataFrame(trades_data)
        return df
    
    def generate_summary_text(self) -> str:
        """
        Genera un resumen textual del backtest
        
        Returns:
            String con resumen
        """
        metrics = self.result.metrics
        advanced = self.analyzer.calculate_advanced_metrics()
        
        summary = f"""
{'='*80}
BACKTEST SUMMARY REPORT
{'='*80}

CAPITAL PERFORMANCE
-------------------
Initial Capital:        ${self.result.initial_capital:,.2f}
Final Capital:          ${self.result.final_capital:,.2f}
Net P&L:                ${self.result.final_capital - self.result.initial_capital:,.2f}
Total Return:           {((self.result.final_capital/self.result.initial_capital - 1) * 100):.2f}%

TRADE STATISTICS
----------------
Total Trades:           {metrics.get('total_trades', 0)}
Winning Trades:         {metrics.get('winning_trades', 0)}
Losing Trades:          {metrics.get('losing_trades', 0)}
Win Rate:               {metrics.get('win_rate', 0):.2%}

Gross Profit:           ${metrics.get('gross_profit', 0):,.2f}
Gross Loss:             ${metrics.get('gross_loss', 0):,.2f}
Average Win:            ${metrics.get('avg_win', 0):.2f}
Average Loss:           ${metrics.get('avg_loss', 0):.2f}

RISK METRICS
------------
Profit Factor:          {metrics.get('profit_factor', 0):.2f}
Expectancy:             ${metrics.get('expectancy', 0):.2f}
Avg Risk/Reward:        {metrics.get('avg_risk_reward', 0):.2f}

Sharpe Ratio:           {metrics.get('sharpe_ratio', 0):.2f}
Sortino Ratio:          {advanced.get('sortino_ratio', 0):.2f}
Omega Ratio:            {advanced.get('omega_ratio', 0):.2f}
Calmar Ratio:           {metrics.get('calmar_ratio', 0):.2f}

DRAWDOWN ANALYSIS
-----------------
Maximum Drawdown:       {metrics.get('max_drawdown', 0):.2%}
Recovery Factor:        {metrics.get('recovery_factor', 0):.2f}
Ulcer Index:            {advanced.get('ulcer_index', 0):.2f}

EXECUTION QUALITY
-----------------
Average MAE:            {metrics.get('avg_mae', 0):.2%}
Average MFE:            {metrics.get('avg_mfe', 0):.2%}
Total Commission:       ${metrics.get('total_commission', 0):.2f}
Total Slippage:         ${metrics.get('total_slippage', 0):.2f}

ADVANCED METRICS
----------------
Kelly Criterion:        {advanced.get('kelly_criterion', 0):.2%}
Tail Ratio:             {advanced.get('tail_ratio', 0):.2f}
Max Consecutive Wins:   {advanced.get('max_consecutive_wins', 0)}
Max Consecutive Losses: {advanced.get('max_consecutive_losses', 0)}

{'='*80}
"""
        return summary
    
    def save_report_html(self, filename: str = 'backtest_report.html') -> None:
        """
        Guarda un reporte HTML completo
        
        Args:
            filename: Nombre del archivo
        """
        # Crear gráfico principal
        fig = self.create_full_report()
        
        # Crear tabla de métricas
        metrics_df = self.create_metrics_table()
        metrics_html = metrics_df.to_html(index=False, classes='table table-striped')
        
        # Crear tabla de trades
        trades_df = self.create_trades_dataframe()
        trades_html = trades_df.to_html(index=False, classes='table table-striped')
        
        # HTML completo
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Backtest Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #007bff;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #555;
            margin-top: 30px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #007bff;
            color: white;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .summary {{
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
            font-family: monospace;
            white-space: pre-wrap;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Backtest Report</h1>
        
        <h2>Summary</h2>
        <div class="summary">{self.generate_summary_text()}</div>
        
        <h2>Performance Metrics</h2>
        {metrics_html}
        
        <h2>Visual Analysis</h2>
        {fig.to_html(include_plotlyjs='cdn', full_html=False)}
        
        <h2>Trade Details</h2>
        {trades_html}
    </div>
</body>
</html>
"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"HTML report saved to {filename}")
