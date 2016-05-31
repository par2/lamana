#------------------------------------------------------------------------------
'''Test for consistency of utils.'''
# CAUTION: This module writes and removes temporary files in the "export" dir


import os
import sys
import abc
import logging
import tempfile
import difflib
##import collections as ct

import nose.tools as nt
import pandas as pd

import lamana as la
from lamana.models import Wilson_LT as wlt
from lamana.models.fixtures import fixture_model_func      # special import for hooks
from lamana.models.fixtures import fixture_model_class     # special import for hooks
from lamana.models.fixtures import fixture_model_module_a  # special import for hooks
from lamana.models.fixtures import fixture_model_module_b  # special import for hooksfrom lamana.utils import config
from lamana.utils import tools as ut
from lamana.utils import config

dft = wlt.Defaults()                                       # from inherited class in models; user

RANDOMCHARS = 'xZ(1-)[]'                                   # file characters

# PARAMETERS ------------------------------------------------------------------
# Build dicts of geometric and material parameters
load_params = {
    'R': 12e-3,                                            # specimen radius
    'a': 7.5e-3,                                           # support ring radius
    'p': 5,                                                # points/layer
    'P_a': 1,                                              # applied load
    'r': 2e-4,                                             # radial distance from center loading
}

mat_props = {
    'HA': [5.2e10, 0.25],
    'PSu': [2.7e9, 0.33],
}

# TESTS -----------------------------------------------------------------------

# =============================================================================
# TOOLS -----------------------------------------------------------------------
# =============================================================================


# Laminator -------------------------------------------------------------------
def test_laminator_consistency1():
    '''Check laminator yields same LMFrame as classic case building.'''
    case = ut.laminator(geos=dft.geos_all, ps=[5])
    for case_ in case.values():
        case1 = case_
    case2 = la.distributions.Case(load_params, mat_props)
    case2.apply(dft.geos_all)
    #print(case1)
    #print(case2)
    ##for actual, expected in zip(case1, case2.LMs):
    for actual, expected in zip(case1.LMs, case2.LMs):
        #print(actual)
        #print(expected)
        ut.assertFrameEqual(actual.LMFrame, expected.LMFrame)


@nt.raises(Exception)
def test_lamainator_type1():
    '''Check raises Exception if geos is not a list.'''
    actual = ut.laminator(geos={'400-200-800'})


def test_laminator_type2():
    '''Check defaults to 400-200-800 nothing is passed in.'''
    case1 = ut.laminator(geos=['400-200-800'])
    LM = case1[0]
    actual = LM.frames[0]
    case2 = la.distributions.Case(dft.load_params, dft.mat_props)
    case2.apply(['400-200-800'])
    expected = case2.frames[0]
    ut.assertFrameEqual(actual, expected)


def test_laminator_type3():
    '''Check defaults triggerd if nothing is passed in.'''
    case1 = ut.laminator()
    LM = case1[0]
    actual = LM.frames[0]
    case2 = la.distributions.Case(dft.load_params, dft.mat_props)
    case2.apply(['400-200-800'])
    expected = case2.frames[0]
    ut.assertFrameEqual(actual, expected)


def test_laminator_gencon1():
    '''Check returns a geometry string in General Convention; converts 'S'.'''
    case = ut.laminator(['400-0-400S'])
    for case_ in case.values():
        for LM in case_.LMs:
            actual = ut.get_special_geometry(LM.LMFrame)
            ##expected = '400-[0]-800'                       # pre to_gen_convention()
            expected = '400.0-[0.0]-800.0'
            nt.assert_equal(actual, expected)


# IO Tests -------------------------------------------------------------------
# These tests create temporary files in the OS temp directory.
# Files are removed after testing.
# Attempts to remove remnant files
def test_tool_get_path_default():
    '''Verify returns default export path if no args.'''
    path = ut.get_path()
    actual = path.endswith(os.path.join('lamana', 'export'))
    nt.assert_true(actual)


def test_tool_get_path_name1():
    '''Verify returns path name correctly.'''
    path = ut.get_path(filename=RANDOMCHARS, suffix='.csv')
    actual = path.endswith('.'.join([RANDOMCHARS, 'csv']))
    nt.assert_true(actual)


def test_tool_get_path_name2():
    '''Verify returns path name correctly, for a dashboard; pretend "dash_".'''
    path = ut.get_path(filename=RANDOMCHARS, suffix='.csv', dashboard=True)
    actual1 = path.endswith('.'.join([RANDOMCHARS, 'csv']))
    actual2 = os.path.basename(path).startswith('dash_')
    nt.assert_true(actual1)
    nt.assert_true(actual2)


def test_tool_get_path_name3():
    '''Verify returns path name correctly.'''
    path = ut.get_path(filename=RANDOMCHARS, suffix='.xlsx')
    actual = path.endswith('.'.join([RANDOMCHARS, 'xlsx']))
    nt.assert_true(actual)


