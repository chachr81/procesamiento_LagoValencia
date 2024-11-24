from datetime import datetime

from shapely.geometry import Point
from pylandsat import Catalog, Product

catalog = Catalog()

begin = datetime(2000, 1, 1)
end = datetime(2010, 1, 1)
geom = Point(4.34, 50.85)

# Results are returned as a list
scenes = catalog.search(
    begin=begin,
    end=end,
    geom=geom,
    sensors=['ETM', 'LC08']
)