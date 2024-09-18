#include <slang.h>
#include <slang-com-ptr.h>
#include <slang-com-helper.h>
#include <cstdio>

using Slang::ComPtr;

int main(int argc, char *argv[]) {
    if (argc != 2) {
        printf("Usage: %s <.slang file>\n", argv[0]);
        return -1;
    }

    ComPtr<slang::IGlobalSession> slangGlobalSession;
    SLANG_RETURN_ON_FAIL(slang::createGlobalSession(slangGlobalSession.writeRef()));

    slang::SessionDesc sessionDesc = {};
    slang::TargetDesc targetDesc = {};
    targetDesc.format = SLANG_SHADER_HOST_CALLABLE;
    targetDesc.flags = SLANG_TARGET_FLAG_GENERATE_WHOLE_PROGRAM;
    sessionDesc.targets = &targetDesc;
    sessionDesc.targetCount = 1;
    ComPtr<slang::ISession> session;
    SLANG_RETURN_ON_FAIL(slangGlobalSession->createSession(sessionDesc, session.writeRef()));

    slang::IModule* slangModule = session->loadModule(argv[1]);
    if (!slangModule) {
        printf("Failed to load %s\n", argv[1]);
        return -1;
    }
    printf("Successfully loaded %s\n", argv[1]);
}