def test_tool_get_path_name4():
    '''Verify returns path name correctly, for a dashboard; no "dash_" for xlsx.'''
    # The following should inform dashboards are not separate files.
    path = ut.get_path(filename=RANDOMCHARS, suffix='.xlsx', dashboard=True)
    actual1 = path.endswith('.'.join([RANDOMCHARS, 'xlsx']))
    actual2 = os.path.basename(path).startswith('dash_')
    nt.assert_true(actual1)
    nt.assert_false(actual2)


def test_tool_get_path_name5():
    '''Verify overwrite protected filepath is returned if overwrite is False.'''
    # Just testing that it's triggered; not that it increments.
    path = ut.get_path(filename=RANDOMCHARS, suffix='.xlsx', overwrite=False)
    actual = path.endswith('.'.join([RANDOMCHARS, 'xlsx']))
    nt.assert_true(actual)


def test_tool_get_path_warn1():
    '''Verify correct path for no extension; no suffix kwarg.'''
    path = ut.get_path(filename=RANDOMCHARS)               # should raise a logger warning
    actual = path.endswith(RANDOMCHARS)
    nt.assert_true(actual)


def test_tool_get_path_warn2():
    '''Verify correct path for no filename; uses default path.'''
    actual = ut.get_path(suffix='.csv')                    # should raise a logger warning
    expected = ut.get_path()                               # default path
    nt.assert_equals(actual, expected)


def test_tool_get_path_warn3():
    '''Verify correct path for no filename; uses default path.'''
    actual = ut.get_path(dashboard=True)                   # should raise a logger warning
    expected = ut.get_path()                               # default path
    nt.assert_equals(actual, expected)


