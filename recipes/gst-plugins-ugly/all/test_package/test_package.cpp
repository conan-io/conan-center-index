#include <gst/gst.h>
#include <gst/gstplugin.h>

#ifdef GST_PLUGINS_UGLY_STATIC

extern "C"
{
    GST_PLUGIN_STATIC_DECLARE(asf);
}

#endif

#include <iostream>

int main(int argc, char * argv[])
{
    gst_init(&argc, &argv);

#ifdef GST_PLUGINS_UGLY_STATIC

    GST_PLUGIN_STATIC_REGISTER(asf);

#endif

    GstElement * asfdemux = gst_element_factory_make("asfdemux", NULL);
    if (!asfdemux) {
        std::cerr << "failed to create asfdemux element" << std::endl;
        return -1;
    } else {
        std::cout << "asfdemux has been created successfully" << std::endl;
    }
    gst_object_unref(GST_OBJECT(asfdemux));
    return 0;
}
