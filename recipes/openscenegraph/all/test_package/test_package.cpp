#include <iostream>

#include <osg/ref_ptr>
#include <osgDB/ReaderWriter>
#include <osgDB/Registry>

#ifdef OSG_LIBRARY_STATIC
USE_OSGPLUGIN ( bmp )
#	if WITH_JPEG == 1
USE_OSGPLUGIN ( jpeg )
#	endif
#	if WITH_JASPER == 1
USE_OSGPLUGIN ( jp2 )
#	endif
#	if WITH_OPENEXR == 1
USE_OSGPLUGIN ( exr )
#	endif
#	if WITH_GIF == 1
USE_OSGPLUGIN ( gif )
#	endif
#	if WITH_PNG == 1
USE_OSGPLUGIN ( png )
#	endif
#	if WITH_TIFF == 1
USE_OSGPLUGIN ( tiff )
#	endif
#	if WITH_GDAL == 1
USE_OSGPLUGIN ( gdal )
#	endif
#	if WITH_GTA == 1
USE_OSGPLUGIN ( gta )
#	endif
#	if WITH_DCMTK == 1
USE_OSGPLUGIN ( dicom )
#	endif
#	if WITH_CURL == 1
USE_OSGPLUGIN ( curl )
#	endif
#	if WITH_ZLIB == 1
USE_OSGPLUGIN ( GZ )
#	endif
#	if WITH_FREETYPE == 1
USE_OSGPLUGIN ( freetype )
#	endif
#endif

namespace
{
int check_plugin ( char const* const ext, bool const expected )
{
	osg::ref_ptr< osgDB::ReaderWriter > const reader_writer = osgDB::Registry::instance()->getReaderWriterForExtension ( ext );

	std::cout << "Looking for " << ext << " support: ";
	if ( !reader_writer.valid() )
	{
		std::cout << "not ";
	}
	std::cout << "found";
	if ( reader_writer.valid() != expected )
	{
		std::cout << " (expected ";
		if ( !expected )
		{
			std::cout << "not ";
		}
		std::cout << "found)";
	}
	std::cout << std::endl;

	return reader_writer.valid() == expected ? 0 : 1;
}
} // namespace

int main ( int argc, char** argv )
{
	int res = 0;

	res |= check_plugin ( "bmp", true );
	res |= check_plugin ( "jpg", WITH_JPEG );
	res |= check_plugin ( "jpc", WITH_JASPER );
	res |= check_plugin ( "exr", WITH_OPENEXR );
	res |= check_plugin ( "gif", WITH_GIF );
	res |= check_plugin ( "png", WITH_PNG );
	res |= check_plugin ( "tif", WITH_TIFF );
	res |= check_plugin ( "gdal", WITH_GDAL );
	res |= check_plugin ( "gta", WITH_GTA );
	res |= check_plugin ( "dcm", WITH_DCMTK );
	res |= check_plugin ( "curl", WITH_CURL ); // Replace with a better test that checks for supported protocols
	res |= check_plugin ( "osgz", WITH_ZLIB );
	res |= check_plugin ( "ttf", WITH_FREETYPE );

	return res;
}
