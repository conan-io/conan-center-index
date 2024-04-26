#include <pangolin/display/display.h>
#include <pangolin/display/view.h>
#include <pangolin/handler/handler.h>
#include <pangolin/gl/gldraw.h>

int main()
{
    static const int w = 640;
    static const int h = 480;
    pangolin::GlTexture color_buffer(w, h);
    pangolin::GlRenderBuffer depth_buffer(w, h);
    pangolin::GlFramebuffer fbo_buffer(color_buffer, depth_buffer);
}
