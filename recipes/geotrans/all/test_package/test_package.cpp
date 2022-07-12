// Classification  : UNCLASSIFIED

/******************************************************************************
* Filename        : testCoordinateConversionSample.h
* 
*    Copyright 2007 BAE Systems National Security Solutions Inc. 1989-2006
*                            ALL RIGHTS RESERVED
*
* MODIFICATION HISTORY:
*
* DATE        NAME              DR#               DESCRIPTION
* 
* 05/12/10    S Gillis          BAEts26542        MSP TS MSL-HAE conversion 
*                                                 should use CCS         
* 06/11/10    S. Gillis         BAEts26724        Fixed memory error problem
*                                                 when MSPCCS_DATA is not set 
* 08/26/11    K Ou              BAEts27716        Improved CCS sample code
*
******************************************************************************/

#include <iostream>
#include <string>

#include "CoordinateConversionService.h"
#include "CoordinateSystemParameters.h"
#include "GeodeticParameters.h"
#include "CoordinateTuple.h"
#include "GeodeticCoordinates.h"
#include "CartesianCoordinates.h"
#include "Accuracy.h"
#include "MGRSorUSNGCoordinates.h"
#include "UTMParameters.h"
#include "UTMCoordinates.h"
#include "CoordinateType.h"
#include "HeightType.h"
#include "CoordinateConversionException.h"
/**
 * Sample code to demontrate how to use the MSP Coordinate Conversion Service.
 * 
 * Includes the following conversions:
 *
 * |=============================|=============================|
 * | Source                      | Target                      |
 * |=============================+=============================|
 * | Geodetic (Ellipsoid Height) | Geocentric                  |
 * | Geocentric                  | Geodetic (Ellipsoid Height) |
 * |-----------------------------+-----------------------------|
 * | Geocentric                  | Geodetic (MSL EGM 96 15M)   |
 * |-----------------------------+-----------------------------|
 * | Geodetic (Ellipsoid Height) | Geodetic (MSL EGM 96 15M)   |
 * | Geodetic (MSL EGM 96 15M)   | Geodetic (Ellipsoid Height) |
 * |-----------------------------+-----------------------------|
 * | Geocentric                  | UTM                         |
 * |-----------------------------+-----------------------------|
 * | Geocentric                  | MGRS                        |
 * |-----------------------------+-----------------------------|
 *
 **/


/**
 * Function which uses the given Geodetic (Ellipsoid Height) to Geocentric 
 * Coordinate Conversion Service, 'ccsGeodeticEllipsoidToGeocentric', to
 * convert the given lat, lon, and height to x, y, z coordinates.
 **/
void convertGeodeticEllipsoidToGeocentric(
   MSP::CCS::CoordinateConversionService& ccsGeodeticEllipsoidToGeocentric,
   double lat, 
   double lon, 
   double height, 
   double& x, 
   double& y, 
   double& z)
{    
   MSP::CCS::Accuracy sourceAccuracy;
   MSP::CCS::Accuracy targetAccuracy;
   MSP::CCS::GeodeticCoordinates sourceCoordinates(
      MSP::CCS::CoordinateType::geodetic, lon, lat, height);
   MSP::CCS::CartesianCoordinates targetCoordinates(
      MSP::CCS::CoordinateType::geocentric);

   ccsGeodeticEllipsoidToGeocentric.convertSourceToTarget(
      &sourceCoordinates, 
      &sourceAccuracy, 
      targetCoordinates, 
      targetAccuracy);

   x = targetCoordinates.x();
   y = targetCoordinates.y();
   z = targetCoordinates.z();
}


/**
 * Function which uses the given Geodetic (Ellipsoid Height) to Geocentric 
 * Coordinate Conversion Service, 'ccsGeodeticEllipsoidToGeocentric', to
 * convert the given x, y, z coordinates to a lat, lon, and height.
 **/
