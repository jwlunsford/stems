# imports
from data.db import Session, RegCoeff, SegCoeff, WtCoeff


class StemProfileModel:
    ''' represents an instance of a stem profile model'''

    def __init__(self, region='deep south', spp='loblolly pine',
                 dbh=16.0, height=90.0, bark=1):
        self.region = region
        self.spp = spp
        self.dbh = dbh
        self.height = height
        self.bark = bark
        self._params = {}


    def __repr__(self):
        return f'< StemProfileModel(region="{self.region}", spp="{self.spp}", dbh={self.dbh}, height={self.height}, bark={self.bark})'


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
        try:
            result = self._params['reg4_a'] + self._params['reg4_b'] * self.dbh
            return round(result, 2)
        except (TypeError, KeyError):
            print("Error: Invalid parameter. Diameter inside bark at DBH may be incorrect.")


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
        # calculate diameter at 17.3ft
        try:
            result = self.dbh * (self._params['reg17_a'] + self._params['reg17_b']        * (17.3 / self.height) ** 2)
            return round(result, 2)
        except (TypeError, KeyError):
            print("Error: Invalid parameter. Stem diameter at 17.3 feet may be incorrect.")


    def init_params(self, session):
        '''
        Get the stem-profile, regression and weight parameters from
        the database.  Stores values in self._params dict

        Parameters
        ----------
          session:  SQLAlchemy session instance
        '''
        try:

            # Get the Regression parameters from the database
            reg_result = session.query(RegCoeff).filter(
                        RegCoeff.region == self.region,
                        RegCoeff.spp == self.spp,
                        RegCoeff.bark == self.bark).first()

            # add the output to the dict
            self._params['reg4_a'] = reg_result.reg4_a
            self._params['reg4_b'] = reg_result.reg4_b
            self._params['reg17_a'] = reg_result.reg17_a
            self._params['reg17_b'] = reg_result.reg17_b

            # Get the Segmentation parameters from the database
            seg_result = session.query(SegCoeff).filter(SegCoeff.bark == self.bark, SegCoeff.spp == self.spp).first()

            # add the ouput to the dict
            self._params['butt_r'] = seg_result.butt_r
            self._params['butt_c'] = seg_result.butt_c
            self._params['butt_e'] = seg_result.butt_e
            self._params['lstem_p'] = seg_result.lstem_p
            self._params['ustem_b'] = seg_result.ustem_b
            self._params['ustem_a'] = seg_result.ustem_a

            # query database
            wt_result = session.query(WtCoeff).filter(WtCoeff.spp == self.spp).first()

            # this table has a short list of species, so if the result is None
            # use the average tons per cubic feet for all speices listed (0.022)
            if wt_result:
                self._params['tons_per_cuft'] = wt_result.tons_per_cuft
            else:
                self._params['tons_per_cuft'] = 0.022

        except (AttributeError, KeyError):
            print("Error: Invalid parameter. Possibly due to a bad 'species', 'region', or 'bark' input parameter!")



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
        try:

            # simplify variables for calcs later on, to mimic Source Eq 1.
            r = self._params['butt_r']
            c = self._params['butt_c']
            e = self._params['butt_e']
            p = self._params['lstem_p']
            b = self._params['ustem_b']
            a = self._params['ustem_a']
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

        except KeyError:
            print("Error: Invalid parameter. Possibly due to a bad 'species', 'region', or 'bark' input parameter!")


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
        try:

            # simplify variables for calcs later on, to mimic Source Eq 1.
            r = self._params['butt_r']
            c = self._params['butt_c']
            e = self._params['butt_e']
            p = self._params['lstem_p']
            b = self._params['ustem_b']
            a = self._params['ustem_a']
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

            return round((h1 + h2 + h3), 2)

        except KeyError:
            print("Error: Invalid parameter. Possibly due to a bad 'species', 'region', or 'bark' input parameter!")


    def estimate_volume(self, lower=1, upper=17):
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
        try:

            # simplify variables for calcs later on, to mimic Source Eq 1.
            r = self._params['butt_r']
            c = self._params['butt_c']
            e = self._params['butt_e']
            p = self._params['lstem_p']
            b = self._params['ustem_b']
            a = self._params['ustem_a']
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
            L = lower
            U = upper
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
            tons_per_cuft = self._params['tons_per_cuft']

            return round(V * tons_per_cuft, 2)

        except AttributeError:
            print("Error: Invalid parameter. Possibly due to a bad 'species', 'region', or 'bark' input parameter!")


def main():
    session = Session()

    print('Example of how to use Stems.')
    print('-' * 30)
    print('1. Create a StemProfileModel')
    print('\tspm = StemProfileModel(spp="loblolly pine", dbh=20, height=90)')
    spm = StemProfileModel(spp='loblolly pine', dbh=20, height=90)
    print()
    print('2. Initialize the Model Parameters.')
    print('\tspm.init_params(session)')
    spm.init_params(session)
    print()
    session.close()
    print('3. Estimate stem height at 6" in diameter.')
    print('\th = spm.estimate_stemHeight(d=6)')
    h = spm.estimate_stemHeight(d=6)
    print(f'\tHeight where stem is 6 inches inside bark: {h} feet')
    print()
    print('4. Estimate stem diameter at 50 feet.')
    print('\td = spm.estimate_stemDiameter(h=50)')
    d = spm.estimate_stemDiameter(h=50)
    print(f'\tStem diameter inside bark at 50 feet: {d} inches')
    print()


if __name__ == '__main__':
    main()
