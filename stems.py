# imports
from data.db import dal, RegCoeff, SegCoeff, StemProfileModel


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
    reg = lookup_reg_params(session, model)

    # get the segment parameters
    seg = lookup_seg_params(session, model)

    # calculate diameter at 17.3 feet
    dia17 = calc_dia17(model, reg)






def calc_dia17(model, reg_params):
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
        return 0.0


def lookup_reg_params(session, model):
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


def lookup_seg_params(session, model):
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
    session = dal.Session()

    spm = StemProfileModel()
    params = lookup_reg_params(session, spm)
    params2 = lookup_seg_params(session, spm)
    print(spm)
    print(params)
    print(params2)
    print(calc_dia17(spm, params))

    session.close()


if __name__ == '__main__':
    main()
