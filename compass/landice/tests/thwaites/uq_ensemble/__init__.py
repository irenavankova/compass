from compass.validate import compare_variables
from compass.testcase import TestCase
from compass.landice.tests.thwaites.uq_ensemble.ensemble \
        import CreateEnsembleMember


class UQEnsemble(TestCase):
    """
    A test case for performing two MALI runs of the Thwaites setup,
    with two different core counts.  The test case verifies that the
    results of the two runs are identical.
    """

    def __init__(self, test_group):
        """
        Create the test case

        Parameters
        ----------
        test_group : compass.landice.tests.thwaites.Thwaites
            The test group that this test case belongs to

        """
        name = 'thwaites_uq'
        super().__init__(test_group=test_group, name=name)

        # We need the list of runs to set up steps.
        # Steps need to be defined in TestCase.__init__
        # But we want to keep operations to a minimum

        self.nRuns = 20 # number of runs in ensemble
        for runNum in range(self.nRuns):
            self.add_step(
                CreateEnsembleMember(test_case=self,
                                     runNum=runNum))

    # no configure() method is needed

    # no run() method is needed

    # no validate() method is needed
