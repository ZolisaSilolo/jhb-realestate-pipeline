import logging
import sys
import json
from datetime import datetime

def get_logger(component_name):
    """
    Creates a structured logger that outputs JSON-formatted logs.
    Args:
        component_name (str): e.g., 'LocalGenerator', 'DatabricksETL'
    """
    logger = logging.getLogger(component_name)
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        
        class JsonFormatter(logging.Formatter):
            def format(self, record):
                log_record = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "level": record.levelname,
                    "component": component_name,
                    "message": record.getMessage(),
                    "file": record.filename,
                    "line": record.lineno
                }
                if record.exc_info:
                    log_record["exception"] = self.formatException(record.exc_info)
                
                return json.dumps(log_record)

        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
        
    return logger
