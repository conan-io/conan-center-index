#include <OpenImageIO/imagecache.h>

int main()
{
    OIIO::ImageCache* cache = OIIO::ImageCache::create();
    OIIO::ImageCache::destroy(cache);
}
