#include <resip/stack/SipMessage.hxx>
#include <resip/stack/Helper.hxx>
#include <rutil/Logger.hxx>
#include <iostream>

#define RESIPROCATE_SUBSYSTEM Subsystem::TEST

using namespace resip;

std::string sipRawData = "INVITE sip:nikolia@example.ru SIP/2.0\r\n"
                         "Record-Route: <sip:nikolia@10.0.0.10;lr>\r\n"
                         "Via: SIP/2.0/UDP 10.0.0.10;branch=z9hG4bK3af7.0a6e92f4.0\r\n"
                         "Via: SIP/2.0/UDP 192.168.0.2:5060;branch=z9hG4bK12ee92cb;rport=5060\r\n"
                         "From: \"78128210000\" <sip:78128210000@neutral.ru>;tag=as149b2d97\r\n"
                         "To: <sip:nikolia@example.ru>\r\n"
                         "Contact: <sip:78128210000@neutral.ru>\r\n"
                         "Call-ID: 3cbf958e6f43d91905c3fa964a373dcb@example.ru\r\n"
                         "CSeq: 103 INVITE\r\n"
                         "Max-Forwards: 16\r\n"
                         "Date: Wed, 10 Jan 2001 13:16:23 GMT\r\n"
                         "Allow: INVITE, ACK, CANCEL, OPTIONS, BYE, REFER, SUBSCRIBE, NOTIFY\r\n"
                         "Supported: replaces\r\n"
                         "Content-Type: application/sdp\r\n"
                         "Content-Length: 394\r\n"
                         "\r\n"
                         "v=0\r\n"
                         "o=root 3303 3304 IN IP4 10.0.0.10\r\n"
                         "s=session\r\n"
                         "c=IN IP4 10.0.0.10\r\n"
                         "t=0 0\r\n"
                         "m=audio 40358 RTP/AVP 0 8 101\r\r\n"
                         "a=rtpmap:0 PCMU/8000\r\n"
                         "a=rtpmap:8 PCMA/8000\r\n"
                         "a=rtpmap:101 telephone-event/8000\r\n"
                         "a=fmtp:101 0-16\r\n"
                         "a=silenceSupp:off - - - -\r\n"
                         "a=sendrecv\r\n";

int main(int argc, char* argv[])
{
    Log::initialize(Log::Cout, Log::Warning, argv[0]);

    SipMessage* msg = SipMessage::make(Data(Data::Share, sipRawData.data()), true);
    if (!msg)
    {
        return 1;
    }

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
        headers += "\r\n";
    }

    std::cout << headers << std::endl;
    std::cout << std::string(msg->getRawBody().getBuffer(), msg->getRawBody().getLength()) << std::endl;

    delete msg;
    return 0;
}

