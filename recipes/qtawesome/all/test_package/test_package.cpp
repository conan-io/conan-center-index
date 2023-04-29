#include "QtAwesome.h"
#include <QApplication>

int main(int argc, char *argv[]) {
	QApplication app(argc, argv);
	fa::QtAwesome awesome(&app);

	awesome.initFontAwesome();

    return EXIT_SUCCESS;
}
