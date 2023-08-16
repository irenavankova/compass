from compass.ocean.tests.global_ocean.analysis_test import AnalysisTest
from compass.ocean.tests.global_ocean.daily_output_test import DailyOutputTest
from compass.ocean.tests.global_ocean.data_ice_shelf_melt import (
    DataIceShelfMelt,
)
from compass.ocean.tests.global_ocean.decomp_test import DecompTest
from compass.ocean.tests.global_ocean.files_for_e3sm import FilesForE3SM
from compass.ocean.tests.global_ocean.init import Init
from compass.ocean.tests.global_ocean.mesh import Mesh
from compass.ocean.tests.global_ocean.mesh.arrm10to60.dynamic_adjustment import (  # noqa: E501
    ARRM10to60DynamicAdjustment,
)
from compass.ocean.tests.global_ocean.mesh.ec30to60.dynamic_adjustment import (
    EC30to60DynamicAdjustment,
)
from compass.ocean.tests.global_ocean.mesh.kuroshio.dynamic_adjustment import (
    KuroshioDynamicAdjustment,
)
from compass.ocean.tests.global_ocean.mesh.qu240.dynamic_adjustment import (
    QU240DynamicAdjustment,
)
from compass.ocean.tests.global_ocean.mesh.qu.dynamic_adjustment import (
    QUDynamicAdjustment,
)
from compass.ocean.tests.global_ocean.mesh.rrs6to18.dynamic_adjustment import (
    RRS6to18DynamicAdjustment,
)
from compass.ocean.tests.global_ocean.mesh.so12to60.dynamic_adjustment import (
    SO12to60DynamicAdjustment,
)
from compass.ocean.tests.global_ocean.mesh.wc14.dynamic_adjustment import (
    WC14DynamicAdjustment,
)
from compass.ocean.tests.global_ocean.mesh.fris01to60.dynamic_adjustment import (
    FRIS01to60DynamicAdjustment,
)
from compass.ocean.tests.global_ocean.mesh.fris02to60.dynamic_adjustment import (
    FRIS02to60DynamicAdjustment,
)
from compass.ocean.tests.global_ocean.mesh.fris04to60.dynamic_adjustment import (
    FRIS04to60DynamicAdjustment,
)
from compass.ocean.tests.global_ocean.mesh.fris08to60.dynamic_adjustment import (
    FRIS08to60DynamicAdjustment,
)
from compass.ocean.tests.global_ocean.monthly_output_test import (
    MonthlyOutputTest,
)
from compass.ocean.tests.global_ocean.performance_test import PerformanceTest
from compass.ocean.tests.global_ocean.restart_test import RestartTest
from compass.ocean.tests.global_ocean.threads_test import ThreadsTest
from compass.testgroup import TestGroup


