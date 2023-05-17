#include <QDebug>
#include <QDateTime>

#include <qwt_date.h>

int main()
{
    qDebug() << QwtDate::toString(QwtDate::toDateTime(10), "MMM dd hh:mm ", QwtDate::FirstThursday);
    return 0;
}
