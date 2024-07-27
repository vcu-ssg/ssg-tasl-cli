
import sys
from loguru import logger
import argparse


# Define custom message templates
#info_template = "<green>{time}</green> - <level>{level}</level> - <cyan>{message}</cyan>"
#success_template = "<green>{time}</green> - <level>{level}</level> - <magenta>{message}</magenta>"
#warning_template = "<green>{time}</green> - <level>{level}</level> - <yellow>{message}</yellow>"

info_template = "<cyan>INFO: {message}</cyan>"
success_template = "{message}"
warning_template = "<yellow>{level}</yellow>: <yellow>{message}</yellow>"
default_format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"


# Values: "TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"
DEFAULT_LOG_LEVEL = 'INFO'


def sniff_log_level():
    """ take early look at command line, setting log_level as early as possible """
    # disable help, parse only known arguments.  You're sniffing early!
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--log-level', type=str)

    args, unknown = parser.parse_known_args()
    log_level = args.log_level
    return log_level


log_level = sniff_log_level()
if log_level is None:
    log_level=DEFAULT_LOG_LEVEL

if not log_level==DEFAULT_LOG_LEVEL:
    logger.success(f"Log level set to {log_level} by --log-level argument (early).")

# Remove the default handler
logger.remove()

simple_format = "{message}"

simple_levels = ["INFO","SUCCESS","WARNING"]

log_levels = [level.name for level in logger._core.levels.values() if level.no >= logger.level(log_level).no and not level.name in simple_levels ]

# Remove the default logger configuration
logger.remove()

logger.add(sys.stderr, format=default_format, level=log_level, filter=lambda record: record["level"].name in log_levels)

# this code is written out because of a bug in logger.add
if "INFO" in simple_levels and logger.level(log_level).no <= logger.level("INFO").no:
    logger.add(sys.stderr, format=info_template, level='INFO', filter=lambda record: record["level"].name=='INFO' )
if "SUCCESS" in simple_levels and logger.level(log_level).no <= logger.level("SUCCESS").no:
    logger.add(sys.stderr, format=success_template, level='SUCCESS', filter=lambda record: record["level"].name=='SUCCESS' )
if "WARNING" in simple_levels and logger.level(log_level).no <= logger.level("WARNING").no:
    logger.add(sys.stderr, format=warning_template, level='WARNING', filter=lambda record: record["level"].name=='WARNING' )
if "ERROR" in simple_levels and logger.level(log_level).no <= logger.level("ERROR").no:
    logger.add(sys.stderr, format=default_format, level='ERROR', filter=lambda record: record["level"].name=='ERROR' )
if "CRITICAL" in simple_levels and logger.level(log_level).no <= logger.level("CRITICAL").no:
    logger.add(sys.stderr, format=default_format, level='CRITICAL', filter=lambda record: record["level"].name=='CRITICAL' )
