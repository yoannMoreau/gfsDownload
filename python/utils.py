#-*- coding: utf-8 -*-
'''
Created on 16 déc. 2013

@author: yoann Moreau

All controls operations :
return true if control ok 
'''
import os
import errno
from datetime import date,datetime, timedelta
import ogr,osr
import re
import gdal
import osr
import numpy as np
import subprocess
import urllib2
import pygrib
from curses.ascii import isdigit
    
def checkForFile(pathToFile):
    if os.path.isfile(pathToFile):
        return True
    else:
        return False

def createParamFile(pathFile,user,key):
    
    f = open(pathFile, 'w+')
    f.write("{\n")
    f.write(' "url"   : "https://api.ecmwf.int/v1",\n')
    f.write('"key"   : "'+key+'",\n')
    f.write('"email" : "'+user+'"\n')
    f.write("}")
    f.close()
    

def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def checkForFolder(pathToFolder):
    try:
        os.makedirs(pathToFolder)
    except OSError as exception:
        if exception.errno != errno.EEXIST:            
            exit('Path for downloaded Era Interim could not be create. Check your right on the parent folder...')
            
def checkForDate(dateC):
    #convert string to date from YYYY-MM-DD

    if len(dateC)==10:
        YYYY=dateC[0:4]
        MM=dateC[5:7]
        DD=dateC[8:10]
        if (YYYY.isdigit() and MM.isdigit()  and DD.isdigit()):
            try:
                date(int(YYYY),int(MM),int(DD))
            except ValueError:
                exit('Error on Date Format... please give a date in YYYY-MM-DD format')
            
            return date(int(YYYY),int(MM),int(DD))

        else:
            exit('Error on Date Format... please give a date in YYYY-MM-DD format')
    else: 
        exit('Error on Date Format... please give a date in YYYY-MM-DD format')

def convertShpToExtend(pathToShp):
    """
    reprojette en WGS84 et recupere l'extend
    """ 
    
    driver = ogr.GetDriverByName('ESRI Shapefile')
    dataset = driver.Open(pathToShp)
    if dataset is not None:
        # from Layer
        layer = dataset.GetLayer()
        spatialRef = layer.GetSpatialRef()
        # from Geometry
        feature = layer.GetNextFeature()
        geom = feature.GetGeometryRef()
        spatialRef = geom.GetSpatialReference()
        
        #WGS84
        outSpatialRef = osr.SpatialReference()
        outSpatialRef.ImportFromEPSG(4326)

        coordTrans = osr.CoordinateTransformation(spatialRef, outSpatialRef)

        env = geom.GetEnvelope()

        pointMAX = ogr.Geometry(ogr.wkbPoint)
        pointMAX.AddPoint(env[1], env[3])
        pointMAX.Transform(coordTrans)
        
        pointMIN = ogr.Geometry(ogr.wkbPoint)
        pointMIN.AddPoint(env[0], env[2])
        pointMIN.Transform(coordTrans)


        return [pointMAX.GetPoint()[1],pointMIN.GetPoint()[0],pointMIN.GetPoint()[1],pointMAX.GetPoint()[0]]
    else:
        exit(" shapefile not found. Please verify your path to the shapefile")


def is_float_re(element):
    _float_regexp = re.compile(r"^[-+]?(?:\b[0-9]+(?:\.[0-9]*)?|\.[0-9]+\b)(?:[eE][-+]?[0-9]+\b)?$").match
    return True if _float_regexp(element) else False


def checkForExtendValidity(extendList):
    
    if len(extendList)==4 and all([is_float_re(str(x)) for x in extendList]) and extendList[0]>extendList[2] and extendList[1]<extendList[3]:
        if float(extendList[0]) > -180 and float(extendList[2]) <180 and float(extendList[1]) <90 and  float(extendList[3]) > -90:
            extendArea=[str(x) for x in extendList]
            return extendArea
        else:
            exit('Projection given is not in WGS84. Please verify your -t parameter')
    else:
        exit('Area scpecified is not conform to a  ymax xmin ymin xmax  extend. please verify your declaration')

