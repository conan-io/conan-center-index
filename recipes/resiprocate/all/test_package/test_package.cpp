#include <resip/stack/SipMessage.hxx>
#include <resip/stack/Helper.hxx>
#include <rutil/Logger.hxx>
#include <fstream>
#include <iostream>

#define RESIPROCATE_SUBSYSTEM Subsystem::TEST

using namespace resip;

int main(int argc, char* argv[])
{    
    if (argc < 2)
    {
        return 1;
    }
    Log::initialize(Log::Cout, Log::Warning, argv[0]);
    
    std::ifstream file(argv[1]);
    if(!file.is_open())
    {
        return 1;
    }
    std::string fileData = std::string((std::istreambuf_iterator<char>(file)), std::istreambuf_iterator<char>());
    file.close();

    auto msg = SipMessage::make(Data(Data::Share, fileData.data()), true);
    std::shared_ptr<SipMessage> forDel(msg);
    std::cout << std::string(msg->methodStr().data()) << std::endl;
    std::string headers = "";
    for (int i = 0; i < Headers::Type::MAX_HEADERS; i++)
    {
        auto rawHeader = msg->getRawHeader(static_cast<Headers::Type>(i));
        if (!rawHeader)
        {
            continue;
        }
        for (auto value : *rawHeader)
        {
            headers += std::string(value.getBuffer(), value.getLength());
        }
        headers += '\n';
    }

    std::cout << headers << std::endl;
    std::cout << std::string(msg->getRawBody().getBuffer(), msg->getRawBody().getLength()) << std::endl;

    return 0;
}

