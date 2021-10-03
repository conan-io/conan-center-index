#include <gphoto2/gphoto2-camera.h>

int main() {
    Camera *camera;
    int	ret;
    char *owner;
    GPContext *context;
    CameraText text;

    context = gp_context_new();
    gp_camera_new (&camera);
    return 0;
}