def checkForLevelValidity(levelList):
    
    levelPossible=['0-0.1_m_below_ground','0.1-0.4_m_below_ground','0.33-1_sigma_layer','0.4-1_m_below_ground','0.44-0.72_sigma_layer','0.44-1_sigma_layer','0.72-0.94_sigma_layer','0.995_sigma','0C_isotherm','1000_mb','100_m_above_ground','100_mb','10_m_above_ground','10_mb','1-2_m_below_ground','150_mb','180-0_mb_above_ground','1829_m_above_mean_sea','200_mb','20_mb','250_mb','255-0_mb_above_ground','2743_m_above_mean_sea','2_m_above_ground','3000-0_m_above_ground','300_mb','30-0_mb_above_ground','30_mb','350_mb','3658_m_above_mean_sea','400_mb','450_mb','500_mb','50_mb','550_mb','6000-0_m_above_ground','600_mb','650_mb','700_mb','70_mb','750_mb','800_mb','80_m_above_ground','850_mb','900_mb','925_mb','950_mb','975_mb','boundary_layer_cloud_layer','convective_cloud_bottom','convective_cloud_layer','convective_cloud_top','entire_atmosphere','entire_atmosphere_%5C%28considered_as_a_single_layer%5C%29','high_cloud_bottom','high_cloud_layer','high_cloud_top','tropopause','highest_tropospheric_freezing','low_cloud_bottom','low_cloud_layer','low_cloud_top','max_wind','mean_sea','middle_cloud_bottom','middle_cloud_layer','middle_cloud_top','planetary_boundary_layer','PV%3D-2e-06_%5C%28Km%5C%5E2%2Fkg%2Fs%5C%29_surface','PV%3D2e-06_%5C%28Km%5C%5E2%2Fkg%2Fs%5C%29_surface','surface','top_of_atmosphere']
    if all([x in levelPossible for x in levelList]):
        return levelList
    else:
        exit('One or more level declared is not available. Please choose one in those  : %s' % '\n'.join(levelPossible))

def checkForParams(codeGFS):
    codeGFSPossible=['all','4LFTX','5WAVH','ABSV','ACPCP','ALBDO','APCP','CAPE','CFRZR','CICEP','CIN','CLWMR','CPOFP','CPRAT','CRAIN','CSNOW','CWAT','CWORK','DLWRF','DPT','DSWRF','FLDCP','GFLUX','GUST','HGT','HINDEX','HLCY','HPBL','ICAHT','ICEC','LAND','LFTX','LHTFL','MSLET','O3MR','PEVPR','PLPL','POT','PRATE','PRES','PRMSL','PWAT','RH','SHTFL','SNOD','SOILW','SPFH','SUNSD','TCDC','TMAX','TMIN','TMP','TOZNE','TSOIL','UFLX','UGRD','U-GWD','ULWRF','USTM','USWRF','VFLX','VGRD','V-GWD','VRATE','VSTM','VVEL','VWSH','WATR','WEASD','WILT']
    
    if all([x in codeGFSPossible for x in codeGFS]):
        return codeGFS
    else:
        exit('One or more level declared is not available. Please choose one in those  : %s' % '\n'.join(codeGFSPossible))
        
        
def checkForProductValidity(listTime):
    
    validParameters=('00','06','12','18')
    
    if len(listTime)>0 and isinstance(listTime, list) and all([x in validParameters for x in listTime]):
        return listTime
    else: 
        exit('time parameters not conform to GFS posibility : '+ ",".join(validParameters))

def checkForStepValidity(listStep):
    
    validParameters=(0,6,12,18)
    
    if len(listStep)>0 and isinstance(listStep, list) and all([int(x) in validParameters for x in listStep]):
        listStep=[int(x) for x in listStep]
        return listStep
    else: 
        exit('step parameters not conform to GFS posibility : '+ ",".join([str(x) for x in validParameters]))

