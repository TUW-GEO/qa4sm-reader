# -*- coding: utf-8 -*-

from src.qa4sm_reader.img import QA4SMImg
import os
import numpy as np
import unittest
from src.qa4sm_reader import globals

class TestQA4SMImgBasicIntercomp(unittest.TestCase):

    def setUp(self) -> None:
        self.testfile = '3-ERA5_LAND.swvl1_with_1-C3S.sm_with_2-SMOS.Soil_Moisture.nc'
        self.testfile_path = os.path.join(os.path.dirname(__file__), '..','tests',
                                          'test_data', 'basic', self.testfile)
        self.img = QA4SMImg(self.testfile_path, ignore_empty=False)

    def test_parse_filename(self):
        print('test_parse_filename')
        ds_and_vars = self.img.parse_filename()
        assert ds_and_vars['i_ref'] == 3
        assert ds_and_vars['i_ds1'] == 1
        assert ds_and_vars['i_ds2'] == 2
        assert ds_and_vars['ref'] == 'ERA5_LAND'
        assert ds_and_vars['ds1'] == 'C3S'
        assert ds_and_vars['ds2'] == 'SMOS'

    def test_metrics_in_file(self):
        m_groups = self.img.ls_metrics(as_groups=True)
        assert m_groups['common'] == globals.metric_groups[0]
        for m in m_groups['double']:  # tau is not in the results
            assert m in globals.metric_groups[2]
        assert m_groups['triple'] == []  #  this is not the TC test case

        # with merged return value
        ms = self.img.ls_metrics(as_groups=False)
        for m in ms:
            assert any([m in l for l in list(globals.metric_groups.values())])

    def test_vars_in_file(self):
        print('test_vars_in_file')
        vars = self.img.ls_vars()
        vars_should = ['n_obs']
        for metric in globals.metric_groups[2]:
            vars_should.append('{}_between_3-ERA5_LAND_and_1-C3S'.format(metric))
            vars_should.append('{}_between_3-ERA5_LAND_and_2-SMOS'.format(metric))
        vars_should = np.sort(np.array(vars_should))
        assert all(vars == vars_should)
        vars = self.img.ls_vars()
        assert len(vars) <= len(vars_should)


    def test_find_group(self):
        double_group = self.img.find_group('R')
        assert 'R' in double_group and len(double_group['R']) == 2
        assert 'mse' in double_group and len(double_group['mse']) == 2
        assert 'RSS' in double_group and len(double_group['RSS']) == 2
        assert 'rho' in double_group and len(double_group['rho']) == 2
        assert 'BIAS' in double_group and len(double_group['BIAS']) == 2
        assert 'p_R' in double_group and len(double_group['p_R']) == 2
        common_group = self.img.find_group('n_obs')
        assert list(common_group.keys()) == ['n_obs']

        also_double_group = self.img.find_group('R_between_3-ERA5_LAND_and_1-C3S')
        assert double_group == also_double_group

        assert self.img.triple == {}

    def test_metric_meta(self):
        r_meta = self.img.metric_meta('R')
        for var, meta in r_meta.items():
            assert var.split('_between_')[0] == 'R'
            assert len(meta) == 3 # ref, dss, mds
            ref_meta = meta[0][1]
            assert ref_meta['short_name'] == 'ERA5_LAND'
            assert ref_meta['pretty_name'] == 'ERA5-Land'
            assert len(meta[1]) == 1
            assert meta[2] is None
        obs_meta = self.img.metric_meta('n_obs')
        assert obs_meta['n_obs'][0] == obs_meta['n_obs'][1] == \
               obs_meta['n_obs'][2] == None

    def test_ref_meta(self):
        ref_meta = self.img.ref_meta()
        assert len(ref_meta) == 2
        assert ref_meta[0] == 3
        ref_meta = ref_meta[1]
        assert ref_meta['short_name'] == 'ERA5_LAND'
        assert ref_meta['pretty_name'] == 'ERA5-Land'

    def test_var_meta(self):
        meta = self.img.var_meta('n_obs')
        assert list(meta.keys()) == ['n_obs']
        meta = meta['n_obs']
        assert meta == (None, None, None)

        meta = self.img.var_meta('R_between_3-ERA5_LAND_and_1-C3S')
        assert list(meta.keys()) == ['R']
        meta = meta['R']

        ref_meta = meta[0][1]
        assert ref_meta['short_name'] == 'ERA5_LAND'
        assert ref_meta['pretty_name'] == 'ERA5-Land'
        assert ref_meta['pretty_version'] == 'v20190904'

        ds_meta = meta[1][0][1]
        assert ds_meta['short_name'] == 'C3S'
        assert ds_meta['pretty_name'] == 'C3S'
        assert ds_meta['pretty_version'] == 'v201812'



if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(TestQA4SMImgBasicIntercomp("test_var_meta"))
    runner = unittest.TextTestRunner()
    runner.run(suite)
