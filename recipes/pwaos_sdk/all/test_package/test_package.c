// pwaos_sdk test_package.
//
// Link/ABI smoke: includes the packaged header, links the import
// library, checks the ABI version macros and that resultToString answers.
// No pwaos_server needed.
//
// When the environment has a display (X11 DISPLAY or Wayland
// WAYLAND_DISPLAY/WAYLAND_SOCKET), the full SDK "hello" example flow (init ->
// createInstance -> pwaMain -> shutDown) additionally runs against the
// packaged pwaos_server; without a display it is skipped automatically. The
// client forwards its argv to the spawned server, e.g. pass --no-sandbox on
// root/CI boxes via PWAOS_TEST_ARGS. Bounded by fork + killpg so it can never
// hang the test. Skipped too when the package was built with_runtime=False
// (PWAOS_RUNTIME_DIR is then unset/empty).
#include "runtime_client_api.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <signal.h>
#include <sys/wait.h>

static int g_argc;
static char** g_argv;
static time_t g_start;

static unsigned elapsed_seconds(void) {
    return (unsigned)(time(NULL) - g_start);
}

static void sleep_ms(int ms) {
    struct timespec ts = {ms / 1000, (ms % 1000) * 1000000L};
    nanosleep(&ts, NULL);
}

/* Link/ABI smoke: no server needed. */
static int smoke_abi(void) {
    unsigned major = (unsigned)PWAOS_RUNTIME_API_VERSION_MAJOR(PWAOS_RUNTIME_CURRENT_API_VERSION);
    unsigned minor = (unsigned)PWAOS_RUNTIME_API_VERSION_MINOR(PWAOS_RUNTIME_CURRENT_API_VERSION);
    printf("pwaos_sdk ABI %u.%u\n", major, minor);
    if (major != 0 || minor != 2) {
        printf("FAIL: unexpected ABI version\n");
        return 1;
    }

    char buf[PWAOS_MAX_RESULT_NAME_SIZE];
    pwaosResult r = pwaos_resultToString(PWAOS_RESULT_SUCCESS, buf);
    if (r != PWAOS_RESULT_SUCCESS || buf[0] == '\0') {
        printf("FAIL: resultToString r=%d buf='%.20s'\n", (int)r, buf);
        return 1;
    }
    printf("resultToString(SUCCESS) = \"%s\"\n", buf);
    return 0;
}

/* pwaMain, from the SDK "hello" example: query runtime properties, launch a
 * console PWA, wait for terminal events. Deadline-bounded (45s). */
static pwaosResult pwaMain(PWAOS_INSTANCE_HANDLE instance) {
    printf("starting...\n");

    pwaosInstanceProperties props = {
        .type = PWAOS_TYPE_INSTANCE_GET_PROPERTIES,
        .next = NULL
    };
    pwaosResult r = pwaosInstance_getProperties(instance, &props);
    if (r != PWAOS_RESULT_SUCCESS) {
        char err[PWAOS_MAX_RESULT_NAME_SIZE];
        pwaos_resultToString(r, err);
        printf("pwaosInstance_getProperties failed: %s\n", err);
        return r;
    }
    printf("%s is connected, its version is (%u.%u.%u)\n",
           props.runtimeName,
           (unsigned)PWAOS_RUNTIME_API_VERSION_MAJOR(props.runtimeVersion),
           (unsigned)PWAOS_RUNTIME_API_VERSION_MINOR(props.runtimeVersion),
           (unsigned)PWAOS_RUNTIME_API_VERSION_PATCH(props.runtimeVersion));

    PWAOS_APP_HANDLE app = INVALID_PWAOS_HANDLE;
    pwaosAppCreateInfo createInfo = {
        .type = PWAOS_TYPE_PWA_CREATE_INFO,
        .next = NULL,
        .appType = appTypeConsole,
        .appUrl = "https://www.pwaos.net",
        .width = 800,
        .height = 600
    };
    r = pwaosInstance_createPwa(instance, &createInfo, &app);
    if (r != PWAOS_RESULT_SUCCESS) {
        char err[PWAOS_MAX_RESULT_NAME_SIZE];
        pwaos_resultToString(r, err);
        printf("pwaosInstance_createPwa failed: %s\n", err);
        return r;
    }

    while (elapsed_seconds() <= 45) {
        pwaosEventDataBuffer buffer;
        if (PWAOS_RESULT_SUCCESS != pwaosInstance_pollEvent(instance, &buffer)) {
            sleep_ms(10);
            continue;
        }
        if (buffer.type == PWAOS_TYPE_EVENT_DATA_INSTANCE_STATUS_CHANGED) {
            const pwaosEventDataInstanceStatusChanged* ev =
                (const pwaosEventDataInstanceStatusChanged*)&buffer;
            if (ev->instance != instance)
                continue;
            if (ev->status < 0 || ev->status == instanceStatusConnectionLost)
                break;
        } else if (buffer.type == PWAOS_TYPE_EVENT_DATA_APP_STATUS_CHANGED) {
            const pwaosEventDataAppStatusChanged* ev =
                (const pwaosEventDataAppStatusChanged*)&buffer;
            if (ev->app == app && ev->status == appStatusStopping)
                break;
        }
    }

    printf("exiting...\n");
    pwaosInstance_destroyPwa(app);
    return PWAOS_RESULT_SUCCESS;
}