class TestExport():
    '''Comprise a sample LaminateModel and FeatureInput to test exported files.'''
    # See Also: Scratchpad - Dashboard.ipynb

    # Setup -------------------------------------------------------------------
    # TODO: Make a Fixture
    case = ut.laminator(dft.geos_standard)[0]
    LM = case.LMs[0]
    FI = LM.FeatureInput

    # Path Munging
    temp_dirpath = tempfile.gettempdir()
    csv_fpath = os.path.join(
        temp_dirpath, 't_laminate_5ply_p5_t2.0_400.0-[200.0]-800.0.csv'
    )
    csv_dash_fpath = os.path.join(
        temp_dirpath, 't_dash_laminate_5ply_p5_t2.0_400.0-[200.0]-800.0.csv'
    )
    xlsx_fpath = os.path.join(
        temp_dirpath, 't_laminate_5ply_p5_t2.0_400.0-[200.0]-800.0.xlsx'
    )

    # Pre-clean directory
    if os.path.exists(csv_fpath):
        os.remove(csv_fpath)
    if os.path.exists(csv_dash_fpath):
        os.remove(csv_dash_fpath)
    if os.path.exists(xlsx_fpath):
        os.remove(xlsx_fpath)

    # Tests -------------------------------------------------------------------
    # .csv files
    # The following use temporary files
    def test_export_csv_temp1(self):
        '''Verify write csv files, unnamed tempfile.'''
        try:
            # Write unnamed tempfiles and see if exists; then remove.
            data_fpath, dash_fpath = ut.export(
                self.LM, overwrite=True, suffix='.csv', temp=True, keepname=False,
                delete=False
            )
            actual1 = os.path.exists(data_fpath)
            actual2 = os.path.exists(dash_fpath)
            nt.assert_true(actual1)
            nt.assert_true(actual2)
        finally:
            os.remove(data_fpath)
            os.remove(dash_fpath)
            logging.info('File has been deleted: {}'.format(data_fpath))
            logging.info('File has been deleted: {}'.format(dash_fpath))

    def test_export_csv_temp2(self):
        '''Verify write csv files; named tempfile.'''
        try:
            # Write named tempfiles, verify, then remove
            data_fpath, dash_fpath = ut.export(
                self.LM, overwrite=True, suffix='.csv', temp=True, keepname=True,
                delete=False
            )
            actual1, actual2 = data_fpath, dash_fpath
            expected1, expected2 = self.csv_fpath, self.csv_dash_fpath
            nt.assert_equals(actual1, expected1)
            nt.assert_equals(actual2, expected2)
        finally:
            os.remove(data_fpath)
            os.remove(dash_fpath)
            logging.info('File has been deleted: {}'.format(data_fpath))
            logging.info('File has been deleted: {}'.format(dash_fpath))

    def test_export_csv_temp_del1(self):
        '''Verify write csv, unnamed tempfile; delete afterwards.'''
        # Write unnamed tempfiles and see if exists; then remove.
        data_fpath, dash_fpath = ut.export(
            self.LM, overwrite=True, suffix='.csv', temp=True, keepname=False,
            delete=True
        )
        actual1 = os.path.exists(data_fpath)
        actual2 = os.path.exists(dash_fpath)
        nt.assert_false(actual1)
        nt.assert_false(actual2)

    def test_export_csv_temp_del2(self):
        '''Verify write csv, named tempfile; delete afterwards.'''
        # Write named tempfiles, verify, then remove
        data_fpath, dash_fpath = ut.export(
            self.LM, overwrite=True, suffix='.csv', temp=True, keepname=True,
            delete=True
        )
        actual1 = os.path.exists(data_fpath)
        actual2 = os.path.exists(dash_fpath)
        nt.assert_false(actual1)
        nt.assert_false(actual2)

    def test_export_csv_temp_increment1(self):
        '''Verify writes incremented csv if same filename found; named tempfile.

        Notes
        -----
        Test the data file, but since dashboards are written, deletes both files.
        Simply sees if incremented file is greater.  If incremented file is empty
        (starting fresh), then ignore loop.

        '''
        fname_list = []
        try:
            baseline = self.csv_fpath
            for i in range(3):
                # Increment filepath after first loop
                data_fpath, dash_fpath = ut.export(
                    self.LM, overwrite=False, prefix=None, suffix='.csv',
                    temp=True, keepname=True, delete=False
                )
                # See differences (should be the increment); assert last number < current
                incremented = data_fpath
                prior_inc = [int(i[2:]) for i in difflib.ndiff(baseline, incremented)
                             if '-' in i and i[2:].isdigit()]
                post_inc = [int(i[2:]) for i in difflib.ndiff(baseline, incremented)
                            if '+' in i and i[2:].isdigit()]
                if prior_inc == []: prior_inc = [0]            # reset prior
                if post_inc:                                   # ignore loop if [], means first loop, and hasn't incremented yet
                    actual = prior_inc[0] < post_inc[0]
                    nt.assert_true(actual)
                baseline = data_fpath

                fname_list.append(data_fpath)
                fname_list.append(dash_fpath)                  # not used by still written, so need cleaning
        finally:
            for fpath in fname_list:
                os.remove(fpath)
                logging.info('File has been deleted: {}'.format(fpath))

    # .xlsx files
    # The following use temporary files
    def test_export_xlsx_temp1(self):
        '''Verify write xslx files, unnamed tempfile.'''
        try:
            # Write unnamed tempfiles and see if exists; then remove.
            workbook_fpath, = ut.export(
                self.LM, overwrite=True, suffix='.xlsx', temp=True, keepname=False,
                delete=False
            )
            actual1 = os.path.exists(workbook_fpath)
            nt.assert_true(actual1)
        finally:
            os.remove(workbook_fpath)
            logging.info('File has been deleted: {}'.format(workbook_fpath))

    def test_export_xlsx_temp2(self):
        '''Verify write xslx files; named tempfile.'''
        try:
            # Write named tempfiles, verify, then remove
            workbook_fpath, = ut.export(
                self.LM, overwrite=True, suffix='.xlsx', temp=True, keepname=True,
                delete=False
            )
            actual1 = workbook_fpath
            expected1 = self.xlsx_fpath
            nt.assert_equals(actual1, expected1)
        finally:
            os.remove(self.xlsx_fpath)
            logging.info('File has been deleted: {}'.format(workbook_fpath))

    def test_export_xlsx_temp_del1(self):
        '''Verify write xslx, unnamed tempfile; delete afterwards.'''
        # Write unnamed tempfiles and see if exists; then remove.
        workbook_fpath, = ut.export(
            self.LM, overwrite=True, suffix='.xlsx', temp=True, keepname=False,
            delete=True
        )
        actual1 = os.path.exists(workbook_fpath)
        nt.assert_false(actual1)

    def test_export_xlsx_temp_del2(self):
        '''Verify write xslx, named tempfile; delete afterwards.'''
        # Write named tempfiles, verify, then remove
        workbook_fpath, = ut.export(
            self.LM, overwrite=True, suffix='.xlsx', temp=True, keepname=True,
            delete=True
        )
        actual1 = os.path.exists(workbook_fpath)
        nt.assert_false(actual1)

    def test_export_xlsx_temp_increment1(self):
        '''Verify writes incremented xslx if same filename found; named tempfile.

        Notes
        -----
        Test the data file, but since dashboards are written, deletes both files.
        Simply sees if incremented file is greater.  If incremented file is empty
        (starting fresh), then ignore loop.

        '''
        fname_list = []
        try:
            baseline = self.xlsx_fpath
            for i in range(3):
                # Increment filepath after first loop
                workbook_fpath, = ut.export(
                    self.LM, overwrite=False, prefix=None, suffix='.xlsx',
                    temp=True, keepname=True, delete=False
                )
                # See differences (should be the increment); assert last number < current
                incremented = workbook_fpath
                prior_inc = [int(i[2:]) for i in difflib.ndiff(baseline, incremented)
                             if '-' in i and i[2:].isdigit()]
                post_inc = [int(i[2:]) for i in difflib.ndiff(baseline, incremented)
                            if '+' in i and i[2:].isdigit()]
                if prior_inc == []: prior_inc = [0]            # reset prior
                if post_inc:                                   # ignore loop if [], means first loop, and hasn't incremented yet
                    actual = prior_inc[0] < post_inc[0]
                    nt.assert_true(actual)
                baseline = workbook_fpath

                fname_list.append(workbook_fpath)
        finally:
            for fpath in fname_list:
                os.remove(fpath)
                logging.info('File has been deleted: {}'.format(fpath))

    def test_export_xlsx_default(self):
        '''Verify default suffix is '.xlsx'.'''
        result = ut.export(self.LM, suffix=None, temp=True, delete=True)
        actual = result[0].endswith('.xlsx')
        nt.assert_true(actual)

    @nt.raises(NotImplementedError)
    def test_export_xlsx_error1(self):
        '''Verify raises error if a directory name is passed in.'''
        # This way for now due to security concerns accidentatly writing to disk.
        ut.export(self.LM, dirpath='dummy', delete=True)


