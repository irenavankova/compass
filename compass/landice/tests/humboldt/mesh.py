from compass.landice.mesh import build_cell_width, build_mali_mesh
from compass.model import make_graph_file
from compass.step import Step


class Mesh(Step):
    """
    A step for creating a mesh and initial condition for humboldt test cases

    Attributes
    ----------
    mesh_type : str
        The resolution or mesh type of the test case
    """
    def __init__(self, test_case):
        """
        Create the step

        Parameters
        ----------
        test_case : compass.TestCase
            The test case this step belongs to

        mesh_type : str
            The resolution or mesh type of the test case
        """
        super().__init__(test_case=test_case, name='mesh')

        self.add_output_file(filename='graph.info')
        self.add_output_file(filename='Humboldt.nc')
        self.add_input_file(
            filename='humboldt_1km_2020_04_20.epsg3413.icesheetonly.nc',
            target='humboldt_1km_2020_04_20.epsg3413.icesheetonly.nc',
            database='')
        self.add_input_file(filename='Humboldt.geojson',
                            package='compass.landice.tests.humboldt',
                            target='Humboldt.geojson',
                            database=None)
        self.add_input_file(filename='greenland_2km_2020_04_20.epsg3413.nc',
                            target='greenland_2km_2020_04_20.epsg3413.nc',
                            database='')

    # no setup() method is needed

    def run(self):
        """
        Run this step of the test case
        """
        logger = self.logger
        section_name = 'mesh'
        mesh_name = 'Humboldt.nc'

        logger.info('calling build_cell_width')
        cell_width, x1, y1, geom_points, geom_edges, floodMask = \
            build_cell_width(
                self, section_name=section_name,
                gridded_dataset='greenland_2km_2020_04_20.epsg3413.nc')

        build_mali_mesh(
            self, cell_width, x1, y1, geom_points, geom_edges,
            mesh_name=mesh_name, section_name=section_name,
            gridded_dataset='humboldt_1km_2020_04_20.epsg3413.icesheetonly.nc',
            projection='gis-gimp', geojson_file='Humboldt.geojson')

        logger.info('creating graph.info')
        make_graph_file(mesh_filename=mesh_name,
                        graph_filename='graph.info')
