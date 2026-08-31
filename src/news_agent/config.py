import os
import re
from pathlib import Path

import yaml

from news_agent.utils.logger import logger


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def load_config(
    sources_path: str = "config/sources.yaml", project_root: Path | None = None
) -> dict:
    """Load and parse the YAML config, expanding ${ENV_VAR} placeholders."""
    root = project_root or PROJECT_ROOT
    config_path = root / sources_path
    if not config_path.exists():
        logger.error("Config file not found: %s", config_path)
        return {"sources": []}

    content = config_path.read_text(encoding="utf-8")

    def replace_env_var(match: re.Match) -> str:
        var_name = match.group(1)
        var_value = os.getenv(var_name)
        if var_value is None:
            logger.warning("Environment variable %s is not set", var_name)
            return match.group(0)
        return var_value

    expanded_content = re.sub(r"\$\{([^}^{]+)\}", replace_env_var, content)
    try:
        return yaml.safe_load(expanded_content) or {}
    except yaml.YAMLError as exc:
        logger.error("YAML parse error: %s", exc)
        return {}
