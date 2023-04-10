import logging
import argparse
import os
from app.modules.interfaces.base import CommonDataHolderModel

scriptname = os.path.basename(__file__)
parser = argparse.ArgumentParser(scriptname)
levels = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
parser.add_argument('--log-level', default='INFO', choices=levels)
options = parser.parse_args()

logging.basicConfig(format='%(asctime)s - %(name)-30s - %(levelname)-10s - %(message)s', level=options.log_level)

logger = logging.getLogger(__name__)
logger.debug("Setting up logger basic info for all to use.")

common = CommonDataHolderModel()
