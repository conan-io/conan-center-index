#include <kubernetes/api/CoreV1API.h>
#include <kubernetes/model/v1_pod.h>
#include <kubernetes/config/kube_config.h>

int main(void) {
    /*
     * Try to invokes the API to load the local k8s configuration.
     * It doesn't matter whether finds it or not.
     * The important thing is that it doesn't fail when use the library.
    */
    char *basePath = NULL;
    sslConfig_t *sslConfig = NULL;
    list_t *apiKeys = NULL;
    int rc = load_kube_config(&basePath, &sslConfig, &apiKeys, NULL);   /* NULL means loading configuration from $HOME/.kube/config */
    
    return EXIT_SUCCESS;
}
