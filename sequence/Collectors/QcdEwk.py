import logging

from .Histogrammer import HistCollector

class QcdEwkCollector(HistCollector):
    def draw(self, histograms):
        logger = logging.getLogger(__name__)
        logger.info(histograms)
