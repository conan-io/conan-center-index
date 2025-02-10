#include <resip/stack/SipMessage.hxx>
#include <resip/stack/Helper.hxx>
#include <rutil/Logger.hxx>
#include <iostream>

#define RESIPROCATE_SUBSYSTEM Subsystem::TEST

using namespace resip;

int main(int argc, char* argv[])
{
    Log::initialize(Log::Cout, Log::Warning, argv[0]);

    const std::string sipRawData("foobar");

    SipMessage* msg = SipMessage::make(sipRawData.data(), true);
    if (!msg) {
        return 0;
    }

    return 0;
}

