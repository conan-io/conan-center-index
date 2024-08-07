/**********************************************************
* Copyright 1989-2004 Earth Resource Mapping Pty Ltd.
*
* This document contains unpublished source code of
* Earth Resource Mapping Pty Ltd. This notice does
* not indicate any intention to publish the source
* code contained herein.
*
* Use of this product is subject to End-User License Agreement for Earth
* Resource Mapping Software.  Use of the examples provided to design, develop,
* and test your own applications is bound by the terms of the license.  Please
* refer to license.txt under the program folder for the contents
* of the license. The license contains important rights and obligations and
* should be read carefully.  If you do not agree to be bound by the terms and
* conditions of the license, you must immediately uninstall and destroy all
* copies of the product.
*
** FILE:   	dexample1.c
** CREATED:	5th April 1999
** AUTHOR: 	NCS
**
** PURPOSE:	Example program demonstrating use of the BLOCKING
**			interface into the NCSECW library
**
** COMPILE:	To compile this example, use VC++ 6.0, and set
**			the following parameters under the Project Settings
**			menu:
**
**			DEBUG:
**				C,C++/Code Generation:		Debug Multithreaded DLL
**				Link/General/Object Files:	add "NCSecw.lib"
**
**			RELEASE:
**				C,C++/Code Generation:		Multithreaded DLL
**				Link/General/Object Files:	add "NCSecw.lib"
**
**			To run the program, specify a path to a local or
**			remote ECW file, for example:
**				ecwp://earth.ermapper.com/images/usa/SanDiego3i.ecw
**
** NOTES:
**	(1) This example demonstrates the BLOCKING interface into the NCSECW
**	library.  The application opens the view, reads the view, then reads
**	another view, and so on.
**
**	(2) This example uses the BIL read call; you could instead use the RGB call if
**	you want to the library to always return a straight RGB image regardless of source.
**
**	EDITS
**	[01] 10May01 mg The boundary checking for end_x and end_y within the image area were incorrect.
**
 *******************************************************/


#include <time.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <stdio.h>
#include <stdlib.h>
#include "NCSECWClient.h"
#include "NCSErrors.h"

#define MAX_WINDOW	333			// max size of a window view for testing
#define MAX_REGION_READS 10		// max number of reads of a file view for a client
#define RAND() ((double) rand() / (double) RAND_MAX)

int setup_report(int argc, char *argv[],
			char **p_p_input_ecw_filename);
int test_openview( char *szInputFilename, BOOLEAN bRandomReads, BOOLEAN bReportTime );

int main(int argc, char **argv)
{

	char	*szInputFilename;
	int		nError = 0;

	/*
	 * 	Initialize the library if we are linking statically
	 */
	NCSecwInit();

  	/*
	**	Find file names, and open the output
	*/
	if( setup_report(argc, argv,
			&szInputFilename) )
		return( 1 );

	nError = test_openview(szInputFilename, FALSE, TRUE);
	if( nError ) {
		printf("Openview test returned an error\n");
		return(nError);
	}

	NCSecwShutdown();
	return(0);
}



int setup_report(int argc, char *argv[],
			char **ppInputFilename)
{
	if (argc != 2) {
	  printf("Usage:  %s file.ecw\n", argv[0]);
	  return(1);
	}

	*ppInputFilename = argv[1];
	return(0);
}

/*****************************************************************
**	NCS Test: READING a file
*****************************************************************/

