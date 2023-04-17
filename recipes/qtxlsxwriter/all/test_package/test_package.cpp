#include <iostream>
#include <QBuffer>
#include <xlsxdocument.h>

int main() {
	QBuffer device;
	device.open(QIODevice::WriteOnly);

	QXlsx::Document xlsx1;
	xlsx1.write("A1", true);
	xlsx1.write("A2", false);
	xlsx1.saveAs(&device);

	return 0;
}
