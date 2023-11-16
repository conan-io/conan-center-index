#include <memory>
#include <OpenHome/Net/Core/OhNet.h>

using namespace OpenHome::Net;

int main()
{
    InitialisationParams* initParams = InitialisationParams::Create();
    UpnpLibrary::InitialiseMinimal(initParams);
    delete initParams;
    UpnpLibrary::Close();
}
