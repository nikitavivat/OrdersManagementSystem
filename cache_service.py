import json
import asyncio
from typing import Optional, Any, Dict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._default_ttl = 300  # 5 минут по умолчанию
    
    def _is_expired(self, cache_entry: Dict[str, Any]) -> bool:
        """Проверяет, истек ли срок действия кэша"""
        if 'expires_at' not in cache_entry:
            return True
        return datetime.now() > cache_entry['expires_at']
    
    def _generate_key(self, prefix: str, **kwargs) -> str:
        """Генерирует ключ кэша на основе префикса и параметров"""
        key_parts = [prefix]
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}:{v}")
        return ":".join(key_parts)
    
    async def get(self, key: str) -> Optional[Any]:
        """Получает значение из кэша"""
        if key not in self._cache:
            return None
        
        cache_entry = self._cache[key]
        if self._is_expired(cache_entry):
            del self._cache[key]
            logger.debug(f"Cache expired for key: {key}")
            return None
        
        logger.debug(f"Cache hit for key: {key}")
        return cache_entry['value']
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Сохраняет значение в кэш"""
        ttl = ttl or self._default_ttl
        expires_at = datetime.now() + timedelta(seconds=ttl)
        
        self._cache[key] = {
            'value': value,
            'expires_at': expires_at,
            'created_at': datetime.now()
        }
        
        logger.debug(f"Cache set for key: {key}, TTL: {ttl}s")
    
    async def delete(self, key: str) -> None:
        """Удаляет значение из кэша"""
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"Cache deleted for key: {key}")
    
    async def delete_pattern(self, pattern: str) -> None:
        """Удаляет все ключи, соответствующие паттерну"""
        keys_to_delete = [key for key in self._cache.keys() if pattern in key]
        for key in keys_to_delete:
            del self._cache[key]
        logger.debug(f"Cache pattern deleted: {pattern}, keys: {len(keys_to_delete)}")
    
    async def get_or_set(self, key: str, func, ttl: Optional[int] = None, *args, **kwargs) -> Any:
        """Получает значение из кэша или вычисляет и сохраняет"""
        cached_value = await self.get(key)
        if cached_value is not None:
            return cached_value
        
        # Вычисляем значение
        if asyncio.iscoroutinefunction(func):
            value = await func(*args, **kwargs)
        else:
            value = func(*args, **kwargs)
        
        await self.set(key, value, ttl)
        return value
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Возвращает статистику кэша"""
        total_keys = len(self._cache)
        expired_keys = sum(1 for entry in self._cache.values() if self._is_expired(entry))
        active_keys = total_keys - expired_keys
        
        return {
            'total_keys': total_keys,
            'active_keys': active_keys,
            'expired_keys': expired_keys,
            'memory_usage_mb': len(str(self._cache)) / 1024 / 1024
        }

# Глобальный экземпляр кэша
cache_service = CacheService()
