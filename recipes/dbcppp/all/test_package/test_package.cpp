
#include <fstream>
#include <unordered_map>
#include <sstream>

#include <dbcppp/Network.h>

int main() {
    constexpr char* test_dbc =
        "VERSION \"\"\n"
        "NS_ :\n"
        "BS_: 1 : 2, 3\n"
        "BU_:\n"
        "BO_ 1 Msg0: 8 Sender0\n"
        "  SG_ Sig0: 0|1@1+ (1,0) [1|12] \"Unit0\" Vector__XXX\n"
        "  SG_ Sig1 m0 : 1|1@0- (1,0) [1|12] \"Unit1\" Recv0, Recv1\n"
        "  SG_ Sig2 M : 2|1@0- (1,0) [1|12] \"Unit2\" Recv0, Recv1\n";

    std::istringstream iss(test_dbc);
    auto net = dbcppp::INetwork::LoadDBCFromIs(iss);
    for (const auto& msg : net->Messages()) {
        std::cout << "Message ID: " << msg.Id() << " Name: " << msg.Name() << std::endl;
        for (const auto& sig : msg.Signals()) {
            std::cout << '\t' << "Signal ID: " << sig.Name() << " Unit: " << sig.Unit() << std::endl;
        }
    }
}
