C     -*- fortran -*-
C     This file is autogenerated with f2py (version:2)
C     It contains Fortran 77 wrappers to fortran functions.

      subroutine f2pywrapdtdz (dtdzf2pywrap, z)
      external dtdz
      real*8 z
      real*8 dtdzf2pywrap, dtdz
      dtdzf2pywrap = dtdz(z)
      end


      subroutine f2pywraprz (rzf2pywrap, z)
      external rz
      real*8 z
      real*8 rzf2pywrap, rz
      rzf2pywrap = rz(z)
      end


      subroutine f2pywrapg (gf2pywrap, z)
      external g
      real*8 z
      real*8 gf2pywrap, g
      gf2pywrap = g(z)
      end


      subroutine f2pywrapdr_dz (dr_dzf2pywrap, z)
      external dr_dz
      real*8 z
      real*8 dr_dzf2pywrap, dr_dz
      dr_dzf2pywrap = dr_dz(z)
      end


      subroutine f2pywrapdv_dz (dv_dzf2pywrap, z)
      external dv_dz
      real*8 z
      real*8 dv_dzf2pywrap, dv_dz
      dv_dzf2pywrap = dv_dz(z)
      end


      subroutine f2pywrapage (agef2pywrap, z)
      external age
      real*8 z
      real*8 agef2pywrap, age
      agef2pywrap = age(z)
      end


      subroutine f2pywrapdsigma2_dk (dsigma2_dkf2pywrap, kl)
      external dsigma2_dk
      real*8 kl
      real*8 dsigma2_dkf2pywrap, dsigma2_dk
      dsigma2_dkf2pywrap = dsigma2_dk(kl)
      end


      subroutine f2pywrapgrow (growf2pywrap, z)
      external grow
      real*8 z
      real*8 growf2pywrap, grow
      growf2pywrap = grow(z)
      end


      subroutine f2pywrapdfridr (dfridrf2pywrap, func, x, h, err)
      external dfridr
      external func
      real*8 x
      real*8 h
      real*8 err
      real*8 dfridrf2pywrap, dfridr
      dfridrf2pywrap = dfridr(func, x, h, err)
      end


      subroutine f2pyinitcparam(setupfunc)
      external setupfunc
      real*8 omegab
      real*8 omegam
      real*8 omegal
      real*8 h
      common /cparam/ omegab,omegam,omegal,h
      call setupfunc(omegab,omegam,omegal,h)
      end

      subroutine f2pyinitdados(setupfunc)
      external setupfunc
      real*8 escala
      real*8 alfa
      real*8 beta
      real*8 gama
      common /dados/ escala,alfa,beta,gama
      call setupfunc(escala,alfa,beta,gama)
      end


