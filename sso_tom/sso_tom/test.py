from selectSky import selectSky
import argparse

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
args = parser.parse_args()

sky=selectSky(args)

print(sky)