class TestFeatureInputTools:
    '''Comprise test functions to convert and reorder FeatureInputs.'''
    case = ut.laminator(dft.geos_standard)[0]
    LM = case.LMs[0]
    FI = LM.FeatureInput
    converted_FI = ut.convert_featureinput(FI)

    def test_tool_convert_featureinput1(self):
        '''Verify all dict values are DataFrames.'''
        for value in self.converted_FI.values():
            actual = isinstance(value, pd.DataFrame)
            nt.assert_true(actual)

    def test_tool_convert_featureinput2(self):
        '''Verify dict with DataFrame stays unconverted.'''
        dict_frame = {0: pd.DataFrame({'': {'Geometry': '1-2-3'}}, )}
        converted_dict = ut.convert_featureinput(dict_frame)
        for value in converted_dict.values():
            actual = isinstance(value, pd.DataFrame)
            nt.assert_true(actual)

    def test_tool_reorder_featureinput1(self):
        '''Verify default list order if no args given.'''
        for value in self.converted_FI.values():
            reordered_FI = ut.reorder_featureinput(self.FI)
            actual = list(reordered_FI.keys())
            expected = [
                'Geometry', 'Model', 'Materials', 'Parameters', 'Globals',
                'Properties'
            ]
            nt.assert_equals(actual, expected)

    def test_tool_reorder_featureinput2(self):
        '''Verify reorder dict keys if keys given.'''
        for value in self.converted_FI.values():
            rev_keys = reversed(
                ['Geometry', 'Model', 'Materials', 'Parameters', 'Globals',
                 'Properties']
            )
            reordered_FI = ut.reorder_featureinput(self.FI, keys=rev_keys)
            actual = list(reordered_FI.keys())
            expected = [
                'Properties', 'Globals', 'Parameters', 'Materials', 'Model',
                'Geometry'
            ]
            nt.assert_equals(actual, expected)

    def test_tool_reorder_featureinput3(self):
        '''Verify missing keys are added if few args given.'''
        for value in self.converted_FI.values():
            reordered_FI = ut.reorder_featureinput(self.FI, ['Model', 'Geometry'])
            actual = set(reordered_FI.keys())
            expected = set(
                ['Model', 'Geometry', 'Materials', 'Parameters', 'Globals', 'Properties']
            )
            nt.assert_equals(actual, expected)