def checkForGridValidity(grid):
    
    if (is_float_re(grid)):
        grid=float(grid)
        validParameters=(0.125,0.25,0.5,0.75,1.125,1.5,2,2.5,3)
        
        if grid in validParameters:
            return grid
        else:
            exit('grid parameters not conform to eraInterim posibility : '+ ",".join([str(x) for x in validParameters]))
    else:
        exit('grid parameters not conform to eraInterim posibility : '+ ",".join([str(x) for x in validParameters]))
    

def create_request_gfs(dateStart,dateEnd,stepList,levelList,grid,extent,paramList,output,typeData):
    """
        Genere la structure de requete pour le téléchargement de données GFS
        
        INPUTS:\n
        -date : au format annee-mois-jour\n
        -heure : au format heure:minute:seconde\n
        -coord : une liste des coordonnees au format [N,W,S,E]\n
        -dim_grille : taille de la grille en degree \n
        -output : nom & chemin du fichier resultat
    """
    
    URLlist=[]
    
    #Control datetype
    listForcastSurface=['GUST','HINDEX','PRES','HGT','TMP','WEASD','SNOD','CPOFP','WILT','FLDCP','SUNSD','LFTX','CAPE','CIN','4LFTX','HPBL','LAND']
    if (0 not in [int(x) for x in stepList]):
        listForcastSurface=listForcastSurface+['PEVPR','CPRAT','PRATE','APCP','ACPCP','WATR','CSNOW','CICEP','CFPER','CRAIN','LHTFL','SHTFL','SHTFL','GFLUX','UFLX','VFLX','U-GWD','V-GWD','DSWRF','DLWRF','ULWRF','USWRF','ALBDO']
    listAnalyseSurface=['HGT','PRES','LFTX','CAPE','CIN','4LFTX']
    
    if typeData == 'analyse' and all([x in listAnalyseSurface for x in paramList]):
        typeData= 'analyse'
        validChoice = None
    else:
        typeData= 'forcast'
        validChoice = typeData
        indexParameters=[i for i, elem in enumerate([x in listAnalyseSurface for x in paramList], 1) if not elem]
        prbParameters=[]
        for i in indexParameters:
            prbParameters.append(paramList[i-1])
    #Control si date/timeList disponible
    today=date.today()
    lastData = today - timedelta(days=14)
    if dateStart < lastData or dateEnd > today : 
        exit('date are not in 14 days range from today' )
    else:
        #Pour chaque jour souhaité
        nbDays=(dateStart-dateEnd).days+1
        for i in range(0,nbDays):
            #on crontrole pour les timeList
            if dateStart + timedelta(days=i) == today:
                maxT=datetime.now().hour-5
                timeListCorr=[ x for x in stepList if x<maxT ]
            else:
                timeListCorr=stepList
              
            for t in timeListCorr:
                URL='http://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_'
                #grid
                URL=URL+"{:.2f}".format(grid).replace('.','p')+'.pl?file=gfs.'
                #time ( attention limiter avec décalage horaire for today
                URL=URL+'t'+str(t).zfill(2)+'z.'
                if (grid==0.5):
                    URL=URL+'pgrb2full.'
                else:
                    URL=URL+'pgrb2.'
                URL=URL+"{:.2f}".format(grid).replace('.','p')+'.'
                
                if typeData=='forcast':
                    URL=URL+'f000&lev_'
                else:
                    URL=URL+'anl&lev_'
                URL=URL+"=on&lev_".join(levelList)+"=on&var_"
                URL=URL+"=on&var_".join(paramList)+"=on&subregion=&"
                URL=URL+"leftlon="+str(round(float(extent[1])-0.05,1))+"&rightlon="+str(round(float(extent[3])+0.05,1))+"&toplat="+str(round(float(extent[0])+0.5,1))+"&bottomlat="+str(round(float(extent[2])-0.5,1))
                URL=URL+"&dir=%2Fgfs."+"{:%Y%m%d}".format(dateStart+timedelta(days=i))+str(t).zfill(2)
                URLlist.append(URL)
        
        print URLlist
        return (URLlist,validChoice,prbParameters)
    
