from compass.testcase import TestCase


class Default(TestCase):
    """
    The default drying_slope test case

    Attributes
    ----------
    resolution : str
        The horizontal resolution of the test case

    coord_type : str
        The type of vertical coordinate (``z-star``, ``z-level``, etc.)
    """

    def __init__(self, test_group, resolution, coord_type):
        """
        Create the test case

        Parameters
        ----------
        test_group : compass.ocean.tests.drying_slope.DryingSlope
            The test group that this test case belongs to

        resolution : str
            The resolution of the test case

        coord_type : str
            The type of vertical coordinate (``sigma``, ``single_layer``)
        """
        name = 'default'

        self.resolution = resolution
        self.coord_type = coord_type
        subdir = '{}/{}/{}'.format(resolution, coord_type, name)
        super().__init__(test_group=test_group, name=name,
                         subdir=subdir)