int test_openview( char *szInputFilename, BOOLEAN bRandomReads, BOOLEAN bReportTime )
{

	NCSFileView *pNCSFileView;
	NCSFileViewFileInfo	*pNCSFileInfo;

	NCSError eError = NCS_SUCCESS;
	UINT8	**p_p_output_line = NULL;
	UINT8	*p_output_buffer = NULL;
	UINT32	x_size, y_size, number_x, number_y;
	UINT32	start_x, start_y, end_x, end_y;
	UINT32	line;
	int		regions;
	double	total_pixels = 0.0;
	UINT32	band;
	UINT32	nBands;
	UINT32	*band_list = NULL;	/* list of individual bands to read, may be subset of actual bands */

	clock_t	start_time, mark_time;

	printf("ECW READ EXAMPLE\n");
	start_time = mark_time = clock();
	/*
	**	Open the input NCSFileView
	*/
	eError = NCScbmOpenFileView(szInputFilename, &pNCSFileView, NULL);

	if (eError != NCS_SUCCESS) {
		printf("Could not open view for file:%s\n",szInputFilename);
		printf("Error = %s\n", NCSGetErrorText(eError));
		return(1);
	}
	NCScbmGetViewFileInfo(pNCSFileView, &pNCSFileInfo);
	x_size = pNCSFileInfo->nSizeX;
	y_size = pNCSFileInfo->nSizeY;
	nBands = pNCSFileInfo->nBands;
	printf("Input file is [%ld x %ld by %d bands]\n",
		(long)x_size, (long)y_size, nBands);

	// Have to set up the band list. Compatible with ER Mapper's method.
	// In this example we always request all bands.
	band_list = (UINT32 *) malloc(sizeof(UINT32) * nBands);
	if( !band_list ) {
		printf("Error - unable to malloc band list\n");
		NCScbmCloseFileView(pNCSFileView);
		return(1);
	}
	for( band = 0; band < nBands; band++ )
		band_list[band] = band;

// All of image
	start_x = 0;		start_y = 0;
	end_x = x_size - 1;	end_y = y_size - 1;
	number_x = x_size;	number_y = y_size;

	// do many region reads as tests
	if( bRandomReads )
		regions = 10;
	else
		regions = 100;
//		regions = 5000;

	while( regions -- ) {
		{	// work out a random region to read
			number_x = number_y = 512;
			// define a random region and size
			start_x = (UINT32) (RAND() * x_size);
			end_x	= (UINT32) (RAND() * (x_size - start_x)) + start_x;
			start_y = (UINT32) (RAND() * y_size);
			end_y	= (UINT32) (RAND() * (y_size - start_y)) + start_y;

			// make a square view area
			if( (end_x - start_x) < MAX_WINDOW ) {
				end_x = start_x + MAX_WINDOW;
				if( end_x >= x_size ) { // [01]
					start_x = x_size - MAX_WINDOW;
					end_x = x_size-1;
				}
			}
			if( (end_y - start_y) < MAX_WINDOW ) {
				end_y = start_y + MAX_WINDOW;
				if( end_y >= y_size ) { // [01]
					start_y = y_size - MAX_WINDOW;
					end_y = y_size-1;
				}
			}
			if( (end_x - start_x) < (end_y - start_y) )
				end_y = start_y + (end_x - start_x);
			else
				end_x = start_x + (end_y - start_y);
			number_x = number_y = MAX_WINDOW;

		}

		printf("Region %4d: [%d,%d] to [%d,%d] for [%d,%d]\n",
			regions, start_x, start_y, end_x, end_y, number_x, number_y);

		eError = NCScbmSetFileView(pNCSFileView,
						nBands, band_list,
						start_x, start_y, end_x, end_y,
						number_x, number_y);
		if( eError != NCS_SUCCESS) {
			printf("Error while setting file view to %d bands, TL[%d,%d] BR[%d,%d], Window size [%d,%d]\n",
				nBands, start_x, start_y, end_x, end_y, number_x, number_y);
			printf("Error = %s\n", NCSGetErrorText(eError));
			NCScbmCloseFileView(pNCSFileView);
			free(band_list);
			return(1);
		}

		p_output_buffer = (UINT8 *) malloc( sizeof(UINT8) * number_x * nBands);
		p_p_output_line = (UINT8 **) malloc( sizeof(UINT8 *) * nBands);

		if( !p_p_output_line || !p_output_buffer) {
			printf("Malloc error for output buffers\n");
			NCScbmCloseFileView(pNCSFileView);
			free(band_list);
			if( p_p_output_line )
				free((char *) p_p_output_line);
			if( p_output_buffer )
				free((char *) p_output_buffer);
			return(1);
		}

		for(band = 0; band < nBands; band++ )
			p_p_output_line[band] = p_output_buffer + (band * number_x);

		/*
		**	Read each line of the compressed file
		*/
		for( line = 0; line < number_y; line++ ) {
			NCSEcwReadStatus eReadStatus;
			eReadStatus = NCScbmReadViewLineBIL( pNCSFileView, p_p_output_line);
			if (eReadStatus != NCSECW_READ_OK) {
				printf("Read line error at line %d\n",line);
				printf("Status code = %d\n", eReadStatus);
				NCScbmCloseFileView(pNCSFileView);
				free(band_list);
				free((char *) p_p_output_line);
				free((char *) p_output_buffer);
				return(1);
			}
		}
		free((char *) p_p_output_line);
		free((char *) p_output_buffer);

		if( bReportTime ) {
			double	pixels, seconds, pixels_per_second, seconds_per_megapixel;

			// time for this run
			seconds = ((double) (clock() - mark_time)) / (double) CLOCKS_PER_SEC;
			if( seconds == 0 )
				seconds = 0.01;
			pixels = (double) number_x * (double) number_y;
			pixels_per_second = pixels / seconds;
			seconds_per_megapixel = seconds / (pixels / 1000000.0);
			printf("Region time:%5.2lf sec.%5.2lf Mpixels/sec. %4.2lf secs/Mpixel (%6.2lf Mpixels)\n",
				seconds, pixels_per_second / 1000000, seconds_per_megapixel, (pixels/1000000));
			// cumulative time
			mark_time = clock();
			seconds = ((double) (mark_time - start_time)) / (double) CLOCKS_PER_SEC;
			if( seconds == 0 )
				seconds = 0.001;
			total_pixels	+= pixels;
			pixels_per_second = total_pixels / seconds;
			seconds_per_megapixel = seconds / (total_pixels / 1000000.0);
		}
	}

	if( bReportTime ) {
		double	seconds, pixels_per_second, seconds_per_megapixel;

		// cumulative time
		mark_time = clock();
		seconds = ((double) (mark_time - start_time)) / (double) CLOCKS_PER_SEC;
		if( seconds == 0 )
			seconds = 0.001;
		pixels_per_second = total_pixels / seconds;
		seconds_per_megapixel = seconds / (total_pixels / 1000000.0);
		printf("ALL    time:%5.2lf sec.%5.2lf Mpixels/sec. %4.2lf secs/Mpixel (%6.2lf Mpixels)\n",
			seconds, pixels_per_second / 1000000, seconds_per_megapixel, total_pixels / 1000000);
	}

	// Make the second argument below TRUE if this is the last view of the file and you
	// want the file closed, otherwise it will be kept open in the cache. This can
	// sometimes be an problem when writing plugins.
	//
	NCScbmCloseFileViewEx(pNCSFileView, FALSE);
	free(band_list);

	return(0);
}