def reprojRaster(pathToImg,output,shape,pathToShape=None):
    
    driver = ogr.GetDriverByName('ESRI Shapefile')
    if pathToShape is not None:
        dataSource = driver.Open(pathToShape, 0)
        layer = dataSource.GetLayer()
        srs = layer.GetSpatialRef()
        proj = srs.ExportToWkt()
    else :
        proj='EPSG:4326'
        
    Xres=shape[0]
    Yres=shape[1]
    subprocess.call(["gdalwarp","-q","-t_srs",proj,pathToImg,output,'-ts',str(Xres),str(Yres),'-overwrite','-dstnodata',"0"])
    return output

def getShape(pathToImg):
        
    raster = gdal.Open(pathToImg)
    cols = raster.RasterXSize
    rows = raster.RasterYSize
    
    return (cols,rows)

def GFSDownload(pathToFile,pathToOutputFile):

    response = urllib2.urlopen(pathToFile)
    
    try:
        html = response.read()
    except:
        exit("error while downloading file")
    
    if len(html) > 0:
        f = open(pathToOutputFile, 'wb')
        f.write(html)
        return True
    else:
        return False

def writeTiffFromDicoArray(DicoArray,outputImg,shape,geoparam,proj=None,format=gdal.GDT_Float32):
    
    gdalFormat = 'GTiff'
    driver = gdal.GetDriverByName(gdalFormat)

    dst_ds = driver.Create(outputImg, shape[1], shape[0], len(DicoArray), format)
    
    j=1
    for i in DicoArray.values():
        dst_ds.GetRasterBand(j).WriteArray(i, 0)
        band = dst_ds.GetRasterBand(j)
        band.SetNoDataValue(0)
        j+=1
    
    originX =  geoparam[0]
    originY =  geoparam[1]
    pixelWidth = geoparam[2]
    pixelHeight  = geoparam[3]

    dst_ds.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
    if proj==None:
        spatialRef = osr.SpatialReference()
        spatialRef.ImportFromEPSG(4326) 
        dst_ds.SetProjection(spatialRef.ExportToWkt())

def convertGribToTiff(listeFile,listParam,listLevel,liststep,grid,startDate,endDate,outFolder):
    """ Convert GRIB to Tif"""
    
    dicoValues={}
    
    for l in listeFile:
        grbs = pygrib.open(l)
        grbs.seek(0)
        index=1
        for j in range(len(listLevel),0,-1):
            for i in range(len(listParam)-1,-1,-1):
                grb = grbs[index]
                p=grb.name.replace(' ','_')
                if grb.level != 0:
                    l=str(grb.level)+'_'+grb.typeOfLevel
                else:
                    l=grb.typeOfLevel
                if p+'_'+l not in dicoValues.keys():
                    dicoValues[p+'_'+l]=[]
                dicoValues[p+'_'+l].append(grb.values)
                shape=grb.values.shape
                lat,lon=grb.latlons()
                geoparam=(lon.min(),lat.max(),grid,grid)
                index+= 1

    nbJour=(endDate-startDate).days+1
    #on joute des arrayNan si il manque des fichiers
    for s in range(0, (len(liststep)*nbJour-len(listeFile))):
        for k in dicoValues.keys():
            dicoValues[k].append(np.full(shape, np.nan))

    #On écrit pour chacune des variables dans un fichier
    for i in range(len(dicoValues.keys())-1,-1,-1):
        dictParam=dict((k,dicoValues[dicoValues.keys()[i]][k]) for k in range(0,len(dicoValues[dicoValues.keys()[i]])))
        sorted(dictParam.items(), key=lambda x: x[0])
        outputImg=outFolder+'/'+dicoValues.keys()[i]+'_'+startDate.strftime('%Y%M%d')+'_'+endDate.strftime('%Y%M%d')+'.tif'
        writeTiffFromDicoArray(dictParam,outputImg,shape,geoparam)
    
    for f in listeFile:
        os.remove(f)

