#if 0
#include <stdbool.h>
#include <stdio.h>
#include <gst/gst.h>

typedef struct
{
    GstElement* pipeline;
    GMainLoop* loop;
} data_t;

static gboolean bus_message_callback(GstBus* bus, GstMessage* message, gpointer user_data)
{
    data_t* data = (data_t*)user_data;
    switch (GST_MESSAGE_TYPE(message))
    {
        case GST_MESSAGE_ERROR:
        {
            GError* error = NULL;
            gchar* debug_info = NULL;
            gst_message_parse_error(message, &error, &debug_info);
            printf("Error received from element %s: %s\n", GST_OBJECT_NAME(message->src), error->message);
            printf("Debugging information: %s\n", debug_info ? debug_info : "none");
            g_clear_error(&error);
            g_free(debug_info);
            g_main_loop_quit(data->loop);
            break;
        }
        case GST_MESSAGE_EOS:
        {
            printf("End-Of-Stream reached\n");
            gst_element_set_state(data->pipeline, GST_STATE_NULL);
            g_main_loop_quit(data->loop);
            break;
        }
        default:
            break;
    }
    return TRUE;
}

gboolean timeout_quit(gpointer user_data)
{
    data_t* data = (data_t*)user_data;
    gst_element_send_event(data->pipeline, gst_event_new_eos());
    return FALSE;
}

int main (int argc, char **argv)
{
    data_t data;
    GError* error = NULL;
    if (!gst_init_check(&argc, &argv, &error))
    {
        printf("Failed to initialize GStreamer: %s\n", error->message);
        g_error_free(error);
        return 1;
    }

    data.loop = g_main_loop_new(NULL, FALSE);
    if (!data.loop)
    {
        printf("Failed to create main loop\n");
        return 1;
    }

    data.pipeline = gst_parse_launch("videotestsrc ! videoconvert ! autovideosink", NULL);
    if (!data.pipeline)
    {
        printf("Failed to create pipeline\n");
        return 1;
    }

    //GstBus* bus = gst_pipeline_get_bus(GST_PIPELINE (data.pipeline));
    //gst_bus_add_signal_watch(bus);
    //g_signal_connect(G_OBJECT(bus), "message", G_CALLBACK(bus_message_callback), &data);
    //gst_object_unref(GST_OBJECT(bus));

    
    //g_timeout_add(10000, (GSourceFunc)timeout_quit, &data);

    gst_element_set_state(data.pipeline, GST_STATE_PLAYING);

    g_main_loop_run(data.loop);

    //gst_object_unref(data.pipeline);
    //g_main_loop_unref(data.loop);

    gst_deinit();

    return 0;
}
#else
#include <stdbool.h>
#include <stdio.h>
#include <gst/gst.h>

typedef struct
{
    GstElement* pipeline;
    GMainLoop* loop;
} data_t;

int main(int argc, char **argv)
{
    data_t data;
    GError* error = NULL;
    if (!gst_init_check(NULL, NULL, &error))
    {
        printf("Failed to initialize GStreamer: %s\n", error->message);
        g_error_free(error);
        return 1;
    }

    data.loop = g_main_loop_new(NULL, FALSE);
    if (!data.loop)
    {
        printf("Failed to create main loop\n");
        return 1;
    }
    return 0;
} 
#endif

