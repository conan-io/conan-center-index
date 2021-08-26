#include <cassert>
#include <cstdio>
#include <cstring>
#include <steam/isteamnetworkingutils.h>
#include <steam/steamnetworkingsockets.h>

static std::FILE* g_fpLog = nullptr;
static SteamNetworkingMicroseconds g_logTimeZero;

static void DebugOutput(ESteamNetworkingSocketsDebugOutputType eType, char const* pszMsg)
{
    SteamNetworkingMicroseconds time = SteamNetworkingUtils()->GetLocalTimestamp() - g_logTimeZero;
    if (g_fpLog) {
        std::fprintf(g_fpLog, "%10.6f %s\n", time * 1e-6, pszMsg);
    }

    if (eType <= k_ESteamNetworkingSocketsDebugOutputType_Msg) {
        std::printf("%10.6f %s\n", time * 1e-6, pszMsg);
        std::fflush(stdout);
    }

    if (eType == k_ESteamNetworkingSocketsDebugOutputType_Bug) {
        std::fflush(stdout);
        std::fflush(stderr);
        if (g_fpLog) {
            std::fflush(g_fpLog);
        }

        if (std::strstr(pszMsg, "SteamNetworkingGlobalLock held for")) {
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
    if (!GameNetworkingSockets_Init(nullptr, errMsg)) {
        std::fprintf(stderr, "GameNetworkingSockets_Init failed. %s", errMsg);
        return 1;
    }

    GameNetworkingSockets_Kill();
    return 0;
}
