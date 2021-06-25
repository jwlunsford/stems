from data.db import dal, RegCoeff, SegCoeff, StemProfileModel
from stems import (lookup_reg_params,
                   lookup_seg_params,
                   calc_d17,
                   calc_dStem,
                   get_model_params)
import pytest


@pytest.fixture
def session():
    dal.connect()
    session = dal.Session()
    return session

@pytest.fixture
def model():
    model = StemProfileModel()
    return model


# tests
def test_lookup_reg_params(session, model):
    get_model_params(session, model)
    assert model.reg_params['reg_a'] != 0.0

def test_lookup_seg_params(session, model):
    get_model_params(session, model)
    assert model.seg_params['butt_r'] != 0.0

def test_calc_d17(session, model):
    get_model_params(session, model)
    assert calc_d17(model) != 0.0

def test_calc_dStem(session, model):
    assert calc_dStem(session, model) >= 0.0

def test_calc_dbh_insideBark(model):
    assert calc_dbh_insideBark(model) >= 0.0

