#include <gst/gst.h>
#include <gst/gstplugin.h>

#ifdef GST_PLUGINS_BAD_STATIC

extern "C"
{
    GST_PLUGIN_STATIC_DECLARE(mpegpsdemux);
}

#endif

#include <iostream>

int main(int argc, char * argv[])
{
    gst_init(&argc, &argv);

#ifdef GST_PLUGINS_BAD_STATIC

    GST_PLUGIN_STATIC_REGISTER(mpegpsdemux);

#endif

    GstElement * mpegpsdemux = gst_element_factory_make("mpegpsdemux", NULL);
    if (!mpegpsdemux) {
        std::cerr << "failed to create mpegpsdemux element" << std::endl;
        return -1;
    } else {
        std::cout << "mpegpsdemux has been created successfully" << std::endl;
    }
    gst_object_unref(GST_OBJECT(mpegpsdemux));
    return 0;
}
