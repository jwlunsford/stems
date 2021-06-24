''' main.py:  connect to the database'''

# imports
from data.db import dal, RegCoeff, SegCoeff


class StemProfileModel:
    ''' represents an instance of a stem profile model'''

    def __init__(self, region='deep south', spp='loblolly pine',
                 dbh=14.0, height=80.0, bark=1):
        self.region = region
        self.spp = spp
        self.dbh = dbh
        self.height = height
        self.bark = bark


    def __repr__(self):
        return f'< StemProfileModel(region="{self.region}", spp="{self.spp}", dbh={self.dbh}, height={self.height}, bark={self.bark})'




def calc_stem_dia(session, model):
    '''
    calculates stem diameter for the height given.  Uses Eq. 1 from Source[1]

    Parameters
    ----------
      model: StemProfileModel object instance

    Returns
    -------
      float, stem diameter at given height

    Sources
    -------
    [1] Clark, A. III, et al. Stem Profile Equations for Southern Tree Speices
    '''

    # get the regression parameters
    reg = get_regcoeff_params(session, model)

    # get the segment parameters
    seg = get_segcoeff_params(session, model)

    # calculate diameter at 17.3 feet
    dia17 = calc_dia_17(model, reg)






def calc_dia_17(model, reg_params):
    '''
    estimate stem diameter at 17.3 feet.  Uses Eq. 10 from Source [1]

    Parameters
    ----------
      model: StemProfileModel instance
      reg_params: dict, regression parameter values

    Returns
    -------
      float, stem diameter at 17.3 feet

    Sources
    -------
    [1] Clark, A. III, et al. Stem Profile Equations for Southern Tree Speices
    '''
    try:
        # calculate diameter at 17.3ft
        result = model.dbh * (reg_params['reg_a'] +
                              reg_params['reg_b'] *
                              (17.3 / model.height) ** 2)
        return round(result, 2)
    except:
        return 0.00


def get_regcoeff_params(session, model):
    '''
    queries the database to retrieve the Regression Coefficients for
    the model.

    Parameters
    ----------
      session:  SQLAlchemy session object
      model: StemProfileModel object

    Returns
    -------
      dictionary of regression parameters
    '''
    try:
        # dict to store output
        output = {}

        # query database
        result = session.query(RegCoeff).filter(
                    RegCoeff.region == model.region,
                    RegCoeff.spp == model.spp,
                    RegCoeff.bark == model.bark).first()

        # add the output to the dict
        output['reg_a'] = result.reg_a
        output['reg_b'] = result.reg_b
        return output

    except:
        # on error set params to 0.0
        output['reg_a'] = 0.0
        output['reg_b'] = 0.0
        return output


def get_segcoeff_params(session, model):
    '''
    queries the database to retrieve the Segment Coefficients for
    the model.

    Parameters
    ----------
      session: SQLAlchemy session object
      model: StemProfileModel object

    Returns
    -------
      dictionary of stem parameters
    '''
    try:
        # dict to store output
        output = {}

        # query database
        result = session.query(SegCoeff).filter(SegCoeff.bark == model.bark,
                                        SegCoeff.spp == model.spp).first()

        # add the ouput to the dict
        output['butt_r'] = result.butt_r
        output['butt_c'] = result.butt_c
        output['butt_e'] = result.butt_e
        output['lstem_p'] = result.lstem_p
        output['ustem_b'] = result.ustem_b
        output['ustem_a'] = result.ustem_a

        return output

    except:
        # on error set all params to 0.0
        output['butt_r'] = 0.0
        output['butt_c'] = 0.0
        output['butt_e'] = 0.0
        output['lstem_p'] = 0.0
        output['ustem_b'] = 0.0
        output['ustem_a'] = 0.0

        return output



def main():
    dal.connect()
    dal.session = dal.Session()

    spm = StemProfileModel()
    params = get_regcoeff_params(dal.session, spm)
    params2 = get_segcoeff_params(dal.session, spm)
    print(spm)
    print(params)
    print(params2)
    print(calc_dia_17(spm, params))

    dal.session.close()


if __name__ == '__main__':
    main()
