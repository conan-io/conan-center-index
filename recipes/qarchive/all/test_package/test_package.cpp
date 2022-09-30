#include <QCoreApplication>
#include <QArchive>

int main(int argc, char **argv)
{
    using QArchive::DiskExtractor;
    QCoreApplication app(argc, argv);
    DiskExtractor Extractor("Test.7z");

    /* Connect Signals and Slots. */
    QObject::connect(&Extractor ,
                     &DiskExtractor::finished ,
                     &app ,
                     &QCoreApplication::quit);

    Extractor.start();
    Extractor.cancel();

    return 0;
}