void convertGeocentricToGeodeticEllipsoid(
   MSP::CCS::CoordinateConversionService& ccsGeodeticEllipsoidToGeocentric,
   double x, 
   double y, 
   double z, 
   double& lat,
   double& lon, 
   double& height)
{
   MSP::CCS::Accuracy geocentricAccuracy;
   MSP::CCS::Accuracy geodeticAccuracy;
   MSP::CCS::CartesianCoordinates geocentricCoordinates(
      MSP::CCS::CoordinateType::geocentric, x, y, z);
   MSP::CCS::GeodeticCoordinates geodeticCoordinates;

   // Note that the Geodetic (Ellipsoid Height) to Geocentric Coordinate
   // Conversion Service is used here in conjunction with the
   // convertTargetToSource() method (as opposed to a Geocentric to
   // Geodetic (Ellipsoid Height) Coordinate Conversion Service in
   // conjunction with the convertSourceToTarget() method)
   ccsGeodeticEllipsoidToGeocentric.convertTargetToSource(
      &geocentricCoordinates, 
      &geocentricAccuracy,
      geodeticCoordinates, 
      geodeticAccuracy); 

   lat = geodeticCoordinates.latitude();
   lon = geodeticCoordinates.longitude();
   height = geodeticCoordinates.height();
}


/**
 * Function which uses the given Geocentric to Geodetic (MSL EGM 96 15M)
 * Coordinate Conversion Service, 'ccsGeocentricToGeodeticMslEgm96', to
 * convert the given x, y, z coordinates to a lat, lon, and height.
 **/
void convertGeocentricToGeodeticMslEgm96(
   MSP::CCS::CoordinateConversionService& ccsGeocentricToGeodeticMslEgm96,
   double x,
   double y,
   double z, 
   double& lat,
   double& lon, 
   double& height)
{
   MSP::CCS::Accuracy sourceAccuracy;
   MSP::CCS::Accuracy targetAccuracy;
   MSP::CCS::CartesianCoordinates sourceCoordinates(
      MSP::CCS::CoordinateType::geocentric, x, y, z);
   MSP::CCS::GeodeticCoordinates targetCoordinates(
      MSP::CCS::CoordinateType::geodetic, lon, lat, height);

   ccsGeocentricToGeodeticMslEgm96.convertSourceToTarget(
      &sourceCoordinates, 
      &sourceAccuracy, 
      targetCoordinates, 
      targetAccuracy );

   lat = targetCoordinates.latitude();
   lon = targetCoordinates.longitude();
   height = targetCoordinates.height();
}


/**
 * Function which uses the given Geodetic (MSL EGM 96 15M) to Geodetic
 * (Ellipsoid Height) Coordinate Conversion Service,
 * 'ccsMslEgm96ToEllipsoidHeight', to convert the given MSL height at the
 * given lat, lon, to an Ellipsoid height.
 **/
void convertMslEgm96ToEllipsoidHeight(
   MSP::CCS::CoordinateConversionService& ccsMslEgm96ToEllipsoidHeight,
   double lat, 
   double lon,
   double mslHeight,
   double& ellipsoidHeight)
{
   MSP::CCS::Accuracy sourceAccuracy;
   MSP::CCS::Accuracy targetAccuracy;
   MSP::CCS::GeodeticCoordinates sourceCoordinates(
      MSP::CCS::CoordinateType::geodetic, lon, lat, mslHeight);
   MSP::CCS::GeodeticCoordinates targetCoordinates;

   ccsMslEgm96ToEllipsoidHeight.convertSourceToTarget(
      &sourceCoordinates, 
      &sourceAccuracy, 
      targetCoordinates, 
      targetAccuracy);

   ellipsoidHeight = targetCoordinates.height();
}


/**
 * Function which uses the given Geodetic (Ellipsoid Height) to Geodetic
 * (MSL EGM 96 15M) Coordinate Conversion Service,
 * 'ccsEllipsoidHeightToMslEgm96', to convert the given Ellipsoid height at
 * the given lat, lon, to an MSL height.
 **/