class GlobalOcean(TestGroup):
    """
    A test group for setting up global initial conditions and performing
    regression testing and dynamic adjustment for MPAS-Ocean
    """
    def __init__(self, mpas_core):
        """
        mpas_core : compass.MpasCore
            the MPAS core that this test group belongs to
        """
        super().__init__(mpas_core=mpas_core, name='global_ocean')

        # we do a lot of tests for QU240/QUwISC240
        self._add_tests(mesh_names=['QU240', 'Icos240', 'QUwISC240'],
                        DynamicAdjustment=QU240DynamicAdjustment,
                        high_res_topography=False,
                        include_rk4=True,
                        include_regression=True,
                        include_phc=True,
                        include_en4_1900=True)

        # for other meshes, we do fewer tests
        self._add_tests(mesh_names=['QU', 'Icos', 'QUwISC', 'IcoswISC'],
                        DynamicAdjustment=QUDynamicAdjustment)

        self._add_tests(mesh_names=['EC30to60', 'ECwISC30to60'],
                        DynamicAdjustment=EC30to60DynamicAdjustment)

        self._add_tests(mesh_names=['ARRM10to60', 'ARRMwISC10to60'],
                        DynamicAdjustment=ARRM10to60DynamicAdjustment)

        self._add_tests(mesh_names=['SO12to60', 'SOwISC12to60'],
                        DynamicAdjustment=SO12to60DynamicAdjustment)

        self._add_tests(mesh_names=['WC14', 'WCwISC14'],
                        DynamicAdjustment=WC14DynamicAdjustment)

        # RRS6to18: with and without cavities
        self._add_tests(mesh_names=['RRS6to18', 'RRSwISC6to18'],
                        DynamicAdjustment=RRS6to18DynamicAdjustment)

        # Kuroshio meshes without ice-shelf cavities
        self._add_tests(mesh_names=['Kuroshio12to60', 'Kuroshio8to60'],
                        DynamicAdjustment=KuroshioDynamicAdjustment)
        '''
        # FRIS01to60: with and without cavities
        self._add_tests(mesh_names=['FRIS01to60', 'FRISwISC01to60'],
                        DynamicAdjustment=FRIS01to60DynamicAdjustment)

        # FRIS01to60: with and without cavities
        self._add_tests(mesh_names=['FRIS02to60', 'FRISwISC02to60'],
                        DynamicAdjustment=FRIS02to60DynamicAdjustment)

        # FRIS01to60: with and without cavities
        self._add_tests(mesh_names=['FRIS04to60', 'FRISwISC04to60'],
                        DynamicAdjustment=FRIS04to60DynamicAdjustment)

        # FRIS01to60: with and without cavities
        self._add_tests(mesh_names=['FRIS08to60', 'FRISwISC08to60'],
                        DynamicAdjustment=FRIS08to60DynamicAdjustment)
        '''
        for mesh_name in ['FRIS01to60', 'FRISwISC01to60']:
            mesh_test = Mesh(test_group=self, mesh_name=mesh_name,
                             high_res_topography=True)
            self.add_test_case(mesh_test)

            init_test = Init(test_group=self, mesh=mesh_test,
                             initial_condition='WOA23')
            self.add_test_case(init_test)

            self.add_test_case(
                PerformanceTest(
                    test_group=self, mesh=mesh_test, init=init_test,
                    time_integrator='split_explicit'))

            dynamic_adjustment_test = FRIS01to60DynamicAdjustment(
                test_group=self, mesh=mesh_test, init=init_test,
                time_integrator='split_explicit')
            self.add_test_case(dynamic_adjustment_test)

        for mesh_name in ['FRIS02to60', 'FRISwISC02to60']:
            mesh_test = Mesh(test_group=self, mesh_name=mesh_name,
                             high_res_topography=True)
            self.add_test_case(mesh_test)

            init_test = Init(test_group=self, mesh=mesh_test,
                             initial_condition='WOA23')
            self.add_test_case(init_test)

            self.add_test_case(
                PerformanceTest(
                    test_group=self, mesh=mesh_test, init=init_test,
                    time_integrator='split_explicit'))

            dynamic_adjustment_test = FRIS02to60DynamicAdjustment(
                test_group=self, mesh=mesh_test, init=init_test,
                time_integrator='split_explicit')
            self.add_test_case(dynamic_adjustment_test)

        for mesh_name in ['FRIS04to60', 'FRISwISC04to60']:
            mesh_test = Mesh(test_group=self, mesh_name=mesh_name,
                             high_res_topography=True)
            self.add_test_case(mesh_test)

            init_test = Init(test_group=self, mesh=mesh_test,
                             initial_condition='WOA23')
            self.add_test_case(init_test)

            self.add_test_case(
                PerformanceTest(
                    test_group=self, mesh=mesh_test, init=init_test,
                    time_integrator='split_explicit'))

            dynamic_adjustment_test = FRIS04to60DynamicAdjustment(
                test_group=self, mesh=mesh_test, init=init_test,
                time_integrator='split_explicit')
            self.add_test_case(dynamic_adjustment_test)

        for mesh_name in ['FRIS08to60', 'FRISwISC08to60']:
            mesh_test = Mesh(test_group=self, mesh_name=mesh_name,
                             high_res_topography=True)
            self.add_test_case(mesh_test)

            init_test = Init(test_group=self, mesh=mesh_test,
                             initial_condition='WOA23')
            self.add_test_case(init_test)

            self.add_test_case(
                PerformanceTest(
                    test_group=self, mesh=mesh_test, init=init_test,
                    time_integrator='split_explicit'))

            dynamic_adjustment_test = FRIS08to60DynamicAdjustment(
                test_group=self, mesh=mesh_test, init=init_test,
                time_integrator='split_explicit')
            self.add_test_case(dynamic_adjustment_test)

        # A test case for making E3SM support files from an existing mesh
        self.add_test_case(FilesForE3SM(test_group=self))

            #dynamic_adjustment_test = DynamicAdjustment(
            #    test_group=self, mesh=mesh_test, init=init_test,
            #    time_integrator=time_integrator)
            #self.add_test_case(dynamic_adjustment_test)
            #self.add_test_case(
            #    FilesForE3SM(
            #        test_group=self, mesh=mesh_test, init=init_test,
            #        dynamic_adjustment=dynamic_adjustment_test))


    def _add_tests(self, mesh_names, DynamicAdjustment,
                   high_res_topography=True, include_rk4=False,
                   include_regression=False, include_phc=False,
                   include_en4_1900=False):
        """ Add test cases for the given mesh(es) """

        default_ic = 'WOA23'
        default_time_int = 'split_explicit'

        for mesh_name in mesh_names:
            mesh_test = Mesh(test_group=self, mesh_name=mesh_name,
                             high_res_topography=high_res_topography)
            self.add_test_case(mesh_test)

            init_test = Init(test_group=self, mesh=mesh_test,
                             initial_condition=default_ic)
            self.add_test_case(init_test)

            time_integrator = default_time_int
            self.add_test_case(
                PerformanceTest(
                    test_group=self, mesh=mesh_test, init=init_test,
                    time_integrator=time_integrator))
            if include_regression:
                self.add_test_case(
                    RestartTest(
                        test_group=self, mesh=mesh_test, init=init_test,
                        time_integrator=time_integrator))
                self.add_test_case(
                    DecompTest(
                        test_group=self, mesh=mesh_test, init=init_test,
                        time_integrator=time_integrator))
                self.add_test_case(
                    ThreadsTest(
                        test_group=self, mesh=mesh_test, init=init_test,
                        time_integrator=time_integrator))
                self.add_test_case(
                    AnalysisTest(
                        test_group=self, mesh=mesh_test, init=init_test,
                        time_integrator=time_integrator))
                self.add_test_case(
                    DailyOutputTest(
                        test_group=self, mesh=mesh_test, init=init_test,
                        time_integrator=time_integrator))
                self.add_test_case(
                    MonthlyOutputTest(
                        test_group=self, mesh=mesh_test, init=init_test,
                        time_integrator=time_integrator))

            if mesh_test.with_ice_shelf_cavities:
                data_melt_test = DataIceShelfMelt(
                    test_group=self, mesh=mesh_test, init=init_test,
                    time_integrator=time_integrator)
                self.add_test_case(data_melt_test)
            else:
                data_melt_test = None

            dynamic_adjustment_test = DynamicAdjustment(
                test_group=self, mesh=mesh_test, init=init_test,
                time_integrator=time_integrator)
            self.add_test_case(dynamic_adjustment_test)

            self.add_test_case(
                FilesForE3SM(
                    test_group=self, mesh=mesh_test, init=init_test,
                    dynamic_adjustment=dynamic_adjustment_test,
                    data_ice_shelf_melt=data_melt_test))

            if include_rk4:
                time_integrator = 'RK4'
                self.add_test_case(
                    PerformanceTest(
                        test_group=self, mesh=mesh_test, init=init_test,
                        time_integrator=time_integrator))
                self.add_test_case(
                    RestartTest(
                        test_group=self, mesh=mesh_test, init=init_test,
                        time_integrator=time_integrator))
                self.add_test_case(
                    DecompTest(
                        test_group=self, mesh=mesh_test, init=init_test,
                        time_integrator=time_integrator))
                self.add_test_case(
                    ThreadsTest(
                        test_group=self, mesh=mesh_test, init=init_test,
                        time_integrator=time_integrator))

            initial_conditions = []
            if include_phc:
                initial_conditions.append('PHC')
            if include_en4_1900:
                initial_conditions.append('EN4_1900')

            for initial_condition in initial_conditions:
                # additional initial conditions (if any)
                time_integrator = default_time_int
                init_test = Init(test_group=self, mesh=mesh_test,
                                 initial_condition=initial_condition)
                self.add_test_case(init_test)

                self.add_test_case(
                    PerformanceTest(
                        test_group=self, mesh=mesh_test, init=init_test,
                        time_integrator=time_integrator))

                if mesh_test.with_ice_shelf_cavities:
                    data_melt_test = DataIceShelfMelt(
                        test_group=self, mesh=mesh_test, init=init_test,
                        time_integrator=time_integrator)
                    self.add_test_case(data_melt_test)
                else:
                    data_melt_test = None

                dynamic_adjustment_test = DynamicAdjustment(
                    test_group=self, mesh=mesh_test, init=init_test,
                    time_integrator=time_integrator)
                self.add_test_case(dynamic_adjustment_test)

                self.add_test_case(
                    FilesForE3SM(
                        test_group=self, mesh=mesh_test, init=init_test,
                        dynamic_adjustment=dynamic_adjustment_test,
                        data_ice_shelf_melt=data_melt_test))
