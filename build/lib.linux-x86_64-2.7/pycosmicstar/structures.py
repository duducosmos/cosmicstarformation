#!/usr/bin/env python3
# *-* Coding: UTF-8 *-*
from __future__ import division, absolute_import

__author__ = "Eduardo dos Santos Pereira"
__email__ = "pereira.somoza@gmail.com"
__credits__ = ["Eduardo dos Santos Pereira"]
__license__ = "GPLV3"
__version__ = "1.0.1"
__maintainer__ = "Eduardo dos Santos Pereira"
__status__ = "Stable"


"""Cosmological Dark Halos History
From the formalism of Reed et al (MNRAS, 346, 565-572, 2003)
it is calculated the mass fraction of dark matter halos.
The code obtain the mass density of dark halos and the fraction
of brions into structures as a function of the time.
Here is used the Transfer function from Efstathiou, Bond & White
-- (MNRAS, 258, 1P, 1992).
The current version it is assumed the normalization of WMAP (withou
gravitational waves) adapted from Eisenstein e Hu (ApJ 511, 5, 1999) that
in the way that return  sigma_8 = 0,84.
The fraction of mass of dark halos is obtained by the work of
Sheth e Tormen (MNRAS 308, 119, 1999).
All models consider Omega_Total = Omega_M + Omega_L = 1,0

This file is part of pystar.
copyright : Eduardo dos Santos Pereira

pystar is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License.
pystar is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

"""

from numpy import sqrt, pi, log, log10, exp, array, abs
import scipy.interpolate as spint
from scipy.interpolate import InterpolatedUnivariateSpline as spline
from scipy.special import gamma

from .structuresabstract import Structuresabstract

import sys
pyversion = sys.version_info
if pyversion[0] >= 3:
    from . import filedict
else:
    print("Importing filedict for python2.7")
    from . import filedict_old as filedict

import os
from .diferencial import dfridr, locate

from .paralleloverlist import parallel_list


