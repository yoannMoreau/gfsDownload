#-*- coding: utf-8 -*-
'''
Created on 25 mars. 2014

Toolbox for downloading era_interim Parameters 
depending to the code EMCWF a shapefile or an extend for the area, 
the period needed and an optional outputFile for downloaded raster  

@author: yoann Moreau
@author: benjamin tardy
'''

import sys
import getopt
import os

import utils as utils
from ecmwfapi import ECMWFDataServer

def main(argv):

    try:
        opts,argv = getopt.getopt(argv,":h:i:e:s:o:c:E:t:p:g:P:",['help','[outFile]','code','[shapeFile]','start','end','[tr]'])
    except getopt.GetoptError:
        print 'error in parameter for eraInterimDownload. type eraInterimDownload.py -help for more detail on use '
        sys.exit(2)
    
    for opt, arg in opts:
        if opt == '-h':
            print 'eraInterimDownload.py  '
            print '    [mandatory] : ',
            print '        --code <EraInterimCode>'
            print '        --init <dateStart YYYY-MM-DD>'
            print '        --end <dateEnd YY-MM-DD>'
            print '        --shapefile <shapefile> OU -Extend < xmin,ymax,xmax,ymin>'
            print '    [optional] :'
            print '        --time <EraInterim Time> (default 00)'
            print '        --step <EraInterim Step> (default 0)'
            print '        --grid <EraInterim Time> (default 0.75)'
            print '        --outfile <outfolder> (default /home/user/eraInterim)'
            print '        --proxy <proxy : True/False> (default False)'
            print ''
            print 'EXAMPLES'
            print '--temperature on a shapefile'
            print 'python eraInterimDownload.py -c 167 -i 2014-01-01 -e 2014-01-02 -s PATH_TO_SHAPE'
            print '--pressure on a area'
            print 'python eraInterimDownload.py -c 134 -i 2014-01-01 -e 2014-01-02 -E xmin,ymax,xmax,ymin'
            print ''
            print ' CODE PARAMETERS'
            print ''
            print 'total precipitation  :  228 [m of water]'
            print '2 metre temperature  :  167 [K]'
            print 'maximum 2m temperature since last post-processing step : 201 [K]'
            print 'minimum 2m temperature since last post-processing step : 202 [K]'
            print 'surface pressure : 134 [Pa]'
            print '2 metre dewpoint : 168 [K]'
            print '10 metre eastward wind component X X 165 [m s-1]'
            print '10 metre northward wind component X X 166 [m s-1]'
            print '...'
            print 'see http://old.ecmwf.int/publications/library/ecpublications/_pdf/era/era_report_series/RS_1_v2.pdf for more references'
            sys.exit() 
        elif opt in ('-o','--outFolder'):
            oFolder = arg
        elif opt in ('-c','--code'):
            codeEra = arg.split(',')
        elif opt in ('-i','--start'):
            startDate = arg
        elif opt in ('-e','--end'):
            endDate = arg
        elif opt in ('-s','--shapefile'):
            pathToShapefile = arg
        elif opt in ('-E','--tr'):
            extend = arg.split(',')
        elif opt in ('-t','--time'):
            time = arg.split(',')
        elif opt in ('-g','--grid'):
            grid = arg
        elif opt in ('-p','--step'):
            step = arg.split(',')
        elif opt in ('-P','--proxy'):
            proxy = arg
    
    if len(sys.argv) < 8:
        print 'eraInterimDownload.py'
        print '    -c <EraInterimCode> -list possible-'
        print '    -i <dateStart YYYY-MM-DD> '
        print '    -e <dateEnd YY-MM-DD>'
        print '    -s <shapefile> '
        print '  or'
        print '    -E < xmin,ymax,xmax,ymin>]'
        print ''
        print '    [-t <eraInterim time parameters in 00/66/12/18> (default 00)] -list possible-'
        print '    [-g <size of grid in 0.125/0.25/0.5/0.75/1.125/1.5/2/2.5/3> (default0.75)]'
        print '    [-p <eraInterim step parameter in 00/03/06/12> default 0] -list possible-'
        print '    [-o <outfolder> (default /home/user/eraInterim)]'
        print '    [-P <proxy> (default False)]'
        print ''
        print 'For help on interimCode -help'
        sys.exit(2)
        
    try:
        oFolder
    except NameError:
        oFolder = os.path.expanduser('~')
        oFolder = oFolder + '/eraInterim'
        print "output folder not precised : downloaded eraInterim images on "+oFolder
    
    # verification du folder/or creation if not exists
    utils.checkForFolder(oFolder) 
    
    try:
        codeEra
    except NameError:
        exit ('parameters need not precise. Please give the era Interim parameter you wish')
    
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
        time
    except NameError:
        time=['00']
    time=utils.checkForTimeValidity(time)
    
    try:
        grid
    except NameError:
        grid='0.75'
    grid=utils.checkForGridValidity(grid)
        
    try:
        step
    except NameError:
        step=[0]
    step=utils.checkForStepValidity(step)
    
    try:
        proxy
    except NameError:
        proxy=False
    
    #Proxy parameteres needed
    if(proxy):
        login = raw_input('login proxy : ')
        pwd = raw_input('password proxy :  : ')
        site = raw_input('site (surf.cnes.fr) : ')
        os.environ["http_proxy"] = "http://%s:%s@%s:8050"%(login,pwd,site)
        os.environ["https_proxy"] = "http://%s:%s@%s:8050"%(login,pwd,site)
    
    
    #Create param if first Time
    if (not utils.checkForFile(os.path.expanduser('~')+'/.ecmwfapirc')):
        print ('for first connexion you have to define yout key and password on ecmwf')
        print ('cf  https://apps.ecmwf.int/auth/login/')
        print ('')
        u = raw_input('user (mail) : ')
        k = raw_input('keys : ')
        utils.createParamFile(os.path.expanduser('~')+'/.ecmwfapirc',u,k)
        
    
    #Download NETCDF
    server = ECMWFDataServer()
    struct=utils.create_request_sfc(startDate, endDate, time, step, grid, extendArea, codeEra, oFolder+'/'+"/".join([str(x) for x in codeEra])+'_'+startDate.strftime('%Y%m%d')+'_'+endDate.strftime('%Y%m%d')+'.nc')
    server.retrieve(struct)
    
     
    
if __name__ == '__main__':
    main(sys.argv[1:])
    
    #server = ECMWFDataServer()
    #server.retrieve({
    #"class": "ei",
    #"dataset": "interim",
    #"date": "2014-01-01/2014-01-02",
    #"grid": "0.75/0.75",
    #"levtype": "sfc",
    #"param": "165.128",
    #"step": "0",
    #"stream": "oper",
    #"target": "CHANGEME",
    #"time": "00",
    #"type": "an",
    #})
    pass