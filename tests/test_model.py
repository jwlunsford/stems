from data.db import dal, RegCoeff, SegCoeff, StemProfileModel
from main import lookup_reg_params, lookup_seg_params, calc_dia17
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
    params = lookup_reg_params(session, model)
    assert params['reg_a'] != 0.0

def test_lookup_seg_params(session, model):
    params = lookup_seg_params(session, model)
    assert params['butt_r'] != 0.0

def test_calc_dia17(session, model):
    params = lookup_reg_params(session, model)
    assert calc_dia17(model, params) != 0.0