# # DEPRECATE Following write_csv tests 0.4.11.dev0
# # Write CSV -------------------------------------------------------------------
# def test_tools_write1():
#     '''Check DataFrame is written of csv and read DataFrame is the same.
#
#     Notes
#     -----
#     Builds case(s), pulls the DataFrame, write a temporary csv in the default
#     "export" directory (overwrites if the temporary file exists to keep clean).
#     Then use pandas to read the csv back as a DataFrame.  Finally compare
#     equality between DataFrames, then removes the file.
#
#     DEV: File is removed even if fails to keep the export dir clean.  Comment
#     if debugging required.
#
#     See also
#     --------
#     - test_write2(): overwrite=False; may give unexpected results in tandem
#
#     '''
#     case = ut.laminator(['400-200-800'])
#     try:
#         ##case = ut.laminator(['400-200-800'])
#         # Write files to default output dir
#         for case_ in case.values():
#             for LM in case_.LMs:
#                 expected = LM.LMFrame
#                 filepath = ut.write_csv(LM, overwrite=True, prefix='temp')
#
#                 # Read a file
#                 actual = pd.read_csv(filepath, index_col=0)
#                 ut.assertFrameEqual(actual, expected)
#     finally:
#         # Remove temporary file
#         os.remove(filepath)
#         #pass
#
#
# def test_tools_write2():
#     '''Check if overwrite=False retains files.
#
#     Notes
#     -----
#     Make two files of the same name.  Force write_csv to increment files.
#     Check the filepath names exist.  Finally remove all files.
#
#     DEV: Files are removed even if fails to keep the export dir clean.  Comment
#     if debugging required.
#
#     '''
#     case = ut.laminator(['400-200-800', '400-200-800'])
#     filepaths = []
#     try:
#         ##case = ut.laminator(['400-200-800', '400-200-800'])
#         # Write files to default output dir
#         ##filepaths = []
#         for case_ in case.values():
#             for LM in case_.LMs:
#                 #filepath = ut.write_csv(LM, overwrite=False, verbose=True, prefix='temp')
#                 filepath = ut.write_csv(LM, overwrite=False, prefix='temp')
#                 filepaths.append(filepath)
#
#         for file_ in filepaths:
#             actual = os.path.isfile(file_)
#             nt.assert_true(actual)
#
#     finally:
#         # Remove temporary file
#         for file_ in filepaths:
#             os.remove(file_)
#
#
# # Read CSV --------------------------------------------------------------------
# # TODO: add modified write file
# # BUG: seems temps aren't deleting if non-csv file exists in export folder
# def test_tools_read1():
#     '''Checks reads file when case items are written to files.'''
#     case = ut.laminator(['400-200-800', '400-[100,100]-800'])
#     written_filepaths = []
#     d = ct.defaultdict(list)
#     try:
#         ##case = ut.laminator(['400-200-800', '400-[100,100]-800'])
#
#         # Expected: Write LaminateModels
#         # Make files in a default export dir, and catch expected dfs
#         list_l = []
#         for case_ in case.values():
#             for LM in case_.LMs:
#                 df_l = LM.LMFrame
#                 filepath_l = ut.write_csv(LM, overwrite=False, prefix='temp')
#                 list_l.append((df_l, filepath_l))
#                 logging.info('File path {}'.format(filepath_l))
#
#         # Actual: Read Files
#         # Get dirpath from last filepath_l; assumes default path structure from write_csv
#         dirpath = os.path.dirname(filepath_l)
#         gen_r = ut.read_csv_dir(dirpath)                   # yields (file, filepath)
#
#         # Use a defaultdict to place same dfs with matching paths
#         # {'...\filename': [df_l, df_r]}
#         ##d = ct.defaultdict(list)
#         for df_l, filepath_l in list_l:
#             d[filepath_l].append(df_l)
#
#         for df_r, filepath_r in gen_r:
#             d[filepath_r].append(df_r)
#
#         # If files are already present in export dir, the # write files < # read files
#         # Need to filter the dict entries that don't have both read and write (left-right) values
#         # Only need to iterate over keys for the written files i.e. filepath_l
#         written_filepaths = [path for df, path in list_l]
#
#         # Verify Equivalence
#         # Compare DataFrames sharing the same pathname (ensure correct file for left and right)
#         for k, v in d.items():
#             filename = k
#             if filename in written_filepaths:
#                 expected, actual = v
#                 #print(filename)
#                 #print(expected.info)
#                 ut.assertFrameEqual(actual, expected)
#
#     # Cleanup
#     # Only remove the written temporary files
#     finally:
#         for file_ in d:
#             if file_ in written_filepaths:
#                 print('Cleaning up temporary files ...')
#                 os.remove(file_)


# Extract geo_strings ---------------------------------------------------------
def test_getmultigeo1():
    '''Check strings are extracted from a "multi" laminate Frame, nplies >= 5.'''
    case = ut.laminator(['400-200-800'])
    for case_ in case.values():
        for LM in case_.LMs:
            actual = ut.get_multi_geometry(LM.LMFrame)
            #expected = '400-[200]-800'                       # pre to_gen_convention()
            expected = '400.0-[200.0]-800.0'
            nt.assert_equal(actual, expected)


@nt.raises(Exception)
def test_getmultigeo2():
    '''Check error is raised if not "multi", rather a special, nplies < 4.'''
    case = ut.laminator(['400-200-0'])
    for case_ in case.values():
        for LM in case_.LMs:
            actual = ut.get_multi_geometry(LM.LMFrame)


def test_getspecialgeo1():
    '''Check strings are extracted from a special laminate Frame, nplies <= 4.'''
    case = ut.laminator(['400-200-0'])
    for case_ in case.values():
        for LM in case_.LMs:
            actual = ut.get_special_geometry(LM.LMFrame)
            ##expected = '400-[200]-0'                       # pre to_gen_convention()
            expected = '400.0-[200.0]-0.0'
            nt.assert_equal(actual, expected)


@nt.raises(Exception)
def test_getspecialgeo2():
    '''Check error is raised if not special, nplies > 4.'''
    case = ut.laminator(['400-200-800'])
    for case_ in case.values():
        for LM in case_.LMs:
            actual = ut.get_special_geometry(LM.LMFrame)


# Sets ------------------------------------------------------------------------
def test_compare_subset():
    '''Check the comparison of subsets.'''
    # Subset: [1,2] < [1,2,3] -> True; [1,2] <= [1,2] -> True
    it = [[1, 2], [1, 2], [1, 2]]
    others = [[1, 2, 3], [1, 2], [3, 4]]

    actual = []
    for i, o in zip(it, others):
        result = ut.compare_set(i, o, how='union', test='issubset')
        actual.append(result)
    expected = [True, True, False]
    nt.assert_equal(actual, expected)


