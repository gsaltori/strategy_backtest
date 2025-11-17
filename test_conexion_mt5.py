from data_manager import MT5DataManager
from datetime import datetime, timedelta

# Conexión automática (sin parámetros)
data_manager = MT5DataManager()

if data_manager.connect():
    print("✅ Conectado exitosamente")
    
    # Ahora puedes descargar datos
    data = data_manager.get_historical_data(
        symbol="EURUSD",
        timeframe="H1",
        start_date=datetime.now() - timedelta(days=365),
        count=5000
    )
else:
    print("❌ Error de conexión")

# Siempre desconectar al final
data_manager.disconnect()