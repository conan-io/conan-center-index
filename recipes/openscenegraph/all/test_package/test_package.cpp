#include <cstdlib>

#include <osg/ref_ptr>
#include <osgDB/ReaderWriter>
#include <osgDB/Registry>

#ifdef OSG_LIBRARY_STATIC
USE_OSGPLUGIN ( bmp )
#	if WITH_PNG == 1
USE_OSGPLUGIN ( png )
#	endif
#	if WITH_DCMTK == 1
USE_OSGPLUGIN ( dicom )
#	endif
#endif

int main ( int argc, char** argv )
{
	osg::ref_ptr< osgDB::ReaderWriter > reader_writer;

	reader_writer = osgDB::Registry::instance()->getReaderWriterForExtension ( "bmp" );
	if ( !reader_writer.valid() )
	{
		std::exit ( 1 );
	}

	reader_writer = osgDB::Registry::instance()->getReaderWriterForExtension ( "png" );
	if ( reader_writer.valid() != bool ( WITH_PNG ) )
	{
		std::exit ( 1 );
	}

	reader_writer = osgDB::Registry::instance()->getReaderWriterForExtension ( "dicom" );
	if ( reader_writer.valid() != bool ( WITH_DCMTK ) )
	{
		std::exit ( 1 );
	}
	return 0;
}
