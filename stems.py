# imports
from data.db import Session, RegCoeff, SegCoeff


class StemProfileModel:
    ''' represents an instance of a stem profile model'''

    def __init__(self, region='deep south', spp='loblolly pine',
                 dbh=16.0, height=90.0, bark=1):
        self.region = region
        self.spp = spp
        self.dbh = dbh
        self.height = height
        self.bark = bark


    def __repr__(self):
        return f'< StemProfileModel(region="{self.region}", spp="{self.spp}", dbh={self.dbh}, height={self.height}, bark={self.bark}, reg_dict={self.reg_dict}, seg_dict={self.seg_dict})'


    def _dbh_insideBark(self):
        '''
        Calculates diameter inside bark at DBH.  Uses Eq. 7 from Source[1]

        Returns
        -------
          float, dbh inside bark rounded to nearst hundredth
        Source
        -------
        [1] Clark, A. III, et al. Stem Profile Equations for Southern Tree Speices
        '''
        if self.reg_dict:
            result = self.reg_dict['reg4_a'] + self.reg_dict['reg4_b'] * self.dbh

            return round(result, 2)

        else:
            print("Missing parameters:  Regression parameters are required before calling this function.")


    def _dia_atGirard(self):
        '''
        Estimate stem diameter at 17.3 feet.  Uses Eq. 10 from Source [1]

        Returns
        -------
          float, stem diameter at Girard Height rounded to nearest hundredth

        Source
        -------
        [1] Clark, A. III, et al. Stem Profile Equations for Southern Tree Speices
        '''

        # check that the model parameters have been stored before proceeding
        if self.reg_dict:
            # calculate diameter at 17.3ft
            result = self.dbh * (self.reg_dict['reg17_a'] +
                                  self.reg_dict['reg17_b'] *
                                  (17.3 / self.height) ** 2)

            return round(result, 2)

        else:
            print("Missing parameters:  Regression parameters are required before calling this function.")


    def _fetch_reg_params(self, session):
        '''
        Queries the database to retrieve the Regression Coefficients for
        the model.

        Parameters
        ----------
        model: StemProfileModel instance
        session: SQLAlchemy DB session

        '''
        try:
            # dict to store output
            params = {}

            # query database
            result = session.query(RegCoeff).filter(
                        RegCoeff.region == self.region,
                        RegCoeff.spp == self.spp,
                        RegCoeff.bark == self.bark).first()

            # add the output to the dict
            params['reg4_a'] = result.reg4_a
            params['reg4_b'] = result.reg4_b
            params['reg17_a'] = result.reg17_a
            params['reg17_b'] = result.reg17_b

            self.reg_dict = params

        except:
            print("Error: Could not retrieve Regression Parameters for the model.")
            self.reg_dict = None


    def _fetch_seg_params(self, session):
        '''
        Queries the database to retrieve the Segment Coefficients for
        the model.

        Parameters
        ----------
        model: StemProfileModel instance
        session:  SQLAlchemy DB session
        '''
        try:
            # dict to store output
            params = {}

            # query database
            result = session.query(SegCoeff).filter(SegCoeff.bark == self.bark,
                                            SegCoeff.spp == self.spp).first()

            # add the ouput to the dict
            params['butt_r'] = result.butt_r
            params['butt_c'] = result.butt_c
            params['butt_e'] = result.butt_e
            params['lstem_p'] = result.lstem_p
            params['ustem_b'] = result.ustem_b
            params['ustem_a'] = result.ustem_a

            self.seg_dict = params

        except:
            print("Error: Could not retrieve Segmented-profile Parameters for the model.")
            self.seg_dict = None


    def fetch_params(self, session):
        '''
        Fetch the stem-profile and regression parameters from the database

        Parameters
        ----------
          session:  SQLAlchemy session instance
        '''

        # query the data and store the results in the model
        self._fetch_reg_params(session)
        self._fetch_seg_params(session)


    def estimate_stemDiameter(self, h=0):
        '''
        Estimates stem diameter for the height given.  Uses Eq. 1 from Source[1]

        Parameters
        ----------
          h: stem height to predict diameter

        Returns
        -------
          float, stem diameter rounded to nearest hundredth

        Source
        -------
        [1] Clark, A. III, et al. Stem Profile Equations for Southern Tree Speices
        '''
        # check that the model parameters have been stored before proceeding
        if self.seg_dict:

            # simplify variables for calcs later on, to mimic Source Eq 1.
            r = self.seg_dict['butt_r']
            c = self.seg_dict['butt_c']
            e = self.seg_dict['butt_e']
            p = self.seg_dict['lstem_p']
            b = self.seg_dict['ustem_b']
            a = self.seg_dict['ustem_a']
            if self.bark == 1:  # inside bark
                D = self._dbh_insideBark()
            else:
                D = self.dbh
            H = self.height
            F = self._dia_atGirard()

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
            print("Missing parameters:  Segmented-profile parameters are required before calling this function.")


    def estimate_stemHeight(self, d=0):
        '''
        Estimates stem height at the diameter given.  Uses Eq. 2 from Source[1]

        Parameters
        ----------
          d: float, stem diameter

        Returns
        -------
          float, height in feet rounded to nearest foot

        Source
        -------
        [1] Clark, A. III, et al. Stem Profile Equations for Southern Tree Speices
        '''
        # check that the model parameters have been stored before proceeding
        if self.seg_dict:

            # simplify variables for calcs later on, to mimic Source Eq 1.
            r = self.seg_dict['butt_r']
            c = self.seg_dict['butt_c']
            e = self.seg_dict['butt_e']
            p = self.seg_dict['lstem_p']
            b = self.seg_dict['ustem_b']
            a = self.seg_dict['ustem_a']
            if self.bark == 1:  # inside bark
                D = self._dbh_insideBark()
            else:
                D = self.dbh
            H = self.height
            F = self._dia_atGirard()

            # set indicator variables
            id_S = 1 if d**2 >= D**2 else 0
            id_B = 1 if D**2 > d**2 >= F**2 else 0
            id_T = 1 if F**2 > d**2 else 0
            id_M = 1 if d**2 > b*(a - 1)**2 * F**2 else 0

            # set combined variables
            G = (1 - 4.5 / H)**r
            W = (c + e / D**3) / (1 - G)
            X = (1 - 4.5 / H)**p
            Y = (1 - 17.3 / H)**p
            Z = (D**2 - F**2) / (X - Y)
            T = D**2 - Z * X
            Qa = b + id_M * (1 - b)/a**2
            Qb = -2 * b - id_M * 2 * (1 - b) / a
            Qc = b + (1 - b) * id_M - d**2 / F **2

            # calculate diameter in sections
            h1 = id_S * H * (1 - ((d**2/D**2 - 1) / W + G)**1 / r)
            h2 = id_B * H * (1 - (X - (D**2 - d**2) / Z)**1 / p)
            h3 = id_T * (17.3 + (H - 17.3) * ((-Qb - (Qb**2 - 4 * Qa *Qc)**0.5)/(2*Qa)))

            return round((h1 + h2 + h3), 0)

        else:
            print("Missing parameters:  Segmented-profile parameters are required before calling this function.")


    def estimate_volume(self, L, U):
        '''
        Estimates stem volume (ft3) between two heights.  Uses Eq. 3 from
        Source[1]

        Parameters
        ----------
          L: integer, lower stem height in feet
          U: integer, upper stem height in feet

        Returns
        -------
          float, vol rounded to the nearest ft3

        Source
        -------
        [1] Clark, A. III, et al. Stem Profile Equations for Southern Tree Speices
        '''
        # check that the model parameters have been stored before proceeding
        if self.seg_dict:

            # simplify variables for calcs later on, to mimic Source Eq 1.
            r = self.seg_dict['butt_r']
            c = self.seg_dict['butt_c']
            e = self.seg_dict['butt_e']
            p = self.seg_dict['lstem_p']
            b = self.seg_dict['ustem_b']
            a = self.seg_dict['ustem_a']
            if self.bark == 1:  # inside bark
                D = self._dbh_insideBark()
            else:
                D = self.dbh
            H = self.height
            F = self._dia_atGirard()

            # set combined variables
            G = (1 - 4.5 / H)**r
            W = (c + e / D**3) / (1 - G)
            X = (1 - 4.5 / H)**p
            Y = (1 - 17.3 / H)**p
            Z = (D**2 - F**2) / (X - Y)
            T = D**2 - Z * X
            L1 = max(L, 0)
            U1 = min(U, 4.5)
            L2 = max(L, 4.5)
            U2 = min(U, 17.3)
            L3 = max(L, 17.3)
            U3 = min(U, H)

            # set indicator variables
            i1 = 1 if L < 4.5 else 0
            i2 = 1 if L < 17.3 else 0
            i3 = 1 if U > 4.5 else 0
            i4 = 1 if U > 17.3 else 0
            i5 = 1 if (L3 - 17.3) < a*(H - 17.3) else 0
            i6 = 1 if (U3 - 17.3) < a*(H - 17.3) else 0

            v1 = i1 * D**2 * ((1-G*W)*(U1-L1)+W*((1-L1/H)**r * (H-L1) - (1-U1/H)**r * (H-U1))/(r+1))
            v2 = i2 * i3 * (T*(U2-L2)+Z*((1-L2/H)**p * (H-L2) - (1-U2/H)**p * (H-U2))/(p+1))
            v3 = i4 * F**2 *(b*(U3-L3)-b*((U3-17.3)**2 - (L3-17.3)**2)/(H-17.3) + (b/3)*((U3-17.3)**3 - (L3-17.3)**3)/(H-17.3)**2 + (i5*(1/3)*((1-b)/a**2)*(a*(H-17.3)-(L3-17.3))**3/(H-17.3)**2 - i6*(1/3)*((1-b)/a**2)*(a*(H-17.3)-(U3-17.3))**3/(H-17.3)**2))

            V = 0.005454154*(v1 + v2 + v3)

            return round(V, 0)






def main():

    # create a default model
    spm = StemProfileModel()

    # fetch the model params from the database and store in the model
    with Session() as session:
        spm.fetch_params(session)

    # output
    print(spm)
    print('Estimate Diameter at 50ft:', spm.estimate_stemDiameter(h=50), " inches")
    print('Estimate Height at Diameter 9":', spm.estimate_stemHeight(d=9), " feet")
    print('Estimate Volume between 1ft and 50 feet:', spm.estimate_volume(L=1, U=50))



if __name__ == '__main__':
    main()