def test_compare_superset():
    '''Check the comparison of supersets.'''
    # Superset: [1,2,3] > [1,2] -> True; [1,2,3] >= [1,2,3] -> True
    it = [[1, 2, 3], [1, 2, 3], [1, 2]]
    others = [[1, 2], [1, 2, 3], [3, 4]]

    actual = []
    for i, o in zip(it, others):
        result = ut.compare_set(i, o, how='union', test='issuperset')
        actual.append(result)
    expected = [True, True, False]
    nt.assert_equal(actual, expected)


def test_compare_disjoint():
    '''Check the comparison of dijoints.'''
    # Superset: [1,2,3] > [1,2] -> True; [1,2,3] >= [1,2,3] -> True
    it = [[1, 2]]
    others = [[3, 4]]

    actual = []
    for i, o in zip(it, others):
        result = ut.compare_set(i, o, how='union', test='isdisjoint')
        actual.append(result)
    expected = [True]
    nt.assert_equal(actual, expected)


def test_compare_union():
    '''Check set union.'''
    # Union: [1,2] | [3,4] -> {1,2,3,4}
    it = [[1, 2]]
    others = [[3, 4]]

    actual = []
    for i, o in zip(it, others):
        result = ut.compare_set(i, o, how='union')
        actual.append(result)
    expected = [{1, 2, 3, 4}]
    nt.assert_equal(actual, expected)


def test_compare_intersection():
    '''Check set intersection.'''
    # Intersection: [1] & [1,2] -> {1}
    it = [[1]]
    others = [[1, 2]]

    actual = []
    for i, o in zip(it, others):
        result = ut.compare_set(i, o, how='intersection')
        actual.append(result)
    expected = [{1}]
    nt.assert_equal(actual, expected)


def test_compare_difference():
    '''Check set difference.'''
    # Difference: [1,2,3] - [3,4] -> {1,2}
    it = [[1, 2, 3]]
    others = [[3, 4]]

    actual = []
    for i, o in zip(it, others):
        result = ut.compare_set(i, o, how='difference')
        actual.append(result)
    expected = [{1, 2}]
    nt.assert_equal(actual, expected)


def test_compare_symmetric():
    '''Check set symmetric difference.'''
    # Symmetric Difference: [1,2,3] ^ [3,4] -> {1,2,4}
    it = [[1, 2, 3]]
    others = [[3, 4]]

    actual = []
    for i, o in zip(it, others):
        result = ut.compare_set(i, o, how='symmetric difference')
        actual.append(result)
    expected = [{1, 2, 4}]
    nt.assert_equal(actual, expected)


def test_compare_iterables():
    '''Check set comparison works if given non-iterables e.g. int.'''
    # Symmetric Difference: [1,2,3] ^ [3,4] -> {1,2,4}
    actual1 = ut.compare_set(1, [2, 3], how='union')       # it is int
    actual2 = ut.compare_set([1, 2], 3, how='union')       # other is int
    expected = {1, 2, 3}
    nt.assert_equal(actual1, expected)
    nt.assert_equal(actual2, expected)


# Pandas Object Comparisons ---------------------------------------------------
class TestPandasComparisions():
    '''Check basic assertions for helper functions comparings Series and DataFrames.'''
    # Build DataFrames
    df_data1 = {'apple': 4, 'orange': 3, 'banana': 2, 'blueberry': 3}
    df_data2 = {'apple': 4, 'orange': 3, 'banana': 2, 'blueberry': 3}
    df_data3 = {'apple': 4, 'strawberry': 3, 'orange': 3, 'banana': 2}

    df1 = pd.DataFrame(df_data1, index=['amount'])
    df2 = pd.DataFrame(df_data2, index=['amount'])
    df3 = pd.DataFrame(df_data3, index=['amount'])

    # Build Series
    s_data1 = {'apple': 4, 'orange': 3, 'banana': 2, 'blueberry': 3}
    s_data2 = {'apple': 4, 'orange': 3, 'banana': 2, 'blueberry': 3}
    s_data3 = {'apple': 4, 'strawberry': 3, 'orange': 3, 'banana': 2}

    s1 = pd.Series(s_data1)
    s2 = pd.Series(s_data2)
    s3 = pd.Series(s_data3)

    # Test assertFrameEqual
    def test_assertframeeq1(self):
        '''Check helper function compares DataFrames, None.'''
        # See https://github.com/pydata/pandas/blob/master/pandas/util/testing.py
        actual = ut.assertFrameEqual(self.df1, self.df2)
        expected = None
        nt.assert_equal(actual, expected)

    @nt.raises(AssertionError)
    def test_assertframeeq2(self):
        '''Check helper function compares DataFrames, raises error is not equal.'''
        actual = ut.assertFrameEqual(self.df1, self.df3)

    # Test assertSeriesEqual
    def test_assertserieseq1(self):
        '''Check helper function compares Series, None.'''
        # See https://github.com/pydata/pandas/blob/master/pandas/util/testing.py
        actual = ut.assertSeriesEqual(self.s1, self.s2)
        expected = None
        nt.assert_equal(actual, expected)

    @nt.raises(AssertionError)
    def test_assertserieseq2(self):
        '''Check helper function compares Series, raises error is not equal.'''
        actual = ut.assertSeriesEqual(self.s1, self.s3)

    # Test ndframe_equal
    def test_ndframeeq_DataFrame1(self):
        '''Check helper function compares DataFrames, True.'''
        actual = ut.ndframe_equal(self.df1, self.df2)
        expected = True
        nt.assert_equal(actual, expected)

    def test_ndframeeq_DataFrame2(self):
        '''Check helper function compares DataFrames, False.'''
        actual = ut.ndframe_equal(self.df1, self.df3)
        expected = False
        nt.assert_equal(actual, expected)

    def test_ndframeeq_Series1(self):
        '''Check helper function compares Series, True.'''
        actual = ut.ndframe_equal(self.s1, self.s2)
        expected = True
        nt.assert_equal(actual, expected)

    def test_ndframeeq_Series2(self):
        '''Check helper function compares Series, False.'''
        actual = ut.ndframe_equal(self.s1, self.s3)
        expected = False
        nt.assert_equal(actual, expected)


