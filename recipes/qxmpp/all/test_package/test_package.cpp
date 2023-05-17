#include <QXmppClient.h>
#include <QXmppLogger.h>

int main() {
    QXmppClient client;
    client.logger()->setLoggingType(QXmppLogger::StdoutLogging);
}
