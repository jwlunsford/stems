# imports
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Table, Column, Float, Integer, String
from sqlalchemy.ext.declarative import declarative_base



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


class DataAccessLayer:
    ''' module level database connection info '''

    def __init__(self):
        self.conn_string = 'sqlite:///data/segprofile.db'

    def connect(self):
        self.engine = create_engine(self.conn_string)
        self.Session = sessionmaker(bind=self.engine)

    def close(self):
        self.Session.close()


dal = DataAccessLayer()

Base = declarative_base()

class RegCoeff(Base):
    __tablename__ = 'regcoeff'

    id = Column(Integer(), primary_key=True)
    region = Column(String(50), nullable=False)
    spp = Column(String(50), nullable=False)
    reg_a = Column(Float(), nullable=False)
    reg_b = Column(Float(), nullable=False)
    bark = Column(Integer(), nullable=False)

    # add repr to represent objects
    def __repr__(self):
        return f'''<RegCoeff(region='{self.region}',
        spp='{self.spp}',
        reg_a={self.reg_a},
        reg_b={self.reg_b})>'''


class SegCoeff(Base):
    __tablename__ = 'segcoeff'

    id = Column(Integer(), primary_key=True)
    bark = Column(Integer(), nullable=False)
    spp = Column(String(50), nullable=False)
    butt_r = Column(Float(), nullable=False)
    butt_c = Column(Float(), nullable=False)
    butt_e = Column(Float(), nullable=False)
    lstem_p = Column(Float(), nullable=False)
    ustem_b = Column(Float(), nullable=False)
    ustem_a = Column(Float(), nullable=False)

    # add repr to represent objects
    def __repr__(self):
        return f'''SegCoeff(bark={self.bark},
        spp='{self.spp}',
        butt_r={self.butt_r},
        butt_c={self.butt_c},
        butt_e={self.butt_e},
        lstem_p={self.lstem_p},
        ustem_b={self.ustem_b},
        ustem_a={self.ustem_a})'''