void convertEllipsoidHeightToMslEgm96(
   MSP::CCS::CoordinateConversionService& ccsEllipsoidHeightToMslEgm96,
   double lat, 
   double lon, 
   double ellipsoidHeight, 
   double& mslHeight)
{
   MSP::CCS::Accuracy sourceAccuracy;
   MSP::CCS::Accuracy targetAccuracy;

   MSP::CCS::GeodeticCoordinates sourceCoordinates(
      MSP::CCS::CoordinateType::geodetic, lon, lat, ellipsoidHeight);
   MSP::CCS::GeodeticCoordinates targetCoordinates;

   ccsEllipsoidHeightToMslEgm96.convertSourceToTarget(
      &sourceCoordinates, 
      &sourceAccuracy, 
      targetCoordinates, 
      targetAccuracy);

   mslHeight = targetCoordinates.height();
}


/**
 * Function which uses the given Geocentric to UTM Coordinate Conversion
 * Service, 'ccsGeocentricToUtm', to convert the given x, y, z coordinates
 * a UTM zone, hemisphere, Easting and Northing.
 **/
void convertGeocentricToUtm(
   MSP::CCS::CoordinateConversionService& ccsGeocentricToUtm,
   double x,
   double y,
   double z, 
   long& zone,
   char& hemisphere, 
   double& easting,
   double& northing)
{
   MSP::CCS::Accuracy sourceAccuracy;
   MSP::CCS::Accuracy targetAccuracy;
   MSP::CCS::CartesianCoordinates sourceCoordinates(
      MSP::CCS::CoordinateType::geocentric, x, y, z);
   MSP::CCS::UTMCoordinates targetCoordinates;

   ccsGeocentricToUtm.convertSourceToTarget(
      &sourceCoordinates, 
      &sourceAccuracy, 
      targetCoordinates, 
      targetAccuracy);

   zone = targetCoordinates.zone();
   hemisphere = targetCoordinates.hemisphere();
   easting = targetCoordinates.easting();
   northing = targetCoordinates.northing();
}


/**
 * Function which uses the given Geocentric to MGRS Coordinate Conversion
 * Service, 'ccsGeocentricToMgrs', to convert the given x, y, z coordinates
 * to an MGRS string and precision.
 **/
std::string convertGeocentricToMgrs(
   MSP::CCS::CoordinateConversionService& ccsGeocentricToMgrs,
   double x,
   double y,
   double z, 
   MSP::CCS::Precision::Enum& precision)
{
   char* p;
   std::string mgrsString;

   MSP::CCS::Accuracy sourceAccuracy;
   MSP::CCS::Accuracy targetAccuracy;
   MSP::CCS::CartesianCoordinates sourceCoordinates(
      MSP::CCS::CoordinateType::geocentric, x, y, z);
   MSP::CCS::MGRSorUSNGCoordinates targetCoordinates;

   ccsGeocentricToMgrs.convertSourceToTarget(
      &sourceCoordinates, 
      &sourceAccuracy, 
      targetCoordinates, 
      targetAccuracy );

   // Returned value, 'p', points to targetCoordinate's internal character
   // array so assign/copy the character array to mgrsString to avoid
   // introducing memory management issues
   p = targetCoordinates.MGRSString();
   mgrsString = p;

   precision = targetCoordinates.precision();

   return mgrsString;
}


/******************************************************************************
 * Main function
 ******************************************************************************/