# Matching Brackets -----------------------------------------------------------
def test_ismatched1():
    '''Check matching pair of brackets or parentheses returns True.'''
    s1 = 'Here the [brackets] are matched.'
    s2 = 'Here the (parentheses) are matched.'
    actual1 = ut.is_matched(s1)
    actual2 = ut.is_matched(s2)
    expected = True
    nt.assert_equal(actual1, expected)
    nt.assert_equal(actual2, expected)


def test_ismatched2():
    '''Check non-matching pair of brackets brackets or parentheses returns False.'''
    s1 = 'Here the [brackets][ are NOT matched.'
    s2 = 'Here the ((parentheses) are NOT matched.'
    actual1 = ut.is_matched(s1)
    actual2 = ut.is_matched(s2)
    expected = False
    nt.assert_equal(actual1, expected)
    nt.assert_equal(actual2, expected)


def test_ismatched3():
    '''Check non-matching pair of brackets brackets or parentheses returns False.'''
    s1 = 'Only accept [letters] in brackets that are [CAPITALIZED[.'
    s2 = 'Only accept (letters) in parentheses that are ((CAPITALIZED(.'
    p = '\W[A-Z]+\W'                                       # regex for all only capital letters and non-alphannumerics
    actual1 = ut.is_matched(s1, p)
    actual2 = ut.is_matched(s2, p)
    expected = False
    nt.assert_equal(actual1, expected)
    nt.assert_equal(actual2, expected)


# TODO: How to access the counting branches in ismatched()?
#def test_ismatched_count1():
#    '''Check parens and brakets are counted.'''
#    s1 = '[[][]]]'
#    s2 = '()))()))'
#    actual1 = ut.is_matched(s1)
#    actual2 = ut.ismatched(s2)
#    actual3 = ut.ismatched(''.join(s1, s2))
#    # (bra, ket, par, ren)
#    expected1 = (3, 4, 0, 0)
#    expected1 = (0, 0, 2, 6)
#    expected3 = (3, 4, 2, 6)
#    nt.assert_equal(actual1, expected1)
#    nt.assert_equal(actual2, expected2)
#    nt.assert_equal(actual3, expected3)


# Sort DataFrame Columns ------------------------------------------------------
# TODO: Make a test class to combine DataFrame builds; see TestPandasComparisions
def test_set_columns_seq1():
    '''Check reorders columns to existing sequence.'''
    # Pandas orders DataFrame columns alphabetically
    data = {'apple': 4, 'orange': 3, 'banana': 2, 'blueberry': 3}
    df = pd.DataFrame(data, index=['amount'])
    # apple  banana  blueberry  orange

    # We can resequence the columns
    seq = ['apple', 'orange', 'banana', 'blueberry']
    actual = ut.set_column_sequence(df, seq)
    expected = pd.DataFrame(data, index=['amount'], columns=seq)
    ut.assertFrameEqual(actual, expected)


def test_set_columns_seq2():
    '''Check reorders columns and adds columns not in sequence to the end.'''
    data = {'apple': 4, 'strawberry': 3, 'orange': 3, 'banana': 2}
    df = pd.DataFrame(data, index=['amount'])

    # Excluded names are appended to the end of the DataFrame
    seq = ['apple', 'strawberry']
    # apple  strawberry banana  orange
    actual = ut.set_column_sequence(df, seq)
    expected = pd.DataFrame(data, index=['amount'],
                            columns=['apple', 'strawberry', 'banana', 'orange'])
    ut.assertFrameEqual(actual, expected)


# Natural Sort ----------------------------------------------------------------
def test_natural_sort1():
    '''Check natural sorting of keys in a dict; keys are passed in from the dict.'''
    dict_ = {'3-ply': None, '1-ply': None, '10-ply': None, '2-ply': None}
    # actual = [k for k, v in sorted(dict_(), key=natural_sort)]    # equivalent
    actual = [k for k in sorted(dict_.keys(), key=ut.natural_sort)]
    expected = ['1-ply', '2-ply', '3-ply', '10-ply']
    nt.assert_equal(actual, expected)


