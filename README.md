=======
# eraInterimDownload
Tools for downloading era Interim physical parameters on an area.
Era Interim is a product of ECMWF and provide a full range of product which are describe in 
http://old.ecmwf.int/publications/library/ecpublications/_pdf/era/era_report_series/RS_1_v2.pdf
 
<h2>Installation<b></h2>

mkdir PATH/TO/INSTALL <br>
cd  PATH/TO/INSTALL/eraInterimDownload <br>
git clone git+git://github.com/yoannMoreau/eraInterimDownload.git <br>
sudo pip install https://software.ecmwf.int/wiki/download/attachments/23694554/ecmwf-api-client-python.tgz 
python python/landsat_theia.py -help <br>

( or you cas Use pip to install eraInterimDownload )

<h2>Overview: What can eraInterimDownload do?</h2>

eraInterimDownload has a main function, allow download of parameters on a area in an automatic way
All type of parameters could be downloaded throuh that utilitary

Four paramaters are mandatory: <br><br>
 --code <EraInterimCode>
 a list of code wich should be downloaded. Code reference can be found on http://old.ecmwf.int/publications/library/ecpublications/_pdf/era/era_report_series/RS_1_v2.pdf
<b>CODE PARAMETERS Exemple :</b>
total precipitation  :  228 <i>[m of water]</i>
2 meters temperature  :  167 <i>[K]</i>
maximum 2m temperature since last post-processing step : 201 <i>[K]</i>
minimum 2m temperature since last post-processing step : 202 <i>[K]</i>
surface pressure : 134 <i>[Pa]</i>
2 meters dewpoint : 168 <i>[K]</i>
10 meters eastward wind component X X 165 <i>[m s-1]</i>
10 meters northward wind component X X 166 <i>[m s-1]</i>
<br><br>
<br> Interval needed
--init <dateStart YYYY-MM-DD>'<br>
--end <dateEnd YY-MM-DD>'
<br><br>
<br> Area needed
--shapefile <pathToShapefile> (srs is not important because it will be reprojected in WGS84)
OR 
--Extend <xmin,ymax,xmax,ymin> in WGS84
<br><br>
EXAMPLES :<br>
--temperature on a shapefile during the first to the second of january <br>
python eraInterimDownload.py -c 167 -i 2014-01-01 -e 2014-01-02 -s PATH_TO_SHAPE'
--pressure on a area  during the first month of 2015 on a specific extend<br>
python eraInterimDownload.py -c 134 -i 2015-01-01 -e 2015-02-01 -E xmin,ymax,xmax,ymin'
<br><br>
Five paramaters are optional: <br><br>
--Time <EraInterim Time> (default 00)' <br><br>
The time for starting modelisation. It could be 00h 06h,12h or 18h (selection in 00,06,12,18). 
Default is 0. 
A list is possible for that parameter
<br><br>
python eraInterimDownload.py -c 168 -i 2013-11-08 -e 2013-12-09 -E xmin,ymax,xmax,ymin -t 00,06,12,18'
<br><br>
--Step <EraInterim Time> (default 0)' <br><br>
The step of modeling. Some parameters are not possible within some of the possibilities. 
Check the documentation for more information.
default is 0. 
A list is possible for that parameter
<br><br>
python eraInterimDownload.py -c 168 -i 2013-11-08 -e 2013-12-09 -E xmin,ymax,xmax,ymin -p 0,6'
<br><br>
--Grid <grid spacing on °.arc> (default 0)' <br><br>
The spacing of final raster. grid possible : 0.125/0.25/0.5/0.75/1.125/1.5/2/2.5/3
default is 0.75
<br><br>
python eraInterimDownload.py -c 168 -i 2011-10-01 -e 2011-10-02 -E xmin,ymax,xmax,ymin -g 0,125'
<br><br>
--Outfile <Path to downloaded Raster> (default /home/user/eraInterim)' <br><br>
<br><br>
python eraInterimDownload.py -c 168 -i 2011-10-01 -e 2011-10-02 -E xmin,ymax,xmax,ymin -o PATH/TO/FILE'
All downloaded raster are netcdf with a code_DateInit_DateEnd.nc name 
<br><br>
--proxy <proxy : True/False> (default False)
Sometimes a proxy definition is needed for downloading from external network.
When this option is activated, a proxy user/key/site could be defined to overpass it

<h2>Important Notes </h2>

All downloaded and processed images are stored by default in your home directory in eraInterim forlder: ~/eraInterim

To Do List

Improve console output
Allow grid download
Maintain with bug error 

