#include <iostream>
#include <gst/gst.h>

#ifdef GST_STATIC_COMPILATION

extern "C"
{
    GST_PLUGIN_STATIC_DECLARE(coreelements);
}

#endif

int main(int argc, char * argv[])
{
    gst_init(&argc, &argv);
    std::cout << "GStreamer version: " << gst_version_string() << std::endl;

#ifdef GST_STATIC_COMPILATION

    GST_PLUGIN_STATIC_REGISTER(coreelements);

#endif

    GstElement * fakesink = gst_element_factory_make("fakesink", NULL);
    if (!fakesink) {
        std::cerr << "failed to create fakesink element" << std::endl;
        return -1;
    } else {
        std::cout << "fakesink has been created successfully" << std::endl;
    }
    gst_object_unref(GST_OBJECT(fakesink));
    GstElement * fakesrc = gst_element_factory_make("fakesrc", NULL);
    if (!fakesrc) {
        std::cerr << "failed to create fakesrc element" << std::endl;
        return -1;
    } else {
        std::cout << "fakesrc has been created successfully" << std::endl;
    }
    gst_object_unref(GST_OBJECT(fakesrc));
    return 0;
}
