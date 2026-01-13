import os

import pandas as pd

from src.reports import save_report


@save_report()
def df_func():
    return pd.DataFrame([{"a": 1}])


def test_save_report_no_filename():
    result = df_func()
    assert os.path.exists("data/df_func_report.json")
    os.remove("data/df_func_report.json")


@save_report("test_name")
def func_with_df():
    return pd.DataFrame([{"b": 2}])


def test_save_report_with_filename():
    result = func_with_df()
    assert os.path.exists("data/test_name_report.json")
    os.remove("data/test_name_report.json")


@save_report()
def func_no_df():
    return "not df"


def test_save_report_no_df():
    result = func_no_df()
    assert not os.path.exists("data/func_no_df_report.json")
    assert isinstance(result, str)
