#include <libwebrtc.h>

using namespace libwebrtc;

int main()
{
    LibWebRTC::Initialize();

    auto pPeerConnectionFactory = LibWebRTC::CreateRTCPeerConnectionFactory();
    pPeerConnectionFactory->Initialize();

    pPeerConnectionFactory->Terminate();

    LibWebRTC::Terminate();
}