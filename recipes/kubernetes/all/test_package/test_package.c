#include <kubernetes/api/CoreV1API.h>
#include <kubernetes/model/v1_pod.h>
#include <kubernetes/config/kube_config.h>

int main(void) {
    /*
     * Try to create a kubernetes apiClient.
     * It doesn't matter whether creates it or not.
     * The important thing is that it doesn't fail when use the library.
    */
    char *basePath = NULL;
    sslConfig_t *sslConfig = NULL;
    list_t *apiKeys = NULL;
    apiClient_t *apiClient = apiClient_create_with_base_path(basePath, sslConfig, apiKeys);
    if (!apiClient) {
        printf("Cannot create a kubernetes client.\n");
    }
    
    return EXIT_SUCCESS;
}