/* The hello flow body: runs in the forked child. */
static int runtime_flow_body(void) {
    setvbuf(stdout, NULL, _IONBF, 0); /* _exit() below skips stdio flush */
    /* PWAOS_RUNTIME_DIR is the directory CONTAINING runtime/ (set by the
     * recipe's package_info), so pass it through unchanged. */
    pwaos_setRuntimeExecutablePath(getenv("PWAOS_RUNTIME_DIR"));

    pwaosInitializeInfo initInfo = {
        .type = PWAOS_TYPE_INITIALIZE_INFO,
        .next = NULL,
        .argc = g_argc,
        .argv = g_argv,
        .use_dedicated_thread = true,
    };
    pwaosResult r = pwaos_init(&initInfo);
    if (r != PWAOS_RESULT_SUCCESS) {
        char err[PWAOS_MAX_RESULT_NAME_SIZE];
        pwaos_resultToString(r, err);
        printf("FAIL: pwaos_init: %s\n", err);
        return 1;
    }

    pwaosInstanceCreateInfo createInfo = {
        .type = PWAOS_TYPE_INSTANCE_CREATE_INFO,
        .next = NULL,
        .runtimeType = runtimeTypePwa,
        .serverUrl = "http://localhost",
        .dataPath = "/tmp/pwaos_sdk_test_data",
    };

    PWAOS_INSTANCE_HANDLE instance = INVALID_PWAOS_HANDLE;
    r = pwaos_createInstance(&createInfo, &instance);
    if (r != PWAOS_RESULT_SUCCESS) {
        char err[PWAOS_MAX_RESULT_NAME_SIZE];
        pwaos_resultToString(r, err);
        printf("FAIL: pwaos_createInstance: %s\n", err);
        pwaos_shutDown();
        return 1;
    }

    int outcome = 1;
    while (elapsed_seconds() <= 150) {
        pwaosEventDataBuffer buffer;
        pwaosResult result = pwaosInstance_pollEvent(instance, &buffer);
        if (PWAOS_RESULT_SUCCESS != result) {
            sleep_ms(10);
            continue;
        }
        if (buffer.type != PWAOS_TYPE_EVENT_DATA_INSTANCE_STATUS_CHANGED)
            continue;
        const pwaosEventDataInstanceStatusChanged* ev =
            (const pwaosEventDataInstanceStatusChanged*)&buffer;
        if (ev->instance != instance)
            continue;
        if (ev->status == instanceStatusWorking) {
            outcome = (pwaMain(instance) == PWAOS_RESULT_SUCCESS) ? 0 : 1;
            break;
        }
        else if (ev->status == instanceStatusStopping) {
            printf("instance stopped before Working\n");
            break;
        }
        else if (ev->status == instanceStatusConnectionLost) {
            printf("instance connection is lost\n");
            break;
        }
    }
    if (outcome != 0 && elapsed_seconds() > 150)
        printf("FAIL: runtime flow deadline (150s) exceeded\n");

    /* Report the outcome BEFORE teardown: pwaos_shutDown can trap (SIGTRAP)
     * on some desktops (observed with older SDK builds too), which would
     * turn a fully successful flow into a crash. The child _exits here and
     * the process-group teardown discards client+server state anyway. */
    if (outcome == 0)
        printf("runtime flow PASS\n");
    fflush(stdout);
    _exit(outcome);
}

/*
 * The hello flow against the packaged pwaos_server. pwaos_createInstance can
 * block indefinitely when the server cannot boot, so the flow runs in a
 * forked child in its own process group; a hard killpg at the deadline takes
 * down the whole tree and keeps `conan test` bounded.
 */
static int runtime_flow(void) {
    const char* rt = getenv("PWAOS_RUNTIME_DIR");
    if (!rt || !rt[0]) {
        printf("SKIP: no PWAOS_RUNTIME_DIR "
               "(package built with_runtime=False?)\n");
        return 0;
    }
    printf("runtime flow: server dir = %s\n", rt);

    pid_t pid = fork();
    if (pid < 0) {
        perror("fork");
        return 1;
    }
    if (pid == 0) {
        setpgid(0, 0); /* own group so the server tree dies with us */
        _exit(runtime_flow_body());
    }

    while (elapsed_seconds() <= 90) {
        int status;
        pid_t w = waitpid(pid, &status, WNOHANG);
        if (w == pid) {
            if (WIFEXITED(status))
                return WEXITSTATUS(status);
            printf("runtime flow FAIL (child crashed, signal %d)\n",
                   WTERMSIG(status));
            return 1;
        }
        if (w < 0) {
            perror("waitpid");
            return 1;
        }
        sleep(1);
    }
    printf("FAIL: runtime flow deadline (90s) exceeded - killing client+server\n");
    kill(-pid, SIGKILL); /* process group: client + spawned pwaos_server */
    waitpid(pid, NULL, 0);
    return 1;
}

/* The runtime flow needs a display: the spawned pwaos_server opens a window
 * (X11 or Wayland). */
static int has_display(void) {
    const char* v = getenv("DISPLAY");
    if (v && v[0])
        return 1;
    v = getenv("WAYLAND_DISPLAY");
    if (v && v[0])
        return 1;
    v = getenv("WAYLAND_SOCKET");
    return v && v[0];
}

int main(int argc, char** argv) {
    g_argc = argc;
    g_argv = argv;
    g_start = time(NULL);

    printf("pwaos clientApp started\n");
    int failed = smoke_abi();

    if (!failed) {
        if (has_display())
            failed |= runtime_flow();
        else
            printf("SKIP: no display (DISPLAY/WAYLAND_DISPLAY unset) - "
                   "ABI smoke only\n");
    }

    printf("pwaos clientApp exited\n");
    return failed ? 1 : 0;
}
