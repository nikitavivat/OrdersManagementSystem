import time
from typing import Dict, Any
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import logging

logger = logging.getLogger(__name__)

# Метрики Prometheus
REQUEST_COUNT = Counter(
    'http_requests_total', 
    'Total HTTP requests', 
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_CONNECTIONS = Gauge(
    'active_connections',
    'Number of active connections'
)

CACHE_HITS = Counter(
    'cache_hits_total',
    'Total cache hits',
    ['cache_type']
)

CACHE_MISSES = Counter(
    'cache_misses_total',
    'Total cache misses',
    ['cache_type']
)

DATABASE_QUERIES = Counter(
    'database_queries_total',
    'Total database queries',
    ['operation', 'table']
)

class MetricsService:
    def __init__(self):
        self._start_time = time.time()
        self._request_times: Dict[str, float] = {}
    
    def record_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Записывает метрику запроса"""
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status_code).inc()
        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
    
    def record_cache_hit(self, cache_type: str):
        """Записывает попадание в кэш"""
        CACHE_HITS.labels(cache_type=cache_type).inc()
    
    def record_cache_miss(self, cache_type: str):
        """Записывает промах кэша"""
        CACHE_MISSES.labels(cache_type=cache_type).inc()
    
    def record_database_query(self, operation: str, table: str):
        """Записывает запрос к базе данных"""
        DATABASE_QUERIES.labels(operation=operation, table=table).inc()
    
    def set_active_connections(self, count: int):
        """Устанавливает количество активных соединений"""
        ACTIVE_CONNECTIONS.set(count)
    
    def get_uptime(self) -> float:
        """Возвращает время работы приложения"""
        return time.time() - self._start_time
    
    def get_metrics(self) -> str:
        """Возвращает метрики в формате Prometheus"""
        return generate_latest().decode('utf-8')
    
    def get_health_status(self) -> Dict[str, Any]:
        """Возвращает статус здоровья приложения"""
        uptime = self.get_uptime()
        
        return {
            'status': 'healthy',
            'uptime_seconds': uptime,
            'uptime_human': self._format_uptime(uptime),
            'timestamp': time.time()
        }
    
    def _format_uptime(self, seconds: float) -> str:
        """Форматирует время работы в читаемый вид"""
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m {secs}s"
        elif hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"

# Глобальный экземпляр сервиса метрик
metrics_service = MetricsService()
