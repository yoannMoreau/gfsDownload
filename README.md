=======
# gfsDownload
Tools for downloading gfs meteo parameters modelling estimation on an area and on a specific time.
GFS is a product of NCEP,NOAA and provide a full range of product which are describe in 
http://www.nco.ncep.noaa.gov/pmb/products/gfs/

 
<h2>Installation<b></h2>

mkdir PATH/TO/INSTALL <br>
cd  PATH/TO/INSTALL/gfsDownload <br>
git clone git+git://github.com/yoannMoreau/gfsDownload.git <br>
sudo apt-get install grib-api
sudo apt-get install libopenjpeg
sudo apt-get install pyproj
python python/GFSDownload.py -help <br>

( or you cas Use pip to install gfsDownload )

<h2>Overview: What can gfsDownload do?</h2>

gfsDownload has a main function, allow download of parameters on a area in an automatic way

<u>Four paramaters are mandatory: <br><br></u>
<b> --Code of Parameters <gfsDownload></b><br>
A list of code which define parameters desired. Code reference can be found on :<br>
<a href="http://www.nco.ncep.noaa.gov/pmb/products/gfs/gfs_upgrade/gfs.t06z.pgrb2.0p25.anl.shtml">For analyse </a><br>
<a href="http://www.nco.ncep.noaa.gov/pmb/products/gfs/gfs_upgrade/gfs.t06z.pgrb2.0p25.f006.shtml">For forecast </a><br>
</u>CODE PARAMETERS Exemple :</u><br>
total precipitation  :  APCP <i>[m of water]</i><br>
temperature  :  TMP <i>[K]</i><br>
pressure : PRES <i>[Pa]</i><br>
dewpoint : DPT <i>[K]</i><br>
eastward wind component UGRD <i>[m s-1]</i><br>
northward wind component VGRD <i>[m s-1]</i>
<br><br>
<b>--Interval needed : </b><br>
init date <dateStart YYYY-MM-DD>' AND end date <dateEnd YY-MM-DD>'
these parameters should be in a 14 days range from maximum date today
<br><br> 
<b>--Area needed </b><br>
shapefile <pathToShapefile> (srs is not important because it will be reprojected in WGS84)
OR 
--Extend <xmin,ymax,xmax,ymin> in WGS84
<br><br>

<b>EXAMPLES :</b><br>
<i>--temperature on a shapefile during the first to the second of january <br></i>
python GFSDownload.py -c TMP -i 2014-01-01 -e 2014-01-02 -s PATH_TO_SHAPE'<br>
<i>--pressure and dewPoint on a area  during the first month of 2015 on a specific extend<br></i>
python eraInterimDownload.py -c PRES,DPT -i 2015-01-01 -e 2015-02-01 -E xmin,ymax,xmax,ymin'<br>
<br><br>
<u>Five paramaters are optional: </u><br><br>
<b>--Step <gfsDownload Step> (default 0)' </b><br>
The step of modeling. 
The step of itarate data over the days choosen ! 
default is 0,6,12,18. 
A list is possible for that parameter
<br><br>
python GFSDownload.py -c TMP -i 2013-11-08 -e 2013-12-09 -E xmin,ymax,xmax,ymin -p 0,6'
<br><br>
<b>--Grid <grid spacing on °.arc> (default 0)'</b> 
<br><br>
The spacing of final raster. grid possible :  0.25/0.5/1/2.5
default is 0.25
<br><br>
python GFSDownload.py -c TMP -i 2015-04-19 -e 2015-04-19 -E xmin,ymax,xmax,ymin -g 0.5'
<br><br>
<b>--Outfile <Path to downloaded Raster> (default /home/user/eraInterim)'</b>
<br><br>
python GFSDownload.py -c PRES -i 2011-10-01 -e 2011-10-02 -E xmin,ymax,xmax,ymin -o PATH/TO/FILE'
All downloaded raster are tif with a VAR_LEVEL_DateInit_DateEnd.tif name 
<br><br>
<b>--proxy <proxy : True/False></b> (default False)
<br><br>
Sometimes a proxy definition is needed for downloading from external network.
When this option is activated, a proxy user/key/site could be defined to overpass it
<br><br>
<h2>Important Notes </h2>

All downloaded and processed images are stored by default in your home directory in GFS forlder: ~/GFS
<br><br>
To Do List
<br><br>
Improve console output<br>
Maintain with bug error <br>

