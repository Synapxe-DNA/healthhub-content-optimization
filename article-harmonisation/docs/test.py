import sys

sys.path.append("content-optimization/src/content_optimization/utils/")

from extract import HTMLExtractor

HTMLExtractor(
    "https://www.healthhub.sg/a-z/costs-and-financing/breast-cancer-screening-subsidies"
)
