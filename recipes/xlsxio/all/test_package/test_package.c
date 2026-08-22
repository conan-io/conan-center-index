#include <stdio.h>
#include <xlsxio_read.h>
#include <xlsxio_write.h>

int main(int argc, char** argv) {
  xlsxiowriter xlsxwrite;
  int i;
  xlsxioreader xlsxioread;

  // open .xlsx file for writing (will overwrite if it already exists)
  if ((xlsxwrite = xlsxiowrite_open("test_package.xlsx", "MySheet")) == NULL) {
    fprintf(stderr, "Error creating .xlsx file\n");
    return 1;
  }
  // set row height
  xlsxiowrite_set_row_height(xlsxwrite, 1);
  // how many rows to buffer to detect column widths
  xlsxiowrite_set_detection_rows(xlsxwrite, 10);
  // write column names
  xlsxiowrite_add_column(xlsxwrite, "Col1", 0);
  xlsxiowrite_add_column(xlsxwrite, "Col2", 21);
  xlsxiowrite_add_column(xlsxwrite, "Col3", 0);
  xlsxiowrite_add_column(xlsxwrite, "Col4", 2);
  xlsxiowrite_add_column(xlsxwrite, "Col5", 0);
  xlsxiowrite_add_column(xlsxwrite, "Col6", 0);
  xlsxiowrite_add_column(xlsxwrite, "Col7", 0);
  xlsxiowrite_next_row(xlsxwrite);
  // write data
  for (i = 0; i < 1000; i++) {
    xlsxiowrite_add_cell_string(xlsxwrite, "Test");
    xlsxiowrite_add_cell_string(xlsxwrite, "A b  c   d    e     f\nnew line");
    xlsxiowrite_add_cell_string(xlsxwrite, "&% <test> \"'");
    xlsxiowrite_add_cell_string(xlsxwrite, NULL);
    xlsxiowrite_add_cell_int(xlsxwrite, i);
    xlsxiowrite_add_cell_datetime(xlsxwrite, time(NULL));
    xlsxiowrite_add_cell_float(xlsxwrite, 3.1415926);
    xlsxiowrite_next_row(xlsxwrite);
  }
  // close .xlsx file
  xlsxiowrite_close(xlsxwrite);

  // read .xlsx file
  xlsxioread = xlsxioread_open("test_package.xlsx");

  // close .xlsx file
  xlsxioread_close(xlsxioread);

  return 0;
}
