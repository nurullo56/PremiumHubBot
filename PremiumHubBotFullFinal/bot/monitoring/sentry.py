"""Sentry integration for error tracking."""

import logging

logger = logging.getLogger(__name__)

_sentry_initialized = False


def init_sentry(dsn: str = None, environment: str = "production"):
    """
    Initialize Sentry error tracking.
    
    Args:
        dsn: Sentry DSN (if None, Sentry won't be initialized)
        environment: Environment name (production, staging, development)
    """
    global _sentry_initialized
    
    if not dsn:
        logger.info("⚠️ Sentry DSN not provided, error tracking disabled")
        return
    
    try:
        import sentry_sdk
        
        sentry_sdk.init(
            dsn=dsn,
            environment=environment,
            traces_sample_rate=0.1,
            profiles_sample_rate=0.1,
            enable_tracing=True,
        )
        
        _sentry_initialized = True
        logger.info(f"✅ Sentry initialized (environment: {environment})")
        
    except ImportError:
        logger.warning("⚠️ sentry-sdk not installed, error tracking disabled")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Sentry: {e}")


def capture_exception(exception: Exception, **kwargs):
    """
    Capture exception and send to Sentry.
    
    Args:
        exception: Exception to capture
        **kwargs: Additional context
    """
    if not _sentry_initialized:
        return
    
    try:
        import sentry_sdk
        
        with sentry_sdk.push_scope() as scope:
            for key, value in kwargs.items():
                scope.set_context(key, value)
            
            sentry_sdk.capture_exception(exception)
            
    except Exception as e:
        logger.error(f"❌ Failed to send exception to Sentry: {e}")


def capture_message(message: str, level: str = "info", **kwargs):
    """
    Capture message and send to Sentry.
    
    Args:
        message: Message to capture
        level: Severity level (info, warning, error)
        **kwargs: Additional context
    """
    if not _sentry_initialized:
        return
    
    try:
        import sentry_sdk
        
        with sentry_sdk.push_scope() as scope:
            for key, value in kwargs.items():
                scope.set_context(key, value)
            
            sentry_sdk.capture_message(message, level=level)
            
    except Exception as e:
        logger.error(f"❌ Failed to send message to Sentry: {e}")
