#include <gst/gst.h>
#include <gst/gstplugin.h>

#ifdef GST_PLUGINS_RS_STATIC
extern "C"
{
    GST_PLUGIN_STATIC_DECLARE(rswebrtc);
}
#endif

#include <iostream>

void list_plugins()
{
    GstRegistry *registry = gst_registry_get();
    if (!registry) {
        std::cerr << "Failed to get GStreamer registry" << std::endl;
        exit(-1);
    }
    GList *plugins = gst_registry_get_plugin_list(registry);
    std::cout << "Found plugins:" << std::endl;
    for (GList *plugin_item = plugins; plugin_item != nullptr; plugin_item = plugin_item->next) {
        GstPlugin *plugin = GST_PLUGIN(plugin_item->data);
        const gchar *name = gst_plugin_get_name(plugin);
        const gchar *desc = gst_plugin_get_description(plugin);
        std::cout << "- " << name;
        if (desc) {
            std::cout << " (" << desc << ")";
        }
        std::cout << std::endl;
    }
    gst_plugin_list_free(plugins);
}

int main(int argc, char * argv[])
{
    gst_init(&argc, &argv);

#ifdef GST_PLUGINS_RS_STATIC
    GST_PLUGIN_STATIC_REGISTER(rswebrtc);
#endif

    list_plugins();

    GstElement * rswebrtc = gst_element_factory_make("rswebrtc", NULL);
    if (!rswebrtc) {
        std::cerr << "failed to create rswebrtc element" << std::endl;
        return -1;
    } else {
        std::cout << "rswebrtc has been created successfully" << std::endl;
    }
    gst_object_unref(GST_OBJECT(rswebrtc));
    return 0;
}
