"""Progress-grid parents cannot cross either zero-progress boundary."""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from generation import make
from unrestricted_grid import solve_unrestricted
from unrestricted_checker import InvalidGridCertificate, check_unrestricted


class GridBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.instance = make('boundary-regression', [(2, 3, 1, 2), (4, 1, 2, 1)], 'regression')
        self.certificate = solve_unrestricted(self.instance)

    def test_valid_certificate(self):
        result = check_unrestricted(self.instance, self.certificate)
        self.assertEqual(result['value'], self.certificate['upper_bound'])

    def test_stream_one_cannot_precede_top_boundary(self):
        certificate = copy.deepcopy(self.certificate)
        certificate['cells'][0][1]['states'][0].update(stream=1, parent_cell=[-1, 1], parent=0)
        with self.assertRaises(InvalidGridCertificate):
            check_unrestricted(self.instance, certificate)

    def test_stream_two_cannot_precede_left_boundary(self):
        certificate = copy.deepcopy(self.certificate)
        certificate['cells'][1][0]['states'][0].update(stream=2, parent_cell=[1, -1], parent=0)
        with self.assertRaises(InvalidGridCertificate):
            check_unrestricted(self.instance, certificate)


if __name__ == '__main__':
    unittest.main()
