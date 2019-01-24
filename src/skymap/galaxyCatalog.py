import sys
import numpy
#from pyfits import open as open_fits
from astropy.io import fits

class gc(object):
    def __init__(self, filename):
        """Loads the galaxy catalogue from a FITS file.
        """
        hdulist = fits.open(filename)
#        print (hdulist[1].header)
#        print (hdulist[1].data)
        data = hdulist[1].data

        self.right_ascension = data.field('RAJ2000')
        self.declination =     data.field('DEJ2000')


        self.distance =        data.field('Dist')
        got_distance = self.distance[~numpy.isnan(self.distance)]
        hist,bins = numpy.histogram(numpy.log10(got_distance), bins=32)
        self.log_distance_centres = []
        self.distance_hist = []
        for i in range(len(bins)-1):
            self.log_distance_centres.append(0.5*(bins[i] + bins[i+1]))
            self.distance_hist.append(float(hist[i])/len(got_distance))
#        print 'centers', self.log_distance_centres
#        print 'histo', self.distance_hist
        isnan = numpy.isnan(self.distance).sum()
        length = len(self.distance)
        print('distance %.0f percent nan' % (isnan*100.0/length))

        self.Kmag =            data.field('Kmag')
        got_Kmag = self.Kmag[~numpy.isnan(self.Kmag)]
        hist,bins = numpy.histogram(got_Kmag, bins=32)
        self.Kmag_centres = []
        self.Kmag_hist = []
        for i in range(len(bins)-1):
            self.Kmag_centres.append(0.5*(bins[i] + bins[i+1]))
            self.Kmag_hist.append(float(hist[i])/len(got_Kmag))
#        print 'centers', self.Kmag_centres
#        print 'histo', self.Kmag_hist
        isnan = numpy.isnan(self.Kmag).sum()
        length = len(self.Kmag)
        print('Kmag %.0f percent nan' % (isnan*100.0/length))

    @staticmethod
    def ptp(data):
        """Returns the minimum, maximum and range of the data.
        """
        clean_data = data[~numpy.isnan(data)]
        dmin = numpy.amin(clean_data)
        dmax = numpy.amax(clean_data)

        return dmin, dmax

    def info(self):
        """Prints some debug information about the right ascension
        and declination data.
        """
        ptp_info = gc.ptp(self.right_ascension)
        print>>sys.stderr, "RA   range: {0[0]:7.2f} - {0[1]:7.2f}".format(ptp_info)

        ptp_info = gc.ptp(self.declination)
        print>>sys.stderr, "Dec  range: {0[0]:6.2f} - {0[1]:6.2f}".format(ptp_info)

        ptp_info = gc.ptp(self.distance)
        print>>sys.stderr, "Dist range: {0[0]:8.4f} - {0[1]:8.4f}".format(ptp_info)

        ptp_info = gc.ptp(self.Kmag)
        print>>sys.stderr, "Kmag range: {0[0]:8.4f} - {0[1]:8.4f}".format(ptp_info)


if __name__ == "__main__":
   gc = gc('/data/ztf/skymap/galaxy_catalog/glade.fits') 
   gc.info()
