#!/usr/bin/env python

"""Find a sky position for nod and shuffle"""

from sso_tom.catalog_class import DarkSkyPAL
import numpy as np
import argparse
import pandas as pd

def selectSky(args):
    # Loads catalogue of bright stars, galaxies and globular clusters
    # Set the grid spacing that searches for skies to 20 arc seconds

    catalog = DarkSkyPAL(mag_limit=args.magLimit, map_dist=0.5, map_grid_spacing=40, mask_radius=args.maskRadius, ra=args.RA, dec=args.Dec, verbose=args.Verbose, debug=args.Debug)

    # A catalogue of dark sky positions
    single_degree_centre, overlap = catalog.create_degree_square(args.RA, args.Dec, plot_image=args.plotImage, add_query=True, mode='centre', debug=args.Debug)

    # Find the nearest sky position

    if single_degree_centre is not None:
        skies=pd.DataFrame(single_degree_centre, columns=["RA", "Dec"])
        skies['offset']=np.sqrt(((skies['RA']-args.RA)*np.cos(skies['Dec']*np.pi/180.))**2+(skies['Dec']-args.Dec)**2.)  
    
        # Select those that are at least a WiFES FoV away

        valid_skies=skies[skies['offset'] > 40. / 3600.]

        # Sort by the offset and select the first entry
        valid_skies.sort_values(by='offset',inplace=True)

        if len(valid_skies) > 0:
            ra_sky=valid_skies.iloc[0]['RA']
            dec_sky=valid_skies.iloc[0]['Dec']
        else:
            # A valid sky could not be found
            ra_sky = None
            dec_sky = None
    else:
        # A valid sky could not be found
            ra_sky = None
            dec_sky = None


   #print("Sky posiiton: %7.5f %7.5f" % (ra_sky,dec_sky))
   
    return {'ra_sky':ra_sky,'dec_sky':dec_sky}

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Extract all data")

    parser.add_argument(
        "--ra", dest="RA", default=0.00, type=float, help="Right Ascension (degrees)"
    )

    parser.add_argument(
        "--dec", dest="Dec", default=-45.0, type=float, help="Declination (degrees)"
    )

    parser.add_argument(
        "--maskRadius", dest="maskRadius", default=20.0, type=float, help="minimum mask radius (arc seconds)"
    )

    parser.add_argument(
        "--magLimit", dest="magLimit", default=20.0, type=float, help="Magnitude threshold to mask objects"
    )

    parser.add_argument(
        "--debug", dest="Debug", default=False, action="store_true", help="Debug option"
    )

    parser.add_argument(
        "--verbose", dest="Verbose", default=False, action="store_true", help="Verbose option"
    )

    parser.add_argument(
        "--plotImage", dest="plotImage", default=False, action="store_true", help="Verbose option"
    )

    args = parser.parse_args()

    selectSky(args)
