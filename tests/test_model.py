from data.db import Session, RegCoeff, SegCoeff
from stems import StemProfileModel
import pytest


@pytest.fixture
def model_default():
    with Session() as session:
        model = StemProfileModel()
        model.fetch_params(session)
    return model

@pytest.fixture
def model_outside():
    with Session() as session:
        model = StemProfileModel(bark=0)
        model.fetch_params(session)
    return model

@pytest.fixture
def model_invalid_spp():
    with Session() as session:
        model = StemProfileModel(spp="Holly")
        model.fetch_params(session)
    return model

@pytest.fixture
def model_invalid_bark():
    with Session() as session:
        model = StemProfileModel(bark=3)
        model.fetch_params(session)
    return model

@pytest.fixture
def model_invalid_region():
    with Session() as session:
        model = StemProfileModel(region="West Coast")
        model.fetch_params(session)
    return model

# tests
def test_init_reg_params(model_default):
    # check if reg parameters were fetched and stored correctly
    assert isinstance(model_default.reg_dict, dict)

def test_init_seg_params(model_default):
    # check if seg parameters were fetched and stored correctly
    assert isinstance(model_default.seg_dict, dict)

def test_init_wt_params(model_default):
    # check if wt params were fetched and stored correctly
    assert isinstance(model_default.wt_dict, dict)

def test_stem_diameter_lt_dbh_using_default(model_default):
    # stem diameter at 5ft should be less than dbh
    d = model_default.estimate_stemDiameter(h=5)
    assert d < model_default.dbh

def test_stem_diameter_lt_dbh_using_outside_bark(model_outside):
    # stem diameter at 5ft should be sligthly less than dbh outside bark
    d = model_outside.estimate_stemDiameter(h=5)
    assert d < model_outside.dbh

def test_dbh_insideBark_lt_dbh(model_default):
    # _dbh_insideBark should return a value less than dbh
    d = model_default._dbh_insideBark()
    assert d < model_default.dbh

def test_dia_atGirard_lt_dbh(model_outside):
    # _dia_atGirard should retrun a value less than dbh
    d = model_outside._dia_atGirard()
    assert d < model_outside.dbh

def test_dia_atGirard_equals(model_default):
    # default model diameter at Girard should be 13.15
    d = model_default._dia_atGirard()
    assert d == 13.15

def test_stem_diameter_equals(model_default):
    # default model diameter at stem height 50ft should be 9.80 or 9.8
    d = model_default.estimate_stemDiameter(h=50)
    assert d == 9.80

def test_stem_height_equals(model_default):
    # default model stem height at 9.8in should be 50ft.  This is the inverse
    # of the above test_stem_diameter_equals()
    d = model_default.estimate_stemHeight(d=9.8)
    assert d == 50.0

def test_invalid_spp(model_invalid_spp):
    # invalid spp parameter should return None for seg_dict, and reg_dict
    assert model_invalid_spp.seg_dict == None
    assert model_invalid_spp.reg_dict == None
    assert model_invalid_spp.wt_dict != None

def test_invalid_bark(model_invalid_bark):
    # invalid bark parameter should return None for seg_dict and reg_dict
    assert model_invalid_bark.seg_dict == None
    assert model_invalid_bark.reg_dict == None
    assert model_invalid_bark.wt_dict != None

def test_invalid_region(model_invalid_region):
    # invalid region parameter should return None for reg_dict
    assert model_invalid_region.seg_dict != None
    assert model_invalid_region.reg_dict == None
    assert model_invalid_region.wt_dict != None








