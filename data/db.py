# imports
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Table, Column, Float, Integer, String
from sqlalchemy.ext.declarative import declarative_base


engine = create_engine('sqlite:///data/segprofile.db')
Session = sessionmaker(bind=engine)

Base = declarative_base()


# TODO:  Need code that will build the DB, create all tables and import the CSV # files in data/

class RegCoeff(Base):
    __tablename__ = 'regcoeff'

    id = Column(Integer(), primary_key=True)
    region = Column(String(50), nullable=False)
    spp = Column(String(50), nullable=False)
    bark = Column(Integer(), nullable=False)
    reg4_a = Column(Float(), nullable=False)
    reg4_b = Column(Float(), nullable=False)
    reg17_a = Column(Float(), nullable=False)
    reg17_b = Column(Float(), nullable=False)

    # add repr to represent objects
    def __repr__(self):
        return f'''<RegCoeff(region='{self.region}',
        spp='{self.spp}',
        bark='{self.bark}',
        reg4_a={self.reg4_a},
        reg4_b={self.reg4_b},
        reg17_a={self.reg17_a},
        reg17_b={self.reg17_b})>'''


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
