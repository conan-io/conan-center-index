#include <gphoto2/gphoto2-camera.h>
#include <gphoto2/gphoto2-abilities-list.h>

int main() {
    GPContext* context;
    CameraAbilitiesList* list;
    Camera* camera;
    int ret;

    context = gp_context_new();
    ret = gp_abilities_list_new(&list);
    if (ret != GP_OK) {
        return 1;
    }
    ret = gp_abilities_list_load(list, context);
    if (ret != GP_OK) {
        return 1;
    }
    int count = gp_abilities_list_count(list);
    if (count == 0) {
        return 1;
    }
    gp_camera_new(&camera);
    gp_camera_free(camera);
    gp_abilities_list_free(list);
    return 0;
}
