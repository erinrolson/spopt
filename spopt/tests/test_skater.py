import geopandas
import libpysal
import numpy
from sklearn.metrics import pairwise as skm
import unittest

from spopt.region import Skater


# Empirical tests
RANDOM_STATE = 12345
# -- Mexican states
pth = libpysal.examples.get_path("mexicojoin.shp")
MEXICO = geopandas.read_file(pth)
# -- Columbus
pth = libpysal.examples.get_path("columbus.shp")
COLUMBUS = geopandas.read_file(pth)


class TestSkater(unittest.TestCase):
    def setUp(self):

        # Mexico
        self.mexico = MEXICO.copy()
        self.w_mexico = libpysal.weights.Queen.from_dataframe(self.mexico)
        self.default_attrs_mexico = [f"PCGDP{year}" for year in range(1950, 2010, 10)]
        self.default_mexico = [0, 0, 1, 2, 2, 1, 1, 1, 1, 1, 3, 2, 1, 1, 1, 1]
        self.default_mexico += [4, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 1, 1]
        self.non_default_mexico = [0, 0, 1, 2, 2, 3, 4, 5, 6, 4, 4, 2, 5, 7, 7, 5, 7]
        self.non_default_mexico += [5, 6, 6, 6, 6, 0, 8, 8, 1, 1, 3, 3, 8, 3, 3]

        # Columbus (synth island)
        self.columbus = COLUMBUS.copy()
        remove = [13, 14, 17, 18, 20, 23, 24, 29]
        self.columbus = self.columbus[~self.columbus.index.isin(remove)]
        self.w_columbus = libpysal.weights.Queen.from_dataframe(self.columbus)
        self.attrs_columbus = ["HOVAL", "INC", "CRIME", "OPEN", "PLUMB", "DISCBD"]
        self.columbus_labels = [0, 0, 0, 0, 1, 1, 0, 0, 2, 3, 1, 1, 0, 1, 3]
        self.columbus_labels += [3, 2, 3, 2, 2, 2, 2, 4, 3, 2, 4, 2, 4]
        self.columbus_labels += [5, 2, 4, 3, 3, 4, 5, 5, 5, 4, 3, 5, 5]

    def test_skater_defaults(self):
        self.mexico["count"] = 1
        numpy.random.seed(RANDOM_STATE)
        model = Skater(self.mexico, self.w_mexico, self.default_attrs_mexico)
        model.solve()

        numpy.testing.assert_equal(model.labels_, self.default_mexico)

    def test_skater_defaults_verbose(self):
        self.mexico["count"] = 1
        sfkws = {"verbose": 1}
        numpy.random.seed(RANDOM_STATE)
        model = Skater(
            self.mexico,
            self.w_mexico,
            self.default_attrs_mexico,
            spanning_forest_kwds=sfkws,
        )
        model.solve()

        numpy.testing.assert_equal(model.labels_, self.default_mexico)

    def test_skater_defaults_super_verbose(self):
        self.mexico["count"] = 1
        sfkws = {"verbose": 2}
        numpy.random.seed(RANDOM_STATE)
        model = Skater(
            self.mexico,
            self.w_mexico,
            self.default_attrs_mexico,
            spanning_forest_kwds=sfkws,
        )
        model.solve()

        numpy.testing.assert_equal(model.labels_, self.default_mexico)

    def test_skater_defaults_non_defaults(self):
        self.mexico["count"] = 1
        args = self.mexico, self.w_mexico, self.default_attrs_mexico
        n_clusters, floor, trace, islands = 10, 3, True, "ignore"
        kws = dict(n_clusters=n_clusters, floor=floor, trace=trace, islands=islands)
        sfkws = dict(
            dissimilarity=skm.manhattan_distances,
            affinity=None,
            reduction=numpy.sum,
            center=numpy.mean,
            verbose=2,
        )
        kws.update(dict(spanning_forest_kwds=sfkws))
        numpy.random.seed(RANDOM_STATE)
        model = Skater(*args, **kws)
        model.solve()

        numpy.testing.assert_equal(model.labels_, self.non_default_mexico)

    def test_skater_island_pass(self):
        self.columbus["count"] = 1
        args = self.columbus, self.w_columbus, self.attrs_columbus
        n_clusters, floor, trace, islands = 10, 5, True, "increase"
        kws = dict(n_clusters=n_clusters, floor=floor, trace=trace, islands=islands)
        sfkws = dict(dissimilarity=skm.euclidean_distances)
        kws.update(dict(spanning_forest_kwds=sfkws))
        numpy.random.seed(RANDOM_STATE)
        model = Skater(*args, **kws)
        model.solve()

        numpy.testing.assert_equal(model.labels_, self.columbus_labels)

    def test_skater_island_fail(self):
        with self.assertRaises(ValueError):
            self.columbus["count"] = 1
            args = self.columbus, self.w_columbus, self.attrs_columbus
            n_clusters, floor, trace, islands = 10, 10, True, "increase"
            kws = dict(n_clusters=n_clusters, floor=floor, trace=trace, islands=islands)
            sfkws = dict(dissimilarity=skm.euclidean_distances)
            kws.update(dict(spanning_forest_kwds=sfkws))
            numpy.random.seed(RANDOM_STATE)
            model = Skater(*args, **kws)
            model.solve()
