import os
import operator

from utils.Histogramming import Histogram, Histograms
from Histogrammer import Config, HistReader, HistCollector

SystematicsReader = HistReader

class SystematicsCollector(HistCollector):
    def draw(self, histograms):
        return []
