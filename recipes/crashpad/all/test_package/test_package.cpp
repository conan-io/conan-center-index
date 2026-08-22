#include <map>
#include <string>
#include <vector>

#ifdef _WIN32
#include <cwchar>
#endif

#include "client/crashpad_client.h"
#include "client/settings.h"

#include "client/crash_report_database.h"

bool startCrashpad(const base::FilePath &db,
                   const base::FilePath &handler) {
    std::string              url("http://localhost");
    std::map<std::string, std::string> annotations;
    std::vector<std::string>      arguments;

    crashpad::CrashpadClient client;
    return client.StartHandler(
        handler,
        db,
        db,
        url,
        annotations,
        arguments,
        true,
        false
    );
}

int main(int argc, char* argv[]) {
    if (argc != 3) {
        return 2;
    }

#ifdef _WIN32
    wchar_t ws[1024];
    swprintf(ws, 1024, L"%hs", argv[1]);
    base::FilePath db(ws);
    swprintf(ws, 1024, L"%hs", argv[2]);
    base::FilePath handler(ws);
#else
    base::FilePath db(argv[1]);
    base::FilePath handler(argv[2]);
#endif

    // Test availability of this function.
    auto database = crashpad::CrashReportDatabase::Initialize(db);
    (void) database; /* Avoid warning about unused variable */

    return startCrashpad(db, handler) ? 0 : 1;
}