def test_natural_sort2():
    '''Check natural sorting of keys from tuples; key-value pairs are passed in from the dict.'''
    dict_ = {'3-ply': None, '1-ply': None, '10-ply': None, '2-ply': None}
    actual = [k for k in sorted(dict_.items(), key=ut.natural_sort)]
    expected = [('1-ply', None), ('2-ply', None), ('3-ply', None), ('10-ply', None)]
    nt.assert_equal(actual, expected)


def test_natural_sort3():
    '''Check if non-digits are in keys.'''
    dict_ = {'3-ply': None, 'foo-ply': None, '10-ply': None, '2-ply': None}
    # actual = [k for k, v in sorted(dict_(), key=natural_sort)]    # equivalent
    actual = [k for k in sorted(dict_.keys(), key=ut.natural_sort)]
    expected = ['2-ply', '3-ply', '10-ply', 'foo-ply']
    nt.assert_equal(actual, expected)


def test_utils_tools_withmeta1():
    '''Verify the meta class is equivalent to python version variations.'''
    class MyClassC(ut.with_metaclass(abc.ABCMeta)):
        pass

    if sys.version_info < (3,):
        class MyClassA(object):
            __metaclass__ = abc.ABCMeta
            pass
        nt.assert_is(type(MyClassA), type(MyClassC))

#     elif sys.version_info >= (3,):
#         class MyClassB(metaclass=abc.ABCMeta):
#             pass                                             # can't run in python 2
#         nt.assert_is(type(MyClassB), type(MyClassC))


# Inspection and Hooks --------------------------------------------------------
# Favored class tests for scoping
# Using psudeo "fixtures" to mock bad models for trigger errors
class TestInspectionTools:
    '''Verify inspection tools are covered.

    This class uses "fixtures" with sample models to test importing.

    '''
    class Parent(object):
        def method():
            pass
        pass

    class Child1(Parent):
        '''Inherits a method'''
        pass

    class Child2():
        '''No methods.'''
        pass

    def test_utils_tools_inspection_isparent1(self):
        '''Verify class is a parent.'''
        actual1 = ut.isparent(self.Parent)
        actual2 = ut.isparent(self.Child1)
        nt.assert_true(actual1)
        nt.assert_false(actual2)

    def test_utils_tools_inspection_findclasses1(self):
        '''Verify classes are present is class-style model; not function-style.'''
        actual1 = len(ut.find_classes(fixture_model_class)) >= 1
        actual2 = len(ut.find_classes(fixture_model_func)) >= 1
        nt.assert_true(actual1)
        nt.assert_false(actual2)

    def test_utils_tools_inspection_findmethods1(self):
        '''Verify methods are found in classes.'''
        actual1 = len(ut.find_methods(self.Parent)) >= 1
        actual2 = len(ut.find_methods(self.Child1)) >= 1
        actual3 = len(ut.find_methods(self.Child2)) >= 1
        nt.assert_true(actual1)
        nt.assert_true(actual2)
        nt.assert_false(actual3)

    def test_utils_tools_inspection_findfunctons1(self):
        '''Verify functions are present is function-style model; not class-style.'''
        actual1 = len(ut.find_functions(fixture_model_func)) >= 1
        actual2 = len(ut.find_functions(fixture_model_class)) >= 1
        nt.assert_true(actual1)
        nt.assert_false(actual2)


class TestHookTools:
    '''Verify hook tools operate correctly.

    This class uses "fixtures" with sample models to test importing.

    '''
    # TODO: Remove
    hookname = config.HOOKNAME

    hook_func_module = fixture_model_func
    hook_class_module = fixture_model_class
    non_hook_module = fixture_model_module_a
    many_hook_module = fixture_model_module_b

    @nt.raises(AttributeError)
    def test_utils_tools_gethookfunction_error1(self):
        '''Verify raise error if no hook function found.'''
        # Assumes no hook functions in the fixture containing hook classes
        actual = ut.get_hook_function(self.hook_class_module, self.hookname)

    @nt.raises(AttributeError)
    def test_utils_tools_gethookclass_error1(self):
        '''Verify raise error if no hook class found.'''
        # Assumes no hook classes in the fixture containing hook functions
        actual = ut.get_hook_class(self.hook_func_module, self.hookname)

    @nt.raises(AttributeError)
    def test_utils_tools_gethookclass_error2(self):
        '''Verify raise error if no hook class found.'''
        # Assumes no hook classes in the fixture containing hook functions
        actual = ut.get_hook_class(self.non_hook_module, self.hookname)

    @nt.raises(AttributeError)
    def test_utils_tools_gethookclass_error3(self):
        '''Verify raise error if too many hooks classes found.'''
        # Assumes no hook classes in the fixture containing hook functions
        actual = ut.get_hook_class(self.many_hook_module, self.hookname)
