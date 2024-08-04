#include <cigicl/CigiIGSession.h>
#include <cigicl/CigiHostSession.h>
#include <cigicl/CigiSOFV4.h>

int main(void) {
    // Test constructing sessions
    CigiIGSession* pIgSession = new CigiIGSession();
    CigiHostSession* pHostSession = new CigiHostSession();

    // Write outgoing messages to buffer
    CigiSOFV4 sofMsg;

    CigiOutgoingMsg& msgOut = pIgSession->GetOutgoingMsgMgr();
    msgOut.BeginMsg();
    msgOut.pack(sofMsg);

    Cigi_uint8* rawMsgData = nullptr;
    int msgLength = 0;
    msgOut.PackageMsg(&rawMsgData, msgLength);

    // Test reading back the message
    CigiIncomingMsg& msgIn = pHostSession->GetIncomingMsgMgr();
    int status = msgIn.ProcessIncomingMsg(rawMsgData, msgLength);

    // Cleanup
    msgOut.FreeMsg();
    delete pIgSession;
    delete pHostSession;

    // Test results
    return (status == CIGI_SUCCESS) ? 0 : -1;
}
