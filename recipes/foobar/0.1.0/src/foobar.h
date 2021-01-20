#pragma once

#ifdef WIN32
  #define foobar_EXPORT __declspec(dllexport)
#else
  #define foobar_EXPORT
#endif

foobar_EXPORT void foobar();
