#pragma once

#ifdef WIN32
  #define hello_EXPORT __declspec(dllexport)
#else
  #define hello_EXPORT
#endif

hello_EXPORT void hello();
