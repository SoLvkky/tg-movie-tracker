import json
import logging
from pathlib import Path
from contextvars import ContextVar
from typing import Dict, Any

logger = logging.getLogger(__name__)

_translations: Dict[str, Dict[str, Any]] = {}
current_locale = ContextVar('locale', default='en-US')

def load_locales(dir_path: str = 'bot/locales') -> None:
    global _translations
    _translations.clear()
    
    path = Path(dir_path)
    if not path.exists():
        logger.error(f"Locales path not found: {path.absolute()}")
        return
    
    files = list(path.glob('*.json'))
    if not files:
        logger.error(f"No JSON files in {path}")
        return
    
    for file in files:
        try:
            lang = file.stem
            content = json.loads(file.read_text('utf-8'))
            _translations[lang] = content
            logger.info(f"Loaded {lang}: {len(content)} keys")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON {file}: {e}")
        except Exception as e:
            logger.error(f"Failed to load {file}: {e}")
    
    logger.info(f"i18n ready: {list(_translations.keys())}")

def t(key: str, **kwargs: Any) -> str:
    try:
        locale = current_locale.get()
        data = _translations.get(locale, _translations.get('en-US', {}))
        
        for part in key.split('.'):
            if isinstance(data, dict):
                data = data.get(part, f'[{locale}:{key}]')
            else:
                break
        
        text = str(data)
    except Exception:
        text = f'[{key}]'
    
    return text.format(**kwargs) if kwargs else text

load_locales()