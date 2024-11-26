#include <xlsxdocument.h>

int main() {
	// INFO: Document does not exist. Only for test package purposes.
	QXlsx::Document xlsxR("Test.xlsx");
	xlsxR.load();

	return 0;
}