class Structures(Structuresabstract):
    """This class was contructed based in the like Press-Schechter formalism
    that provides characteristis like numerical density of dark matter halos
    into the range m_h, m_h + dm_h, the fraction of barionic matter,
    and,  the accretion rate of barions into structures and the total number
    of dark halos.

    The models used to develop this class was presented for the first time
    in the article of Pereira and Miranda (2010) - (MNRAS, 401, 1924, 2010).

    The cosmologic background model is passed as a instance parameter:
        cosmology

    Keyword arguments:
        lmin -- (default 6.0) log10 of the minal mass of the dark halo
                            where it is possible to have star formation.

        zmax -- (defaul 20.0) - the maximum redshift to be considered

        omegam -- (default 0.24) - The dark matter parameter

        omegab -- (default 0.04) - The barionic parameter

        omegal -- (default 0.73) - The dark energy parameter

        h -- (default 0.7) - The h of the Hubble constant (H = h * 100)

        massFunctionType:
            (Dark Haloes Mass Function)
            default 'ST' - Sheth et al. (2001)
            'R' - Reed et al. (2007).
            'TK' - Tinker et al. (2008) - z=[0,2.5]
            'PS' - Press and Schechter (1974)
            'JK' - Jenkins et al. (2001) z=[0,5]
            'W' - Warren et al. (2006) z=0
            'WT1' - Watson et al. (2013) - Tinker Modified
            'WT2' - Watson et al. (2013) - Gamma times times Tinker Modified
            'B' - Burr Distribuction. Marassi and Lima (2006) - Press Schechter
                                    modified.
        qBurr:
            (default 1) - The q value of Burr Distribuction.

    """

    def __init__(self, cosmology, **kwargs):

        listParameters = ["lmin", 'lmax', "zmax",
                      "omegam", "omegab", "omegal", "h",
                      "cacheDir", "cacheFile", "massFunctionType",
                      "delta_halo", "qBurr", "deltaWT"]

        testeKeysArgs = [Ki for Ki in list(kwargs.keys())
                            if Ki not in  listParameters]

        if(len(testeKeysArgs) >= 1):
            nameError = "The key args are not defined:"
            for i in range(len(testeKeysArgs)):
                nameError += testeKeysArgs[i]
            raise NameError(nameError)

        #lmin=6.0, zmax=20.0,

        if 'lmin' in list(kwargs.keys()):
            lmin = kwargs['lmin']
        else:
            lmin = 6.0

        if('lmax' in list(kwargs.keys())):
            self.__lmax = kwargs['lmax']
            self.__mmax = 10.0 ** kwargs['lmax']
        else:
            self.__mmax = 1.0e+18
            self.__lmax = log10(self.__mmax)

        if 'zmax' in list(kwargs.keys()):
            zmax = kwargs['zmax']
        else:
            zmax = 20.0

        #omegam=0.24, omegab=0.04, omegal=0.73, h=0.7,

        if 'omegam' in list(kwargs.keys()):
            omegam = kwargs['omegam']
        else:
            omegam = 0.24

        if 'omegab' in list(kwargs.keys()):
            omegab = kwargs['omegab']
        else:
            omegab = 0.04

        if 'omegal' in list(kwargs.keys()):
            omegal = kwargs['omegal']
        else:
            omegal = 0.73

        if 'h' in list(kwargs.keys()):
            h = kwargs['h']
        else:
            h = 0.7

        #cacheDir=None, cacheFile=None,

        if 'cacheDir' in list(kwargs.keys()):
            cacheDir = kwargs['cacheDir']
        else:
            cacheDir = None

        if 'cacheFile' in list(kwargs.keys()):
            cacheFile = kwargs['cacheFile']
        else:
            cacheFile = None

        #massFunctionType="ST", delta_halo=200, qBurr=1

        if 'massFunctionType' in list(kwargs.keys()):
            massFunctionType = kwargs['massFunctionType']
        else:
            massFunctionType = "ST"

        if 'delta_halo' in list(kwargs.keys()):
            delta_halo = kwargs['delta_halo']
        else:
            delta_halo = 200

        if 'qBurr' in list(kwargs.keys()):
            qBurr = kwargs['qBurr']
        else:
            qBurr = 1

        if "deltaWT" in list(kwargs.keys()):
            self.__deltaWT = kwargs["deltaWT"]
        else:
            self.__deltaWT = 178.0

        self._cosmology = cosmology(omegam, omegab, omegal, h)

        if(cacheDir is None):
            self._cacheDir = self. __creatCachDiretory()[0]
        else:
            self._cacheDir = cacheDir

        if(cacheFile is None):
            if(massFunctionType == "TK"):

                cacheFile = str(self._cacheDir) + "/structures_cache_"\
                  + massFunctionType + str(delta_halo) + "_" + "_" +\
                   str(omegab) + "_" \
                  + str(omegam) + "_" +\
                   str(omegal) + "_ " \
                  + str(h) + "_" + str(lmin) \
                  + "_" + str(self.__lmax) \
                  + "_" + str(zmax)

            else:
                cacheFile = str(self._cacheDir) + "/structures_cache_"\
                      + massFunctionType + "_" + str(omegab) + "_" \
                      + str(omegam) + "_" + str(omegal) + "_ " \
                      + str(h) + "_" + str(lmin) \
                      + "_" + str(self.__lmax) \
                      + "_" + str(zmax)
        else:
            cacheFile = str(self._cacheDir) + cacheFile

        self.__rangeMassFunction = {"ST": None,
                                   "TK": [-1.7, 0.9],
                                   "PS": None,
                                   "JK": [-1.2, 1.05],
                                   "W": [10, 15],
                                   "WT1": [-0.55, 1.31],
                                   "WT2": [-0.06, 1.024],
                                   "B": None,
                                   "R": [-1.7, 0.9]
                                   }

        self.__massFunctionDict = {"ST": self.__massFunctionST,
                                   "TK": self.__massFunctionTinker,
                                   "PS": self.__massFunctionPressSchechter,
                                   "JK": self.__massFunctionJenkins,
                                   "W": self.__massFunctionW,
                                   "WT1": self.__massFunctionWT1,
                                   "WT2": self.__massFunctionWT2,
                                   "B": self.__massFunctionBurr,
                                   "R": self.__massFunctionRedd
                                   }

        self._cacheFIle = cacheFile

        self._cache_dict = filedict.FileDict(filename=cacheFile + ".cache")

        self.__mmin = 1.0e+4

        self._zmax = zmax
        self.__lmin = lmin
        self.__deltac = self._cosmology.getDeltaC()
        self.__pst = 0.3
        self.__dinamicLimits = False

        h2 = h * h
        h2om = h2 * omegam
        #h2br = h2 * omegab
        self.__ut = 1.0 / 3.0
        self.__nr = 14000
        self.__ct0 = 4.0 * pi
        self.__ct1 = self.__ct0 * 2.76e+11 / 3.0
        self.__ct2 = self.__ct1 * h2om
        self.__ast1 = 0.322
        self.__ast2 = 0.707
        self.__pst = 0.3
        self.__tilt2 = self._cosmology.getTilt() / log(10.0)
        self.__ctst = self.__ast1 * sqrt(2.0 * self.__ast2 / pi)

        #Burr q coeficiente
        self.__qBurr = qBurr

        self.__massFunctionType = massFunctionType
        self.__delta_halo = delta_halo

        self.__lmInf, self.__lmSup = None, None
        self.__startingSigmaAccretion()

    def integrationLimitsMassFunction(self):
        if(self.__dinamicLimits is False):
            return [self.__lmin, self.__lmax]
        lnsgm = self.__rangeMassFunction[self.__massFunctionType]
        if(lnsgm is None):
            return [self.__lmin, self.__lmax]

        if(self.__massFunctionType == "W"):
            return lnsgm

        #if(self.__massFunctionType == "TK"):
        sgmMin = 10 ** (- lnsgm[0])
        sgmMax = 10 ** (- lnsgm[1])
        #else:
            #sgmMin = exp(- lnsgm[0])
            #sgmMax = exp(- lnsgm[1])

        return self.massRangeSigma(sgmMin, sgmMax)

    def __creatCachDiretory(self):
        HOME = os.path.expanduser('~')
        if not os.path.exists(HOME + '/.cosmicstarformation'):
            print(('Creating .cosmicstarformation cache diretory in %s'
                     % HOME))
            os.makedirs(HOME + '/.cosmicstarformation')
        return os.path.expanduser('~') + '/.cosmicstarformation', True

    def __ifSigmaNotInCache(self):
        """Calculate the values necessaries to initialize the
        numerical function of sigma
        """
        numk = 1000.0
        kscale = self.__mmax / self.__mmin
        kls = log10(kscale)
        numk = numk * kls
        kls1 = kls / numk
        deltaz = self._zmax / (numk)

        def CalculaKm(i):
            kmass = (10.0 ** ((i + 1) * kls1)) * self.__mmin
            return kmass

        def CalculaScale(i):
            scale = (CalculaKm(i) / self.__ct2) ** self.__ut
            return scale

        self.__kmass = array([CalculaKm(i) for i in range(int(numk))])
        self.__scale = array([CalculaScale(i) for i in range(int(numk))])
        self.__zred = array([self._zmax - i * deltaz
                                  for i in range(int(numk))])

        e, f = self._cosmology.sigma(self.__kmass)

        self.__km = array([ei for ei in e])
        self.__sg = array([FI for FI in f])

        self.__t_z = parallel_list(self._cosmology.age, self.__zred)

        self.__d_c2 = parallel_list(self.__deltaCz, self.__zred)

        self.__rdm2 = parallel_list(self.__rodmz, self.__zred)

        self.__rbr2 = parallel_list(self._cosmology.robr, self.__zred)

        #self.__t_z = array([self._cosmology.age(zi) for zi in self.__zred])

        #self.__d_c2 = array([
            #self.__deltac / self._cosmology.growthFunction(zi)
                            #for zi in self.__zred
                            #])
        #self.__rdm2 = array([self._cosmology.rodm(zi)[0]
                            #for zi in self.__zred
                            #])
        #self.__rbr2 = array([self._cosmology.robr(zi)
                                #for zi in self.__zred])

        self.__lmInf, self.__lmSup = self.integrationLimitsMassFunction()

    def __rodmz(self, z):
        return self._cosmology.rodm(z)[0]

    def __deltaCz(self, z):
        return self.__deltac / self._cosmology.growthFunction(z)

    def __startingSigmaAccretion(self):
        """
        Verify if the values are in cache
        """

        try:

            self.__km = self._cache_dict['km']
            self.__scale = self._cache_dict['scale']
            self.__zred = self._cache_dict['zred']
            self.__sg = self._cache_dict['sg']
            self.__t_z = self._cache_dict['t_z']
            self.__d_c2 = self._cache_dict['d_c2']
            self.__rdm2 = self._cache_dict['rdm2']
            self.__rbr2 = self._cache_dict['rbr2']
            self._abt2 = self._cache_dict['abt2']
            self._ascale = self._cache_dict['ascale']
            self._tck_ab = self._cache_dict['tck_ab']

            print("\nStructures Data in Cache\n")

        except:
            self.__ifSigmaNotInCache()
            self.__startBarionicAccretionRate()
            self.__cachingAtribut()

        self.__lmInf, self.__lmSup = self.integrationLimitsMassFunction()

        print(("The valid log(mass) range for the %s mass function is: "
                % self.__massFunctionType))
        print((self.__lmInf, self.__lmSup))

    def __cachingAtribut(self):
        """Caching the values
        """
        self._cache_dict['km'] = self.__km
        self._cache_dict['scale'] = self.__scale
        self._cache_dict['zred'] = self.__zred
        self._cache_dict['sg'] = self.__sg
        self._cache_dict['t_z'] = self.__t_z
        self._cache_dict['d_c2'] = self.__d_c2
        self._cache_dict['rdm2'] = self.__rdm2
        self._cache_dict['rbr2'] = self.__rbr2
        self._cache_dict['abt2'] = self._abt2
        self._cache_dict['ascale'] = self._ascale
        self._cache_dict['tck_ab'] = self._tck_ab

    def massFunction(self, lm, z):
        """Return the mass function of dark halos.

        Keyword arguments:
            lm -- log10 of the mass of the dark halo
            z -- redshift
        """
        try:
            return self.__massFunctionDict[self.__massFunctionType](lm, z)
        except:
            raise NameError("No Defined Mass Function")

    def validadeMassRange(self, sgm, lnMin, lnMax):
        if(log(sgm) < -1.2 or - log(sgm) > 1.05):
            raise NameError("Mass of dark Halo outside of the valid range")

    def __massFunctionJenkins(self, lm, z):
        """Return the mass function of Jenkins et al. (2003).
         Keyword arguments:
            lm -- log10 of the mass of the dark halo
            z -- redshift
        """

        sgm = self.fstm(lm)
        self.validadeMassRange(sgm, -1.2, 1.05)
        #gte = self._cosmology.growthFunction(z)
        rdmt, drdmt = self._cosmology.rodm(z)
        step = lm / 2.0e+1
        kmsgm = lm
        kmass = 10.0 ** (kmsgm)
        dsgm_dlgm = dfridr(self.fstm, lm, step, err=0.0)
        #sigma1 = self.__deltac / (sgm * gte)
        #sigma2 = sigma1 ** 2.0

        dsgm_dlgm = dfridr(self.fstm, lm, step, err=0.0)

        fst = 0.315 * exp(- abs(log(1.0 / sgm) + 0.61) ** 3.8)

        frst = (rdmt / kmass ** 2.0) * fst * abs(dsgm_dlgm) / sgm
        dn_dm = frst
        return dn_dm

    def __massFunctionPressSchechter(self, lm, z):
        """Return the value of Press-Schechter (1974) mass function.
        Keyword arguments:
            lm -- log10 of the mass of the dark halo
            z -- redshift
        """

        gte = self._cosmology.growthFunction(z)
        rdmt, drdmt = self._cosmology.rodm(z)
        step = lm / 2.0e+1
        kmsgm = lm
        kmass = 10.0 ** (kmsgm)
        sgm = self.fstm(lm)
        dsgm_dlgm = dfridr(self.fstm, lm, step, err=0.0)
        sigma1 = self.__deltac / (sgm * gte)
        sigma2 = sigma1 ** 2.0
        fst = sqrt(2.0 / pi) * (sigma1) * exp(-0.5 * sigma2)
        frst = (rdmt / kmass ** 2.0) * fst * abs(dsgm_dlgm) / sgm
        dn_dm = frst
        return dn_dm

    def _masFunctionWT0(self, lm, z, A, a, b, c):

        rdmt, drdmt = self._cosmology.rodm(z)
        step = lm / 2.0e+1
        kmsgm = lm
        kmass = 10.0 ** (kmsgm)
        sgm = self.fstm(lm)

        dsgm_dlgm = dfridr(self.fstm, lm, step, err=0.0)

        fst = A * (((b / sgm) ** a) + 1.0) * exp(-c / sgm ** 2.0)

        frst = (rdmt / kmass ** 2.0) * fst * abs(dsgm_dlgm) / sgm
        dn_dm = frst
        return dn_dm

    def __massFunctionWT1(self, lm, z):
        """
        Return the value of Watson et al. (2013) (- Tinker Modified - z=[0,30])
        mass function
        Keyword arguments:
            lm -- log10 of the mass of the dark halo
            z -- redshift
        """
        A = 0.282
        a = 2.163
        b = 1.406
        c = 1.21

        gte = self._cosmology.growthFunction(z)
        rdmt, drdmt = self._cosmology.rodm(z)
        step = lm / 2.0e+1
        kmsgm = lm
        kmass = 10.0 ** (kmsgm)
        sgm = self.fstm(lm)

        self.validadeMassRange(sgm, -0.55, 1.31)

        sgmD = sgm * gte

        dsgm_dlgm = dfridr(self.fstm, lm, step, err=0.0)

        fst = A * (((b / sgmD) ** a) + 1.0) * exp(-c / sgmD ** 2.0)

        frst = (rdmt / kmass ** 2.0) * fst * abs(dsgm_dlgm) / sgm
        dn_dm = frst
        return dn_dm

    def __massFunctionWT2(self, lm, z):
        """
        Return the value of Watson et al. (2013) (Gamma times
        Tinker Modified z=[0,30]) mass function
        Keyword arguments:
            lm -- log10 of the mass of the dark halo
            z -- redshift
        """

        gte = self._cosmology.growthFunction(z)
        rdmt, drdmt = self._cosmology.rodm(z)
        step = lm / 2.0e+1
        kmsgm = lm
        kmass = 10.0 ** (kmsgm)
        sgm = self.fstm(lm)

        sgmD = sgm * gte

        dsgm_dlgm = dfridr(self.fstm, lm, step, err=0.0)

        p = 0.072
        q = 2.130

        omz = self._cosmology.omegamz(z)

        cDelta = lambda delta: exp(0.023 * ((delta / 178.0) - 1.0))
        dZ = lambda z: -0.456 * omz - 0.139

        gammaDSZ = lambda delta, sig, z: cDelta(delta) * \
                                         ((delta / 178.0) ** dZ(z)) * \
                                         exp(p * (1.0 - delta / 178)
                                             * (1.0 / sig ** q))

        if(z < 0):
            raise NameError("z lower than zero.")

        if(z == 0):
            self.validadeMassRange(sgm, -0.55, 1.05)
        else:
            self.validadeMassRange(sgm, -0.06, 1.024)

        if(z == 0):
            A = 0.194
            a = 2.267
            b = 1.805
            gm = 1.287

        elif(z >= 6):
            A = 0.563
            a = 3.810
            b = 0.874
            gm = 1.453

        else:

            A = omz * (1.097 * (1.0 + z) ** (-3.216) + 0.074)
            a = omz * (5.907 * ((1.0 + z) ** (-3.058)) + 2.349)
            b = omz * (3.136 * ((1.0 + z) ** (-3.599)) + 2.344)
            gm = 1.318

        fst = A * (((b / sgmD) ** a) + 1.0) * exp(-gm / sgmD ** 2.0)

        fst = gammaDSZ(self.__deltaWT, sgmD, z) * fst

        frst = (rdmt / kmass ** 2.0) * fst * abs(dsgm_dlgm) / sgm
        dn_dm = frst
        return dn_dm

    def _burrBq(self):
        if(self.__qBurr > 0.0 and self.__qBurr < 1.0):
            Bq = ((1.0 - self.__qBurr) ** 0.5) * ((3.0 - self.__qBurr) / 2.0)\
                 * gamma(0.5 + 1.0 / (1.0 - self.__qBurr))\
                 / gamma(1.0 / (1.0 - self.__qBurr))
        elif(self.__qBurr >= 1.0 and self.__qBurr < 2.0):
            Bq = ((self.__qBurr - 1.0) ** 0.5)\
                 * gamma(1.0 / (self.__qBurr - 1.0))\
                 / gamma(1.0 / (self.__qBurr - 1.0) - 0.5)
        else:
            raise NameError('q of Burr function out of valide range')

        return Bq

    def __massFunctionBurr(self, lm, z):
        """
        Return the value of the Burr Distribution (Marassi and Lima (2006))
         - Press Schechter modified, mass function.
        Keyword arguments:
            lm -- log10 of the mass of the dark halo
            z -- redshift
        """
        if(self.__qBurr is None):
            raise NameError('The Burr coeficient is None.')

        gte = self._cosmology.growthFunction(z)
        rdmt, drdmt = self._cosmology.rodm(z)
        step = lm / 2.0e+1
        kmsgm = lm
        kmass = 10.0 ** (kmsgm)
        sgm = self.fstm(lm)
        dsgm_dlgm = dfridr(self.fstm, lm, step, err=0.0)
        sigma1 = self.__deltac / (sgm * gte)
        sigma2 = sigma1 ** 2.0
        fst = self._burrBq() * sqrt(2.0 / pi) * (sigma1) * (
              1.0 - (1.0 - self.__qBurr) * 0.5 * sigma2
              ) ** (1.0 / (1.0 - self.__qBurr))

        frst = (rdmt / kmass ** 2.0) * fst * abs(dsgm_dlgm) / sgm
        dn_dm = frst
        return dn_dm

    def __massFunctionTinker(self, lm, z):
        """Return the mass function of dark halos of
    Tinker mass function (Tinker et al. 2008)

    This function was adapted from the work of:
        S.G. Murray et al. 2013. Astronomy and Computing. 3-4. 23-34.
        source of the original (https://github.com/steven-murray/hmf)

    Keyword arguments:
        lm -- log10 of the mass of the dark halo
        z -- redshift
        """

        #The Tinker function is a bit tricky - we use the code from
        #http://cosmo.nyu.edu/~tinker/massfunction/MF_code.tar
        #to aid us.
        delta_virs = array([200, 300, 400, 600, 800, 1200, 1600, 2400, 3200])
        A_array = array([1.858659e-01,
                            1.995973e-01,
                            2.115659e-01,
                            2.184113e-01,
                            2.480968e-01,
                            2.546053e-01,
                            2.600000e-01,
                            2.600000e-01,
                            2.600000e-01])

        a_array = array([1.466904e+00,
                            1.521782e+00,
                            1.559186e+00,
                            1.614585e+00,
                            1.869936e+00,
                            2.128056e+00,
                            2.301275e+00,
                            2.529241e+00,
                            2.661983e+00])

        b_array = array([2.571104e+00,
                            2.254217e+00,
                            2.048674e+00,
                            1.869559e+00,
                            1.588649e+00,
                            1.507134e+00,
                            1.464374e+00,
                            1.436827e+00,
                            1.405210e+00])

        c_array = array([1.193958e+00,
                            1.270316e+00,
                            1.335191e+00,
                            1.446266e+00,
                            1.581345e+00,
                            1.795050e+00,
                            1.965613e+00,
                            2.237466e+00,
                            2.439729e+00])
        A_func = spline(delta_virs, A_array)
        a_func = spline(delta_virs, a_array)
        b_func = spline(delta_virs, b_array)
        c_func = spline(delta_virs, c_array)

        A_0 = A_func(self.__delta_halo)
        a_0 = a_func(self.__delta_halo)
        b_0 = b_func(self.__delta_halo)
        c_0 = c_func(self.__delta_halo)

        A = A_0 * (1 + z) ** (-0.14)
        a = a_0 * (1 + z) ** (-0.06)
        alpha = exp(-(0.75 / log(self.__delta_halo / 75)) ** 1.2)
        b = b_0 * (1 + z) ** (-alpha)
        c = c_0

        #gte = self._cosmology.growthFunction(z)
        rdmt, drdmt = self._cosmology.rodm(z)
        step = lm / 2.0e+1
        kmsgm = lm
        kmass = 10.0 ** (kmsgm)
        sgm = self.fstm(lm)

        self.validadeMassRange(sgm, -0.6, 0.4)

        dsgm_dlgm = dfridr(self.fstm, lm, step, err=0.0)
        #sigma1 = self.__deltac / (sgm * gte)
        #sigma2 = sigma1 ** 2.0

        dsgm_dlgm = dfridr(self.fstm, lm, step, err=0.0)

        fst = A * ((sgm / b) ** (-a) + 1) * exp(-c / sgm ** 2.0)

        frst = (rdmt / kmass ** 2.0) * fst * abs(dsgm_dlgm) / sgm
        dn_dm = frst
        return dn_dm

    def __massFunctionW(self, lm, z):
        # LANL fitting function - Warren et al. 2005, astro-ph/0506395, eqtn. 5
        A = 0.7234
        a = 1.625
        b = 0.2538
        c = 1.1982

        gte = self._cosmology.growthFunction(z)
        rdmt, drdmt = self._cosmology.rodm(z)
        step = lm / 2.0e+1
        kmsgm = lm
        kmass = 10.0 ** (kmsgm)
        sgm = self.fstm(lm)

        if(lm < 10 or lm > 15):
            raise NameError("Mass of dark Halo outside of the valid range")

        dsgm_dlgm = dfridr(self.fstm, lm, step, err=0.0)
        sigma1 = self.__deltac / (sgm * gte)
        sigma2 = sigma1 ** 2.0

        dsgm_dlgm = dfridr(self.fstm, lm, step, err=0.0)

        fst = A * ((sigma1 ** (-a)) + b) * exp(-c / sigma2)

        frst = (rdmt / kmass ** 2.0) * fst * abs(dsgm_dlgm) / sgm
        dn_dm = frst
        return dn_dm

    def __massFunctionST(self, lm, z):
        """Return the mass function of dark halos of
        Sheth e Tormen (MNRAS 308, 119, 1999).

        Keyword arguments:
            lm -- log10 of the mass of the dark halo
            z -- redshift
        """
        gte = self._cosmology.growthFunction(z)
        #gte2 = self._cosmology.dgrowth_dt(z)
        rdmt, drdmt = self._cosmology.rodm(z)
        step = lm / 2.0e+1
        kmsgm = lm
        kmass = 10.0 ** (kmsgm)
        sgm = self.fstm(lm)
        dsgm_dlgm = dfridr(self.fstm, lm, step, err=0.0)
        sigma1 = self.__deltac / (sgm * gte)
        sigma2 = sigma1 ** 2.0
        expn = exp(-self.__ast2 * sigma2 / 2.0)
        fst = self.__ctst * sigma1 * \
            (1.0 + (1.0 / (sigma2 * self.__ast2)) ** self.__pst) * expn
        frst = (rdmt / kmass ** 2.0) * fst * abs(dsgm_dlgm) / sgm
        dn_dm = frst
        return dn_dm

    def __massFunctionRedd(self, lm, z):
        """Return the mass function of dark halos of
        Reed et al. (MNRAS 374, 2, 2007).
        Based in the genmf.f.
        Reed, Bower, Frenk, Jenkins, and Theuns 2007, MNRAS, 374, 2
        (arXiv:astro-ph/0607150)

        Keyword arguments:
            lm -- log10 of the mass of the dark halo
            z -- redshift
        """
        gte = self._cosmology.growthFunction(z)
        rdmt, drdmt = self._cosmology.rodm(z)
        step = lm / 2.0e+1
        kmsgm = lm
        kmass = 10.0 ** (kmsgm)
        sgm = self.fstm(lm)
        self.validadeMassRange(sgm, -1.7, 0.9)
        dsgm_dlgm = dfridr(self.fstm, lm, step, err=0.0)

        sigma1 = self.__deltac / (sgm * gte)

        neff = ((6.0 / sgm) * abs(dsgm_dlgm) + 3.0)

        sqrt_two_over_pi = 0.79788456
        nu_prime = sqrt(0.707) * sigma1
        lnsigmainv = log(1.0 / sgm)
        lngauss1 = exp(- (lnsigmainv - 0.4) ** 2.0 / 2.0 / 0.6 ** 2.0)
        lngauss2 = exp(- (lnsigmainv - 0.75) ** 2.0 / 2.0 / 0.2 ** 2.0)
        fst = 0.3222 * sqrt_two_over_pi * nu_prime \
                * exp(-1.08 * nu_prime ** 2.0 / 2.0) \
                * (1.0 + 1.0 / nu_prime ** 0.6 +
                    0.6 * lngauss1 + 0.4 * lngauss2) \
                * exp(- 0.03 / (neff + 3.0) ** 2.0 * (sigma1) ** 0.6)

        frst = (rdmt / kmass ** 2.0) * fst * abs(dsgm_dlgm) / sgm
        dn_dm = frst
        return dn_dm

    def fstm(self, lm):
        '''Numerical function that return the value of sigm that
        will be used by dfridr to calculate d_sigma_dlog10(m).

        Keyword arguments:
            lm -- log10 of the mass of dark halo
        '''
        j = locate(self.__km, len(self.__km) - 1, lm)
        return self.__sg[j]

    def massRangeSigma(self, sgmMin, sgmMax):
        """Return the mass down and up for a sigma range
        """

        nElementos = len(self.__sg) - 1

        jmin = locate(self.__sg[::-1], nElementos, sgmMin)
        jmax = locate(self.__sg[::-1], nElementos, sgmMax)

        jmin = (nElementos) - jmin
        jmax = (nElementos) - jmax

        massMin = self.__km[jmin]
        massMax = self.__km[jmax]

        return [massMin, massMax]

    def __fmassM(self, lm, z):
        """Return the mass function of dark halos multiplied by Mass -
        Sheth e Tormen (MNRAS 308, 119, 1999).
        """
        kmsgm = lm
        kmass = 10.0 ** (kmsgm)
        frst = self.massFunction(lm, z) * kmass
        kmassa2 = self.__tilt2 * kmass
        mdn_dm = kmassa2 * frst
        return mdn_dm

    def halos_n(self, z):
        """Return the integral of the mass function of dark halos multiplied
        by mass in the range of log(M_min) a log(M_max)

        Keyword arguments:
            z -- redshift
        """

        lmInf = self.__lmInf
        lmSup = self.__lmSup

        fmassM = lambda lm: self.__fmassM(lm, z)

        deltal = (lmSup - lmInf) / 50.0

        Lm = [lmInf + i * deltal for i in range(50)]

        Fm = [fmassM(lm) for lm in Lm]

        tck = spint.splrep(Lm, Fm)
        Inte = spint.splint(lmInf, lmSup, tck)
        return Inte

    def fbstruc(self, z):
        """Return the faction of barions into structures

        Keyword arguments:
            z -- redshift
        """
        rdm, drdm_dt = self._cosmology.rodm(z)
        fb = self.halos_n(z) / rdm
        return fb

    def numerical_density_halos(self, z):
        """Return the numerial density of dark halos
        within the comove volume

        Keyword arguments:
            z- redshift
        """

        deltal = (self.__lmax - self.__lmin) / 50.0
        Lm = [self.__lmin + i * deltal for i in range(50)]

        Fm = [self.massFunction(lm, z) for lm in Lm]

        tck = spint.splrep(Lm, Fm)
        Inte = spint.splint(self.__lmin, self.__lmax, tck)
        return Inte

    def abt(self, a):
        """Return the accretion rate of barionic matter, as
        a function of scala factor, into strutures.

        Keyword arguments:
            a -- scala factor (1.0 / (1.0 + z))
        """
        i = locate(self._ascale, len(self._ascale) - 1, a)
        return self._abt2[i]

    def __startBarionicAccretionRate(self):

        np = 1000
        deltaz = self._zmax / float(np)

        z = [self._zmax - i * deltaz for i in range(np)]
        z.append(0)
        z = array(z)
        fbt2 = array([self.fbstruc(zi) for zi in z])
        ascale = array([1.0 / (1.0 + zi) for zi in z])
        self._ascale = ascale

        tck = spint.splrep(ascale, fbt2)
        ab3 = spint.splev(ascale, tck, der=1)

        def a5(z, i):
            a = 1.0 / (1.0 + z)
            a2 = a * a
            a3 = -1.0 * ab3[i] * a2
            a4 = a3
            a5 = self._cosmology.getRobr0() * abs(a4) \
                 / self._cosmology.dt_dz(z)
            return a5

        self._abt2 = array([a5(z[i], i) for i in range(z.size)])
        self._tck_ab = spint.splrep(self._ascale, self._abt2)

    def getCacheDir(self):
        """Return True and cache name if the cache directory existe
        and false else.
        """
        if(self._cacheDir is not None):
            return True, self._cacheDir
        else:
            return False

    def getIntegralLimitsFb(self):
        """Return the valid range of mass for a given mass function"""
        lmInf = self.__lmInf
        lmSup = self.__lmSup
        return [lmInf, lmSup]

    def setDeltaHTinker(self, delta_halo):
        if(self.__massFunctionType == "TK"):
            self.__delta_halo = delta_halo
            return True
        else:
            return False

    def getDeltaHTinker(self):
        if(self.__massFunctionType == "TK"):
            return self.__delta_halo
        else:
            raise NameError("TinkerNotDefined")

    def setQBurrFunction(self, q):
        """
        Set the q value of dark haloes mass function derived from Burr
        distribuction.
        """
        self.__qBurr = q

    def getmassFunctionDict(self):
        """
        Return a list with key and function of implemented dark haloes
        mass function
        """
        mydict = []
        for key, value in list(self.__massFunctionDict.items()):
            mydict.append([key, value])
        return mydict

    def setMassFunctionDict(self, key, function):
        """
        Add a new key and function in the dark haloes mass function dictionary
        """

        self.__massFunctionDict[key] = function

