#include <QArchive>

int main(int argc, char **argv)
{
    QArchive::DiskExtractor Extractor("Test.7z");

    Extractor.start();
    Extractor.cancel();

    return 0;
}