int main(int argc, char **argv)
{
   const char* WGE = "WGE";

   // initialize status value to one, indicating an error condition
   int status = 1; 

   std::cout << "Coordinate Conversion Service Sample Test Driver" << std::endl;
   std::cout << std::endl;

   //
   // Coordinate System Parameters 
   //
   MSP::CCS::GeodeticParameters ellipsoidParameters(
      MSP::CCS::CoordinateType::geodetic, 
      MSP::CCS::HeightType::ellipsoidHeight);

   MSP::CCS::CoordinateSystemParameters geocentricParameters(
      MSP::CCS::CoordinateType::geocentric);

   MSP::CCS::GeodeticParameters mslEgm96Parameters(
      MSP::CCS::CoordinateType::geodetic, 
      MSP::CCS::HeightType::EGM96FifteenMinBilinear);

   MSP::CCS::UTMParameters utmParameters(
      MSP::CCS::CoordinateType::universalTransverseMercator, 
      1, 
      0);

   MSP::CCS::CoordinateSystemParameters mgrsParameters(
      MSP::CCS::CoordinateType::militaryGridReferenceSystem);

   //
   // Coordinate Conversion Services 
   //
   MSP::CCS::CoordinateConversionService ccsGeodeticEllipsoidToGeocentric(
      WGE, &ellipsoidParameters, 
      WGE, &geocentricParameters);

   MSP::CCS::CoordinateConversionService ccsGeocentricToGeodeticMslEgm96(
      WGE, &geocentricParameters, 
      WGE, &mslEgm96Parameters);

   MSP::CCS::CoordinateConversionService ccsMslEgm96ToEllipsoidHeight(
      WGE, &mslEgm96Parameters, 
      WGE, &ellipsoidParameters);
   MSP::CCS::CoordinateConversionService ccsEllipsoidHeightToMslEgm96(
      WGE, &ellipsoidParameters, 
      WGE, &mslEgm96Parameters);

   MSP::CCS::CoordinateConversionService ccsGeocentricToUtm(
      WGE, &geocentricParameters, 
      WGE, &utmParameters);
   MSP::CCS::CoordinateConversionService ccsGeocentricToMgrs(
      WGE, &geocentricParameters, 
      WGE, &mgrsParameters);

   try {

      //
      // Geodetic (Ellipsoid Height) to Geocentric
      //
      double lat = 0.56932;
      double lon = -2.04552;
      double height = 0.0;

      double x, y, z;

       std::cout << "convertGeodeticEllipsoidToGeocentric" << '\n';
      convertGeodeticEllipsoidToGeocentric(
         ccsGeodeticEllipsoidToGeocentric, 
         lat, lon, height, 
         x, y, z);

      std::cout << "Convert Geodetic (Ellipsoid Height) to Geocentric" << std::endl
           << std::endl
           << "Lat (radians): " << lat << std::endl
           << "Lon (radians): " << lon << std::endl
           << "Height(m): " << height << std::endl
           << std::endl 
           << "x: " << x << std::endl
           << "y: " << y << std::endl
           << "z: " << z << std::endl
           << std::endl;

      //
      // Geocentric to Geodetic (Ellipsoid Height)
      //

      // function convertGeocentricToGeodeticEllipsoid() reuses the
      // ccsGeodeticEllipsoidToGeocentric instance to perform the reverse
      // conversion
      convertGeocentricToGeodeticEllipsoid(
         ccsGeodeticEllipsoidToGeocentric, 
         x, y, z, 
         lat, lon, height);

      std::cout << "Revert Geocentric To Geodetic (Ellipsoid Height): " << std::endl
           << std::endl
           << "x: " << x << std::endl
           << "y: " << y << std::endl
           << "z: " << z << std::endl
           << std::endl
           << "Lat (radians): " << lat << std::endl
           << "Lon (radians): " << lon << std::endl
           << "Height(m): " << height << std::endl
           << std::endl;


      // reuse ccsGeodeticEllipsoidToGeocentric instance to perform another
      // Geodetic (Ellipsoid Height) to Geocentric conversions
      lat = 0.76388;
      lon = 0.60566;
      height = 11.0;

      convertGeodeticEllipsoidToGeocentric(
         ccsGeodeticEllipsoidToGeocentric, 
         lat, lon, height, 
         x, y, z);

      std::cout << "Convert Geodetic (Ellipsoid Height) to Geocentric" << std::endl
           << std::endl
           << "Lat (radians): " << lat << std::endl
           << "Lon (radians): " << lon << std::endl
           << "Height(m): " << height << std::endl
           << std::endl
           << "x: " << x << std::endl
           << "y: " << y << std::endl
           << "z: " << z << std::endl
           << std::endl;

      // reuse ccsGeodeticEllipsoidToGeocentric instance to perform another
      // Geodetic (Ellipsoid Height) to Geocentric conversions
      lat = 0.71458;
      lon = 0.88791;
      height = 22.0;

      convertGeodeticEllipsoidToGeocentric(
         ccsGeodeticEllipsoidToGeocentric, 
         lat, lon, height, 
         x, y, z);

      std::cout << "Convert Geodetic (Ellipsoid Height) to Geocentric" << std::endl
           << std::endl
           << "Lat (radians): " << lat << std::endl
           << "Lon (radians): " << lon << std::endl
           << "Height(m): " << height << std::endl
           << std::endl
           << "x: " << x << std::endl
           << "y: " << y << std::endl
           << "z: " << z << std::endl
           << std::endl;

      //
      // Geocentric to Geodetic (MSL EGM96 15M)
      //
      x = 3851747;
      y = 3719589;
      z = 3454013;

      double mslHeight;

      convertGeocentricToGeodeticMslEgm96(
         ccsGeocentricToGeodeticMslEgm96, 
         x, y, z, 
         lat, lon, mslHeight);

      std::cout << "Convert Geocentric To Geodetic MSL EGM96: " << std::endl
           << std::endl
           << "x: " << x << std::endl
           << "y: " << y << std::endl
           << "z: " << z << std::endl
           << std::endl
           << "Lat (radians): " << lat << std::endl
           << "Lon (radians): " << lon << std::endl
           << "MSL EGM96 15M Height: " << mslHeight << std::endl
           << std::endl;

      //
      // Geodetic (MSL EGM96 15M) to Geodetic (Ellipsoid Height)   
      //
      convertMslEgm96ToEllipsoidHeight(
         ccsMslEgm96ToEllipsoidHeight, 
         lat, lon, mslHeight, 
         height);

      std::cout << "Convert Geodetic (MSL EMG96 15M Height) To Geodetic (Ellipsoid Height)" << std::endl
           << std::endl
           << "Lat (radians): " << lat << std::endl
           << "Lon (radians): " << lon << std::endl
           << "MSL EGM96 15M Height: " << mslHeight << std::endl
           << std::endl
           << "Ellipsoid Height: " << height << std::endl
           << std::endl;

      //
      // Geodetic (Ellipsoid Height) to Geodetic (MSL EMG96 15M)
      //
      convertEllipsoidHeightToMslEgm96(
         ccsEllipsoidHeightToMslEgm96, 
         lat, lon, height, 
         mslHeight);

      std::cout << "Revert Geodetic (Ellipsoid Height) To Geodetic (MSL EGM96 15M) Height" << std::endl
           << std::endl
           << "Lat (radians): " << lat << std::endl
           << "Lon (radians): " << lon << std::endl
           << "Height(m): " << height << std::endl
           << std::endl
           << "MSL EGM96 15M Height: " << mslHeight << std::endl
           << std::endl;

      //
      // Geocentric to UTM
      //
      long zone;
      char hemi;
      double easting, northing;
      convertGeocentricToUtm(
         ccsGeocentricToUtm, 
         x, y, z, 
         zone, hemi, easting, northing);

      std::cout << "Convert Geocentric To UTM: " << std::endl
           << std::endl
           << "x: " << x << std::endl
           << "y: " << y << std::endl
           << "z: " << z << std::endl
           << std::endl
           << "Zone: " << zone << std::endl
           << "Hemisphere: " << hemi << std::endl
           << "Easting: " << easting << std::endl
           << "Northing: " << northing<< std::endl
           << std::endl;

      //
      // Geocentric to MGRS
      //
      std::string mgrsString;
      MSP::CCS::Precision::Enum precision;

      mgrsString = convertGeocentricToMgrs(
         ccsGeocentricToMgrs, 
         x, y, z, 
         precision);

      std::cout << "Convert Geocentric To MGRS: " << std::endl
           << std::endl
           << "x: " << x << std::endl
           << "y: " << y << std::endl
           << "z: " << z << std::endl
           << std::endl
           << "MGRS: " << mgrsString << std::endl
           << "Precision: " << precision << std::endl
           << std::endl;
      
      // set status value to zero to indicate successful completion
      status = 0;

   } catch(MSP::CCS::CoordinateConversionException& e) {
      // catch and report any exceptions thrown by the Coordinate
      // Conversion Service
      std::cerr
           << "ERROR: Coordinate Conversion Service exception encountered - " 
           << e.getMessage() 
           << std::endl;

   } catch(std::exception& e) {
      // catch and report any unexpected exceptions thrown
      std::cerr << "ERROR: Unexpected exception encountered - "
                << e.what() << std::endl;
   }

   return status;
}

// Classification  : UNCLASSIFIED
