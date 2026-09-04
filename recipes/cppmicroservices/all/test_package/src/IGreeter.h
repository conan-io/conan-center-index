#ifndef IGREETER_H
#define IGREETER_H

#include <greeter_export.h>

#include <string>

class GREETER_EXPORT IGreeter
{
  public:
    virtual ~IGreeter();
    virtual std::string Greet() = 0;
};

#endif // IGREETER_H
