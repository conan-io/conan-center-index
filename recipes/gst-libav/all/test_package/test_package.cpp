#include <gst/gst.h>
#include <gst/gstplugin.h>

#ifdef GST_LIBAV_STATIC

extern "C"
{
    GST_PLUGIN_STATIC_DECLARE(libav);
}

#endif

#include <iostream>

int main(int argc, char * argv[])
{
    gst_init(&argc, &argv);

#ifdef GST_LIBAV_STATIC

    GST_PLUGIN_STATIC_REGISTER(libav);

#endif

    GstElement * avdec_mjpeg = gst_element_factory_make("avdec_mjpeg", NULL);
    if (!avdec_mjpeg) {
        std::cerr << "failed to create avdec_mjpeg element" << std::endl;
        return -1;
    } else {
        std::cout << "avdec_mjpeg has been created successfully" << std::endl;
    }
    gst_object_unref(GST_OBJECT(avdec_mjpeg));
    return 0;
}
