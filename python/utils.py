#-*- coding: utf-8 -*-
'''
Created on 16 déc. 2013

@author: yoann Moreau

All controls operations :
return true if control ok 
'''
import os
import errno
from datetime import date,datetime
import ogr,osr
import re
import gdal
import osr
import numpy as np
import subprocess
    
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

def checkForTimeValidity(listTime):
    
    validParameters=('00','06','12','18')
    
    if len(listTime)>0 and isinstance(listTime, list) and all([x in validParameters for x in listTime]):
        return listTime
    else: 
        exit('time parameters not conform to eraInterim posibility : '+ ",".join(validParameters))

def checkForStepValidity(listStep):
    
    validParameters=(0,3,6,9,12)
    
    if len(listStep)>0 and isinstance(listStep, list) and all([int(x) in validParameters for x in listStep]):
        listStep=[int(x) for x in listStep]
        return listStep
    else: 
        exit('step parameters not conform to eraInterim posibility : '+ ",".join([str(x) for x in validParameters]))

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
    

def create_request_sfc(dateStart,dateEnd, timeList,stepList,grid,extent,paramList,output,typeData):
    """
        Genere la structure de requete sur les serveurs de l'ECMWF
        
        INPUTS:\n
        -date : au format annee-mois-jour\n
        -heure : au format heure:minute:seconde\n
        -coord : une liste des coordonnees au format [N,W,S,E]\n
        -dim_grille : taille de la grille en degre \n
        -output : nom & chemin du fichier resultat
    """
    
    listForcastSurface=[129,172,31,32,33,34,35,36,37,38,39,40,41,42,59,78,79,134,136,137,139,141,148,151,159,164,165,166,167,168,170,183,186,187,188,198,206,229,230,231,232,235,236,238,243,244,245,20,44,45,50,57,58,142,143,145,146,147,169,175,176,177,178,179,180,181,182,189,195,196,197,205,208,209,210,211,212,239,240]
    listAnalyseSurface=[27,28,29,30,74,129,160,161,162,163,172,31,32,33,34,35,36,37,38,39,40,41,42,134,136,137,139,141,148,151,164,165,166,167,168,170,173,174,183,186,187,188,198,206,234,235,236,238]
    
    listForcast=[]
    listAnalyse=[]
    structure = []
    
    if typeData=='forcast':
        for i in paramList:
            if int(i) in listForcastSurface:
                listForcast.append(i)
            else:
                if int(i) in listAnalyseSurface:
                    listAnalyse.append(i)
                else:
                    print "the parameter needed couldn't be downloaded because is not a Surface variable"
    else:
        for i in paramList:
            if int(i) in listAnalyseSurface:
                listAnalyse.append(i)
            else:
                if int(i) in listForcastSurface:
                    listForcast.append(i)
                else:
                    print "the parameter needed couldn't be downloaded because is not a Surface variable"
    
    if len(listAnalyse)>0:
        struct = {
        'dataset' : "interim",
        'date'    : dateStart.strftime("%Y-%m-%d")+"/to/"+dateEnd.strftime("%Y-%m-%d"),
        'time'    : "/".join(map(str, timeList)),
        'stream'  : "oper",
        'step'    : "/".join(map(str, stepList)),
        'levtype' : "sfc", #TO DO pl -> pressure level ,sfc -> surface
        'type'    : "an", #TO DO fc -> forcast , an -> analyse
        'class'   : "ei",
        'param'   : ".128/".join(map(str, listAnalyse))+'.128',
        'area'    : "/".join(extent),
        'grid'    : str(grid)+"/"+str(grid),
        'target'  : output,
        'format'  : 'netcdf'
        }
        structure.append(struct)
    
    if len(listForcast)>0:
        struct = {
        'dataset' : "interim",
        'date'    : dateStart.strftime("%Y-%m-%d")+"/to/"+dateEnd.strftime("%Y-%m-%d"),
        'time'    : "/".join(map(str, timeList)),
        'stream'  : "oper",
        'step'    : "/".join(map(str, stepList)),
        'levtype' : "sfc", #TO DO pl -> pressure level ,sfc -> surface
        'type'    : "fc", #TO DO fc -> forcast , an -> analyse
        'class'   : "ei",
        'param'   : ".128/".join(map(str, listForcast))+'.128',
        'area'    : "/".join(extent),
        'grid'    : str(grid)+"/"+str(grid),
        'target'  : output,
        'format'  : 'netcdf'
        }
        structure.append(struct)
    
    if typeData=='forcast' and len(listAnalyse)>0:
        return (structure,",".join(listAnalyse),"analyse")
    elif typeData=='analyse' and len(listForcast)>0:
        return (structure,",".join(listForcast),"forecast")
    else:
        return (structure,None)

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

def convertNETCDFtoTIF(inputFile,outputFile,format='float'):
    #--convert netCDF to tif
    
    ds_in=gdal.Open('NETCDF:"'+inputFile+'"')
    metadata = ds_in.GetMetadata()
    
    for i in metadata.keys():
        if i.find('scale_factor')>0:
            scale=metadata[i]
        elif i.find('add_offset')>0:
            offset=metadata[i]
        elif i.find('_FillValue')>0:
            nodata=metadata[i]

    cols = ds_in.RasterXSize
    rows = ds_in.RasterYSize
    geotransform = ds_in.GetGeoTransform()
    originX = geotransform[0]
    originY = geotransform[3]
    pixelWidth = geotransform[1]
    pixelHeight = geotransform[5]
    nbBand= ds_in.RasterCount
    
    driver = gdal.GetDriverByName('GTiff')
    outRaster = driver.Create(outputFile,cols, rows, nbBand, gdal.GDT_Float32)
    outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))

    
    for b in range(1,nbBand+1):
        band = ds_in.GetRasterBand(b)
        
        arrayB = np.array(band.ReadAsArray(), dtype=format)
        np.putmask(arrayB,(arrayB==float(nodata)),0)
        #arrayB=numpy.multiply(arrayB, scale)+float(offset)
        trans_arrayB=arrayB*float(scale)+float(offset)
        np.putmask(trans_arrayB,(arrayB==float(nodata)+1),0)
        outband = outRaster.GetRasterBand(b)
        outband.WriteArray(trans_arrayB)
    
    spatialRef = osr.SpatialReference()
    spatialRef.ImportFromEPSG(4326) 
    outRaster.SetProjection(spatialRef.ExportToWkt())
