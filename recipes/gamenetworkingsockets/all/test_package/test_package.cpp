#include <assert.h>
#include <stdio.h>
#include <string.h>

#include <steam/isteamnetworkingutils.h>
#include <steam/steamnetworkingsockets.h>

static FILE* g_fpLog = NULL;
static SteamNetworkingMicroseconds g_logTimeZero;

static void DebugOutput(ESteamNetworkingSocketsDebugOutputType eType, char const* pszMsg)
{
    SteamNetworkingMicroseconds time = SteamNetworkingUtils()->GetLocalTimestamp() - g_logTimeZero;
    if (g_fpLog) {
        fprintf(g_fpLog, "%10.6f %s\n", time * 1e-6, pszMsg);
    }

    if (eType <= k_ESteamNetworkingSocketsDebugOutputType_Msg) {
        printf("%10.6f %s\n", time * 1e-6, pszMsg);
        fflush(stdout);
    }

    if (eType == k_ESteamNetworkingSocketsDebugOutputType_Bug) {
        fflush(stdout);
        fflush(stderr);
        if (g_fpLog) {
            fflush(g_fpLog);
        }

        if (strstr(pszMsg, "SteamNetworkingGlobalLock held for")) {
            return;
        }

        assert(!"TEST FAILED");
    }
}

int main()
{
    g_fpLog = stderr;
    g_logTimeZero = SteamNetworkingUtils()->GetLocalTimestamp();

    SteamNetworkingUtils()->SetDebugOutputFunction(k_ESteamNetworkingSocketsDebugOutputType_Debug, DebugOutput);
    SteamNetworkingUtils()->SetDebugOutputFunction(k_ESteamNetworkingSocketsDebugOutputType_Verbose, DebugOutput);
    SteamNetworkingUtils()->SetDebugOutputFunction(k_ESteamNetworkingSocketsDebugOutputType_Msg, DebugOutput);

    SteamDatagramErrMsg errMsg;
    if (!GameNetworkingSockets_Init(NULL, errMsg)) {
        fprintf(stderr, "GameNetworkingSockets_Init failed. %s", errMsg);
        return 1;
    }

    GameNetworkingSockets_Kill();
    return 0;
}
