# imports
from data.db import dal, RegCoeff, SegCoeff

class StemProfileModel:
    ''' represents an instance of a stem profile model'''

    def __init__(self, region='deep south', spp='loblolly pine',
                 dbh=16.0, height=90.0, bark=1, param_flag=None):
        self.region = region
        self.spp = spp
        self.dbh = dbh
        self.height = height
        self.bark = bark
        self.param_flag = param_flag


    def __repr__(self):
        return f'< StemProfileModel(region="{self.region}", spp="{self.spp}", dbh={self.dbh}, height={self.height}, bark={self.bark}, param_flag={self.param_flag})'


def get_model_params(session, model):
    '''
    Lookup model params and store them with the model.  Set's model param_flag if successful.  This function
    needs to be called before any other to ensure that the parameters
    are stored prior to running calculations.

    Parameters
    ----------
      model: stemProfileModel object instance
      session: SQLAlchemy session

    Returns
    -------
      NA
    '''
    try:
        if model.param_flag:
            pass
        else:
            # store regression parameters as a model property
            model.reg = lookup_reg_params(session, model)
            # store segment parameters as a model property
            model.seg = lookup_seg_params(session, model)
            model.param_flag = 1
    except:
        model.param_flag = None


def calc_dbh_insideBark(model):
    '''
    Calculates diameter inside bark at DBH.  Uses Eq. 7 from Source[1]

    Parameters
    ----------
    model: StemProfileModel object instance

    Returns
    -------
    float, stem diameter inside bark

    Source
    -------
    [1] Clark, A. III, et al. Stem Profile Equations for Southern Tree Speices
    '''
    result = model.reg['reg4_a'] + model.reg['reg4_b'] * model.dbh
    return round(result, 2)



def calc_dStem(session, model, h=0):
    '''
    Calculates stem diameter for the height given.  Uses Eq. 1 from Source[1]

    Parameters
    ----------
      model: StemProfileModel object instance
      session: SQLAlchemy session
      h: stem height to predict diameter

    Returns
    -------
      float, stem diameter at given height

    Source
    -------
    [1] Clark, A. III, et al. Stem Profile Equations for Southern Tree Speices
    '''
    # check that the model parameters have been stored before proceeding
    if model.param_flag:

        # simplify variables for calcs later on, to mimic Source Eq 1.
        r = model.seg['butt_r']
        c = model.seg['butt_c']
        e = model.seg['butt_e']
        p = model.seg['lstem_p']
        b = model.seg['ustem_b']
        a = model.seg['ustem_a']
        if model.bark == 1:  # inside bark
            D = calc_dbh_insideBark(model)
        else:
            D = model.dbh
        H = model.height
        F = calc_d17(model)

        # set indicator variables
        id_S = 1 if h < 4.5 else 0
        id_B = 1 if 4.5 < h < 17.3 else 0
        id_T = 1 if h > 17.3 else 0
        id_M = 1 if h < (17.3 + a * (H - 17.3)) else 0

        # calculate diameter in sections
        d1 = id_S * ((D**2)*(1+(c+e/D**3)*((1-h/H)**r-(1-4.5/H)**r)/(1-(1-4.5/H)**r)))
        d2 = id_B*(D**2-(D**2-F**2)*((1-4.5/H)**p-(1-h/H)**p)/((1-4.5/H)**p-(1-17.3/H)**p))
        d3 = id_T*(F**2*(b*(((h-17.3)/(H-17.3))-1)**2+id_M*((1-b)/a**2)*(a-(h-17.3)/(H-17.3))**2))

        return round((d1 + d2 + d3)**0.5, 2)

    else:
        print("Missing parameters:  Model parameters are required and diameter at 17.3 feet are required before calling this function.")
        return 0.0


def calc_d17(model):
    '''
    estimate stem diameter at 17.3 feet.  Uses Eq. 10 from Source [1]

    Parameters
    ----------
      model: StemProfileModel instance

    Returns
    -------
      float, stem diameter at 17.3 feet

    Source
    -------
    [1] Clark, A. III, et al. Stem Profile Equations for Southern Tree Speices
    '''
    try:
        # check that the model parameters have been stored before proceeding
        if model.param_flag:
            # calculate diameter at 17.3ft
            result = model.dbh * (model.reg['reg17_a'] +
                                  model.reg['reg17_b'] *
                                  (17.3 / model.height) ** 2)
            return round(result, 2)
        else:
            print("Model parameters have not been set.  Please call `get_model_params()` before calling `calc_d17()`.")
    except:
        print("Error calculating diameter at 17.3 feet.  Result may be incorrect!")
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
        output['reg4_a'] = result.reg4_a
        output['reg4_b'] = result.reg4_b
        output['reg17_a'] = result.reg17_a
        output['reg17_b'] = result.reg17_b
        return output

    except:
        # on error set params to 0.0
        output['reg4_a'] = 0.0
        output['reg4_b'] = 0.0
        output['reg17_a'] = 0.0
        output['reg17_b'] = 0.0
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

    # create a default model
    spm = StemProfileModel()
    # get the model params
    get_model_params(session, spm)

    # output
    print(spm)
    print(spm.reg)
    print(spm.seg)
    print('diameter at 17.3 ft', calc_d17(spm))
    print('diameter at h=50 ft', calc_dStem(session, spm, 50))

    session.close()


if __name__ == '__main__':
    main()
