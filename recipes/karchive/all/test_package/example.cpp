#include <KCompressionDevice>
#include <QBuffer>

int main() 
{
    QBuffer b;
    KCompressionDevice kcd(&b, false, KCompressionDevice::GZip);
    return 0;
}
