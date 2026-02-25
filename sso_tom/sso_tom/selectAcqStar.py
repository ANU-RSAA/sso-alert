
"""Find a acqusition Star"""

import numpy as np
import argparse
import pandas as pd
from astroquery.vizier import Vizier 
from astropy.coordinates import SkyCoord 
import astropy.units as u

def query_ucac4_circle(ra_deg, dec_deg, radius_arcmin, max_rows=50000):
    Vizier.ROW_LIMIT = max_rows
    Vizier.columns = ['RAJ2000', 'DEJ2000', 'f.mag', 'pmRA', 'pmDE']

    center = SkyCoord(ra_deg, dec_deg, unit='deg')

    result = Vizier.query_region(
        center,
        radius=radius_arcmin * u.arcmin,
        catalog='I/322A',
        column_filters={"RAJ2000": ">0", "DEJ2000": ">-90"}
    )

    if len(result) == 0:
        return None

    tbl = result[0]

    for col in tbl.colnames: 
        print(col, "NaNs:", tbl[col].mask.any())

    # Some proper motions are reported as Nans

    return tbl   # Astropy Table


def add_distances(table, ra_center, dec_center):
    # Centre of your region
    centre = SkyCoord(ra_center, dec_center, unit='deg')

    # Star positions from the table
    stars = SkyCoord(table['RAJ2000'], table['DEJ2000'], unit='deg')

    # Angular separation
    sep = stars.separation(centre)

    # Add as a new column (in arcminutes, for example)
    table['dist_arcmin'] = sep.to(u.arcmin)

    return table


def selectAcqStar(args):
    #Send the query
    magLimit=10.0

    stars=query_ucac4_circle(args.RA, args.Dec, args.searchRadius)
 
    # Compute the distance 
    if stars is not None:
        stars = add_distances(stars, ra_center=args.RA, dec_center=args.Dec)

        # Accept the brightest star fainter than 10th magnitude
        stars.sort('f.mag')
        acqStar=stars[stars['f.mag'] > magLimit][0]

        if args.Verbose:
            print("Acquistion Star")
            print(acqStar)
        acqStar={'acq_ra':acqStar['RAJ2000'],'acq_dec':acqStar['DEJ2000'],'acq_pmra':acqStar['pmRA'],'acq_pmdec':acqStar['pmDE']}

        return acqStar

    else:
        return {'acq_ra':None,'acq_dec':None,'acq_pmra':None,'acq_pmdec':None}




if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Select an aquistion star")

    parser.add_argument(
        "--ra", dest="RA", default=0.00, type=float, help="Right Ascension (degrees)"
    )

    parser.add_argument(
        "--dec", dest="Dec", default=-45.0, type=float, help="Declination (degrees)"
    )

    parser.add_argument(
        "--searchRadius", dest="searchRadius", default=5.0, type=float, help="Search radius (arc minutes)"
    )

    parser.add_argument(
        "--debug", dest="Debug", default=False, action="store_true", help="Debug option"
    )

    parser.add_argument(
        "--verbose", dest="Verbose", default=False, action="store_true", help="Verbose option"
    )

    args = parser.parse_args()

    selectAcqStar(args)
