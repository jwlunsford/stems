# STEMS
Stems is a model that utilizes the form-class segmented-profile equations for southern
pine and hardwood species created by **A Clark III, R.A. Souter, and B.E. Schlaegel of
the Southeastern Forest Experiment Station** (see Source[1] below).  The model currently includes six
southern pine species including Loblolly Pine, Slash Pine, Shortleaf Pine, Longleaf Pine,
White Pine and Virginia Pine. More speices can be easily added by updating the included database
with the model coefficients provided in Source[1].

# PURPOSE
This model is capable of predicting diameter at any height, height to any diameter and volume
between two heights along the stem.  This model can be used to ajdust inventory volumes, to
estimate stem taper, to analyze product merchandizing decisions, etc.

# HOW TO USE
Download the repository as a ZIP file or clone it using Git.

The code was written using Python version 3.7.  The following packages are required to run the program.
* Sqlalchemy 1.4.20

The model parameters are stored in a SQLite database.  To begin, the user needs to create a model instance, and query the database for the model parameters.  The following code shows an example of using the model in a command-line interface ...

```
# import the package
import stems as stm

# create a session instance, a model instance and retrieve the model parameters
with stm.Session() as session:
    spm = stm.StemProfileModel(spp='shortleaf pine', dbh=18, height=95)
    spm.fetch_params(session)

# calcuate height to a given diameter, d=6
spm.estimate_stemHeight(d=6)

# calculate diameter at a given height, h=64
spm.estimate_stemDiameter(h=64)

# calculate volume in green tons between stump and 64 feet
spm.estimate_volume(lower=1, upper=64)
```

# SOURCES
[1] A. Clark III, R.A. Souter, and B.E. Schlaegel. (1991) ***Stem Profile Equations for Southern Tree Species*** Res. Pap. SE-282.  Ashville, NC: U.S. Department of Agriculture, Forest Service, Southeastern Forest Experiment Station.

