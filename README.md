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

<u>Four paramaters are mandatory: <br><br></u>
<b> --Code of Parameters <EraInterimCode></b><br>
A list of code which define parameters desired. Code reference can be found on http://old.ecmwf.int/publications/library/ecpublications/_pdf/era/era_report_series/RS_1_v2.pdf<br>
</u>CODE PARAMETERS Exemple :</u><br>
total precipitation  :  228 <i>[m of water]</i><br>
2 meters temperature  :  167 <i>[K]</i><br>
maximum 2m temperature since last post-processing step : 201 <i>[K]</i><br>
minimum 2m temperature since last post-processing step : 202 <i>[K]</i><br>
surface pressure : 134 <i>[Pa]</i><br>
2 meters dewpoint : 168 <i>[K]</i><br>
10 meters eastward wind component X X 165 <i>[m s-1]</i><br>
10 meters northward wind component X X 166 <i>[m s-1]</i>
<br><br>
<b>--Interval needed : </b><br>
init date <dateStart YYYY-MM-DD>' AND end date <dateEnd YY-MM-DD>'
<br><br> 
<b>--Area needed </b><br>
shapefile <pathToShapefile> (srs is not important because it will be reprojected in WGS84)
OR 
--Extend <xmin,ymax,xmax,ymin> in WGS84
<br><br>

<b>EXAMPLES :</b><br>
<i>--temperature on a shapefile during the first to the second of january <br></i>
python eraInterimDownload.py -c 167 -i 2014-01-01 -e 2014-01-02 -s PATH_TO_SHAPE'<br>
<i>--pressure on a area  during the first month of 2015 on a specific extend<br></i>
python eraInterimDownload.py -c 134 -i 2015-01-01 -e 2015-02-01 -E xmin,ymax,xmax,ymin'<br>
<br><br>
<u>Five paramaters are optional: </u><br>
<b>--Time <EraInterim Time> (default 00)'</b><br>
The time for starting modelisation. It could be 00h 06h,12h or 18h (selection in 00,06,12,18). 
Default is 0. 
A list is possible for that parameter
<br><br>
python eraInterimDownload.py -c 168 -i 2013-11-08 -e 2013-12-09 -E xmin,ymax,xmax,ymin -t 00,06,12,18'
<br>
<b>--Step <EraInterim Time> (default 0)' </b><br>
The step of modeling. Some parameters are not possible within some of the possibilities. 
Check the documentation for more information.
default is 0. 
A list is possible for that parameter
<br><br>
python eraInterimDownload.py -c 168 -i 2013-11-08 -e 2013-12-09 -E xmin,ymax,xmax,ymin -p 0,6'
<br>
<b>--Grid <grid spacing on °.arc> (default 0)'</b> 
<br><br>
The spacing of final raster. grid possible : 0.125/0.25/0.5/0.75/1.125/1.5/2/2.5/3
default is 0.75
<br><br>
python eraInterimDownload.py -c 168 -i 2011-10-01 -e 2011-10-02 -E xmin,ymax,xmax,ymin -g 0,125'
<br>
<b>--Outfile <Path to downloaded Raster> (default /home/user/eraInterim)'</b>
<br><br>
python eraInterimDownload.py -c 168 -i 2011-10-01 -e 2011-10-02 -E xmin,ymax,xmax,ymin -o PATH/TO/FILE'
All downloaded raster are netcdf with a code_DateInit_DateEnd.nc name 
<br>
<b>--proxy <proxy : True/False></b> (default False)
<br><br>
Sometimes a proxy definition is needed for downloading from external network.
When this option is activated, a proxy user/key/site could be defined to overpass it
<br><br>
<h2>Important Notes </h2>

All downloaded and processed images are stored by default in your home directory in eraInterim forlder: ~/eraInterim

To Do List

Improve console output
Allow grid download
Maintain with bug error 

