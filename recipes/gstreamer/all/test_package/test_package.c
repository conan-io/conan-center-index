#include <stdlib.h>
#include <stdio.h>
#include <gst/gst.h>

#ifdef GST_STATIC_COMPILATION
GST_PLUGIN_STATIC_DECLARE(coreelements);
#endif

int main(int argc, char * argv[])
{
    gst_init(&argc, &argv);
    printf("GStreamer version: %s\n", gst_version_string());

#ifdef GST_STATIC_COMPILATION
    GST_PLUGIN_STATIC_REGISTER(coreelements);
#endif

    GstElement * fakesink = gst_element_factory_make("fakesink", NULL);
    if (!fakesink) {
        printf("failed to create fakesink element\n");
        return EXIT_FAILURE;
    } else {
        printf("fakesink has been created successfully\n");
    }
    gst_object_unref(GST_OBJECT(fakesink));
    GstElement * fakesrc = gst_element_factory_make("fakesrc", NULL);
    if (!fakesrc) {
        printf("failed to create fakesrc element\n");
        return EXIT_FAILURE;
    } else {
        printf("fakesrc has been created successfully\n");
    }
    gst_object_unref(GST_OBJECT(fakesrc));
    return EXIT_SUCCESS;
}
