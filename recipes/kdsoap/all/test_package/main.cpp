#include <KDSoapClient/KDSoapValue.h>
#include <KDSoapClient/KDDateTime.h>

#include <QDateTime>

int main(int argc, char **argv)
{
    QDateTime qdt(QDate(2010, 12, 31));
    KDDateTime kdt(qdt);
    if (!kdt.isValid())
        return 1;

    if (kdt.toDateString() != QString::fromLatin1("2010-12-31T00:00:00"))
        return 1;

    kdt.setTimeZone(QString::fromLatin1("Z"));
    if (kdt.toDateString() != QString::fromLatin1("2010-12-31T00:00:00Z"))
        return 1;

    kdt = QDateTime(QDate(2011, 03, 15), QTime(23, 59, 59, 999));
    kdt.setTimeZone(QString::fromLatin1("+01:00"));
    if (kdt.toDateString() != QString::fromLatin1("2011-03-15T23:59:59.999+01:00"))
        return 1;

    return 0;
}
