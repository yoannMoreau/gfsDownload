#-*- coding: utf-8 -*-
'''
Created on 25 mars. 2014

Toolbox for downloading GFS meteoData 
depending to the variable GFS needed, a shapefile or an extend for the area, 
the period needed and an optional outputFile for downloaded raster  

@author: yoann Moreau
'''

import sys
import getopt
import os
#from netCDF4 import Dataset
import gdal
import osr
import numpy

import utils as utils

def main(argv):

    try:
        opts,argv = getopt.getopt(argv,":h:i:e:s:o:c:E:t:p:g:P:m:l:",['help','[outFile]','code','[shapeFile]','start','end','[tr]'])
    except getopt.GetoptError:
        print 'error in parameter for GFSDownload. type GFSDownload.py -help for more detail on use '
        sys.exit(2)
    
    for opt, arg in opts:
        if opt == '-h':
            print 'GFSDownload.py  '
            print '    [mandatory] : ',
            print '        --code <GFSCode>'
            print '        --init <dateStart YYYY-MM-DD>'
            print '        --end <dateEnd YYYY-MM-DD>'
            print '        --shapefile <shapefile> OU -Extend < xmin,ymax,xmax,ymin>'
            print '    [optional] :'
            print '        --level <GFS Level> (default surface)'
            print '        --step <GFS Step> (default 3,6,9,12)'
            print '        --grid <GFS Grid> (default 0.75)'
            print '        --outfile <outfolder> (default /home/user/GFS)'
            print '        --proxy <proxy : True/False> (default False)'
            print '        --mode <mode : analyse/forcast> (default analyse)'
            print ''
            print 'EXAMPLES'
            print '--temperature on a shapefile'
            print 'python GFSDownload.py -c PRES -i 2014-01-01 -e 2014-01-02 -s PATH_TO_SHAPE'
            print '--pressure on a area'
            print 'python GFSDownload.py -c 134 -i 2014-01-01 -e 2014-01-02 -E xmin,ymax,xmax,ymin'
            print ''
            print ' CODE PARAMETERS'
            print 'total precipitation  :  APCP [m of water]'
            print '2 metre temperature  :  TMP [K]'
            print 'maximum 2m temperature since last post-processing step : TMAX [K]'
            print 'minimum 2m temperature since last post-processing step : TMIN [K]'
            print 'surface pressure : PRES [Pa]'
            print '2 metre dewpoint : DPT [K]'
            print '10 metre eastward wind component UGRD [m s-1]'
            print '10 metre northward wind component VGRD [m s-1]'
            print '...'
            print ''
            print ' LEVEL PARAMETERS'
            print '2_m_above_ground'
            print '10_m_above_ground'
            print '3000-0_m_above_ground'
            print '300_mb'
            print '...'
            print 'see http://www.nco.ncep.noaa.gov/pmb/products/gfs/ for product description'
            sys.exit() 
        elif opt in ('-o','--outFolder'):
            oFolder = arg
        elif opt in ('-c','--code'):
            codeGFS = arg.split(',')
        elif opt in ('-i','--start'):
            startDate = arg
        elif opt in ('-e','--end'):
            endDate = arg
        elif opt in ('-s','--shapefile'):
            pathToShapefile = arg
        elif opt in ('-E','--tr'):
            extend = arg.split(',')
        elif opt in ('-g','--grid'):
            grid = arg
        elif opt in ('-p','--step'):
            step = arg.split(',')
        elif opt in ('-P','--proxy'):
            proxy = arg
        elif opt in ('-m','--mode'):
            mode = arg
        elif opt in ('-l','--level'):
            levelList = arg.split(',')
    
    if len(sys.argv) < 8:
        print 'GFSDownload.py'
        print '    -c <GFSCode> -list possible-'
        print '    -i <dateStart YYYY-MM-DD> '
        print '    -e <dateEnd YY-MM-DD>'
        print '    -s <shapefile> '
        print '  or'
        print '    -E < xmin,ymax,xmax,ymin>]'
        print ''
        print '    [-g <size of grid in 0.25/0.5/1/2.5> (default 0.25)]'
        print '    [-p <GFS step parameter in 0,6,12,18> default 0,6,12,18] -list possible-'
        print '    [-o <outfolder> (default /home/user/GFS)]'
        print '    [-P <proxy> (default False)]'
        print '    [-l <level> (default 2_m_above_ground)]'
        print ''
        print 'For help on paramCode -help'
        sys.exit(2)
        
    try:
        oFolder
    except NameError:
        oFolder = os.path.expanduser('~')
        oFolder = oFolder + '/GFS'
        print "output folder not precised : downloaded GFF images on "+oFolder
    
    # verification du folder/or creation if not exists
    utils.checkForFolder(oFolder) 
    
    try:
        codeGFS
    except NameError:
        exit ('parameter(s) needed not precise. Please give the GFS parameter you wish')
    utils.checkForParams(codeGFS)
    
    
    try:
        startDate
    except NameError:
        exit ('init Date not precised')
    # verification si sartDate est une date
    startDate=utils.checkForDate(startDate) 
    
    try:
        endDate
    except NameError:
        exit ('end Date not specified')
    # verification si sartDate est une date
    endDate=utils.checkForDate(endDate) 
    
    try:
        pathToShapefile
    except NameError:
        try:
            extend
        except NameError:
            exit ('no Area of interest have been specified. please use -shp or -tr to declare it')
    
    if 'pathToShapefile' in locals():
        extendArea=utils.convertShpToExtend(pathToShapefile)
    else:
        extendArea=extend
    extendArea=utils.checkForExtendValidity(extendArea)
    
    try:
        levelList
    except NameError:
        levelList=['surface']
    levelList=utils.checkForLevelValidity(levelList)
    
    try:
        grid
    except NameError:
        grid='0.25'
    grid=utils.checkForGridValidity(grid)
        
    try:
        step
    except NameError:
        step=[0,6,12,18]
    step=utils.checkForStepValidity(step)
        
    try:
        proxy
    except NameError:
        proxy=False
        
    try:
        mode
    except NameError:
        mode='analyse'
    
    #Proxy parameteres needed
    if(proxy):
        login = raw_input('login proxy : ')
        pwd = raw_input('password proxy :  : ')
        site = raw_input('site (surf.cnes.fr) : ')
        os.environ["http_proxy"] = "http://%s:%s@%s:8050"%(login,pwd,site)
        os.environ["https_proxy"] = "http://%s:%s@%s:8050"%(login,pwd,site)
        
    
    #Download GFS
    outTIFFile=oFolder+'/'+"/".join([str(x) for x in codeGFS])+'_'+startDate.strftime('%Y%m%d')+'_'+endDate.strftime('%Y%m%d')+'.nc'
    struct=utils.create_request_gfs(startDate, endDate, step, levelList, grid, extendArea, codeGFS, outTIFFile, mode)    
    listeFile=[]
    
    if len(struct)==0:
        exit("No data founded")
    else:
        for i in struct[0]:
            try :
                outpath=oFolder+'/'+",".join(codeGFS)+'_'+i.rsplit('.',1)[1]+'.grb'
                listeFile.append(outpath)
                result=utils.GFSDownload(i,outpath)
            except:
                print("---")
                exit('Error in GFS server')
        
        if result:
            utils.convertGribToTiff(listeFile,codeGFS,levelList,step,grid,startDate,endDate,oFolder)
        else:
            exit("PARAM needed is not compatible with level selected")
    
    if struct[1] is not None:
        print ("")
        print ("--------------------------------------------------")
        print ("")
        print ("Some parameters couldn't been downloaded in %s mode :" % mode )
        print ("They have been downloaded in %s mode due to var %s" % (struct[1],','.join(struct[2])) )
    
    #
    #utils.convertNETCDFtoTIF(outNETCDFFile, oFolder+'/tmp.tif')
    #shape=utils.getShape(outNETCDFFile)
    #if ('pathToShapefile' in locals()):
    #    utils.reprojRaster(oFolder+'/tmp.tif',outNETCDFFile.rsplit('.')[0]+'.tif',shape,pathToShapefile)
    #else:
    #    utils.reprojRaster(oFolder+'/tmp.tif',outNETCDFFile.rsplit('.')[0]+'.tif',shape)
    #
    #os.remove(oFolder+'/tmp.tif')
    #os.remove(outNETCDFFile)
    
if __name__ == '__main__':
    main(sys.argv[1:])
    pass