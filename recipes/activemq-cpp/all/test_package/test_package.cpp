#include <cstdlib>
#include <memory>
#include <activemq/core/ActiveMQConnectionFactory.h>
#include <activemq/library/ActiveMQCPP.h>
#include <cms/Connection.h>
#include <cms/ConnectionFactory.h>


int main(void) {

    activemq::library::ActiveMQCPP::initializeLibrary();

    activemq::library::ActiveMQCPP::shutdownLibrary();

    return EXIT_SUCCESS;
}
