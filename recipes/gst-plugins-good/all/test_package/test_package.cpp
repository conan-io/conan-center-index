#include <gst/gst.h>
#include <gst/gstplugin.h>

#ifdef _WIN32

#include <Windows.h>

#ifndef FLG_SHOW_LDR_SNAPS
#define FLG_SHOW_LDR_SNAPS 0x02
#endif /* FLG_SHOW_LDR_SNAPS */

extern "C" const IMAGE_LOAD_CONFIG_DIRECTORY _load_config_used =
{
    sizeof(IMAGE_LOAD_CONFIG_DIRECTORY),
    0,
    0,
    0,
    0,
    FLG_SHOW_LDR_SNAPS,
    2000,	// CriticalSectionDefaultTimeout msec
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0
};

LONG NTAPI VexHandler(PEXCEPTION_POINTERS ExceptionInfo)
{
    PEXCEPTION_RECORD ExceptionRecord = ExceptionInfo->ExceptionRecord;

    switch (ExceptionRecord->ExceptionCode)
    {
    case DBG_PRINTEXCEPTION_WIDE_C:
    case DBG_PRINTEXCEPTION_C:

        if (ExceptionRecord->NumberParameters >= 2)
        {
            ULONG len = (ULONG)ExceptionRecord->ExceptionInformation[0];

            union {
                ULONG_PTR up;
                PCWSTR pwz;
                PCSTR psz;
            };

            up = ExceptionRecord->ExceptionInformation[1];

            HANDLE hOut = GetStdHandle(STD_ERROR_HANDLE);
            DWORD temp;
            BOOL is_console = GetConsoleMode(GetStdHandle(STD_OUTPUT_HANDLE), &temp);

            if (ExceptionRecord->ExceptionCode == DBG_PRINTEXCEPTION_C)
            {
                if (is_console)
                {
                    // assume CP_ACP encoding
                    if (ULONG n = MultiByteToWideChar(CP_ACP, 0, psz, len, 0, 0))
                    {
                        PWSTR wz = (PWSTR)alloca(n * sizeof(WCHAR));

                        if (len = MultiByteToWideChar(CP_ACP, 0, psz, len, wz, n))
                        {
                            pwz = wz;
                        }
                    }

                    if (len)
                    {
                        WriteConsoleW(hOut, pwz, len - 1, &len, 0);
                    }
                }
                else
                    WriteFile(hOut, psz, len - 1, &len, 0);
            }

        }
        return EXCEPTION_CONTINUE_EXECUTION;
}

    return EXCEPTION_CONTINUE_SEARCH;
}

#endif

#ifdef GST_PLUGINS_GOOD_STATIC

extern "C"
{
    GST_PLUGIN_STATIC_DECLARE(wavparse);
}

#endif

#include <iostream>

int main(int argc, char * argv[])
{
#ifdef _WIN32
    SetErrorMode(SEM_FAILCRITICALERRORS);
    AddVectoredExceptionHandler(TRUE, VexHandler);
#endif
    gst_init(&argc, &argv);

#ifdef GST_PLUGINS_GOOD_STATIC

    GST_PLUGIN_STATIC_REGISTER(wavparse);

#endif

    GstElement * wavparse = gst_element_factory_make("wavparse", NULL);
    if (!wavparse) {
        std::cerr << "failed to create wavparse element" << std::endl;
        return -1;
    } else {
        std::cout << "wavparse has been created successfully" << std::endl;
    }
    gst_object_unref(GST_OBJECT(wavparse));
    return 0;
}
