from compass.landice.tests.greenland.mesh import Mesh
from compass.testcase import TestCase


class MeshGen(TestCase):
    """
    The high resolution test case for the greenland test
    group simply creates the mesh and initial condition.
    The basal friction optimization occurs separately,
    outside of COMPASS.
    """

    def __init__(self, test_group):
        """
        Create the test case
        Parameters
        ----------
        test_group : compass.landice.tests.greenland.Greenland
            The test group that this test case belongs to
        """
        name = 'mesh_gen'
        subdir = name
        super().__init__(test_group=test_group, name=name,
                         subdir=subdir)

        self.add_step(
            Mesh(test_case=self))
