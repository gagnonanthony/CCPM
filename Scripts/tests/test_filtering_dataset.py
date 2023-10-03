#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import tempfile

from typer.testing import CliRunner

from CCPM.io.download import get_home, download_data, save_files_dict
from Scripts.CCPM_filtering_dataset import app

download_data(save_files_dict(), keys=['data.zip'])
tmp_dir = tempfile.TemporaryDirectory()

runner = CliRunner()


def test_help():
    ret = runner.invoke(app, ['--help'])

    assert ret.exit_code == 0


def test_execution_filtering():
    os.chdir(os.path.expanduser(tmp_dir.name))
    in_dataset = os.path.join(get_home(), 'data/data_example.xlsx')
    out_folder = os.path.join(get_home(), 'data/Filtering/')

    ret = runner.invoke(app, ['--out-folder', out_folder, '--in-dataset', in_dataset,
                              '--desc-columns', 1, '--id-column', 'subjectkey',
                              '-f'])

    assert ret.exit_code == 0
