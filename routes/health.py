"""
Enhanced Health Check Endpoint with Dependencies
Provides comprehensive system health status
"""
from flask import Blueprint, jsonify
from typing import Dict, Any
import time
import psutil

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def basic_health():
    """Basic health check - just alive/dead"""
    return jsonify({'status': 'healthy', 'timestamp': time.time()}), 200


@health_bp.route('/health/detailed', methods=['GET'])
def detailed_health():
    """Detailed health check with all dependencies"""
    health_status = {
        'status': 'healthy',
        'timestamp': time.time(),
        'version': '2.0.0',
        'checks': {}
    }

    overall_healthy = True

    # Check database
    db_health = check_database()
    health_status['checks']['database'] = db_health
    if not db_health['healthy']:
        overall_healthy = False

    # Check Redis
    redis_health = check_redis()
    health_status['checks']['redis'] = redis_health
    if not redis_health['healthy']:
        overall_healthy = False

    # Check OpenAI API
    openai_health = check_openai()
    health_status['checks']['openai'] = openai_health
    # OpenAI is optional, don't mark as unhealthy

    # System resources
    system_health = check_system_resources()
    health_status['checks']['system'] = system_health
    if not system_health['healthy']:
        overall_healthy = False

    # Set overall status
    health_status['status'] = 'healthy' if overall_healthy else 'unhealthy'
    status_code = 200 if overall_healthy else 503

    return jsonify(health_status), status_code


@health_bp.route('/health/ready', methods=['GET'])
def readiness_check():
    """Kubernetes readiness probe - can accept traffic?"""
    # Check critical dependencies only
    db_ready = check_database()['healthy']
    redis_ready = check_redis()['healthy']

    if db_ready and redis_ready:
        return jsonify({'status': 'ready'}), 200
    else:
        return jsonify({'status': 'not ready'}), 503


@health_bp.route('/health/live', methods=['GET'])
def liveness_check():
    """Kubernetes liveness probe - should restart?"""
    # Basic check - if we can respond, we're alive
    return jsonify({'status': 'alive'}), 200


def check_database() -> Dict[str, Any]:
    """Check MongoDB connection"""
    try:
        from flask import current_app
        mongo = current_app.mongo

        start_time = time.time()
        mongo.db.command('ping')
        response_time = (time.time() - start_time) * 1000

        return {
            'healthy': True,
            'response_time_ms': round(response_time, 2),
            'message': 'Database connection successful'
        }
    except Exception as e:
        return {
            'healthy': False,
            'response_time_ms': 0,
            'message': f'Database connection failed: {str(e)}'
        }


def check_redis() -> Dict[str, Any]:
    """Check Redis connection"""
    try:
        import redis
        from config import Config

        r = redis.from_url(Config.REDIS_URL or 'redis://localhost:6379')

        start_time = time.time()
        r.ping()
        response_time = (time.time() - start_time) * 1000

        return {
            'healthy': True,
            'response_time_ms': round(response_time, 2),
            'message': 'Redis connection successful'
        }
    except Exception as e:
        return {
            'healthy': False,
            'response_time_ms': 0,
            'message': f'Redis connection failed: {str(e)}'
        }


def check_openai() -> Dict[str, Any]:
    """Check OpenAI API availability (optional)"""
    try:
        from config import Config

        if not Config.OPENAI_API_KEY or Config.OPENAI_API_KEY == 'your_openai_api_key_here':
            return {
                'healthy': True,
                'available': False,
                'message': 'OpenAI API key not configured (fallback mode active)'
            }

        # Could add actual API call here, but avoid in health check
        return {
            'healthy': True,
            'available': True,
            'message': 'OpenAI API key configured'
        }
    except Exception as e:
        return {
            'healthy': True,  # Don't fail health check
            'available': False,
            'message': f'OpenAI check failed: {str(e)}'
        }


def check_system_resources() -> Dict[str, Any]:
    """Check system resource usage"""
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        # Thresholds
        cpu_ok = cpu_percent < 90
        memory_ok = memory.percent < 90
        disk_ok = disk.percent < 90

        healthy = cpu_ok and memory_ok and disk_ok

        return {
            'healthy': healthy,
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'disk_percent': disk.percent,
            'message': 'System resources OK' if healthy else 'High resource usage detected'
        }
    except Exception as e:
        return {
            'healthy': True,  # Don't fail on monitoring errors
            'message': f'System check failed: {str(e)}'
        }
