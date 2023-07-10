#include <iostream>
#include <xlsxio_read.h>
#include <xlsxio_write.h>

int main(int argc, char** argv) {
  xlsxiowriter handle;
  // open .xlsx file for writing (will overwrite if it already exists)
  if ((handle = xlsxiowrite_open("test_package.xlsx", "MySheet")) == NULL) {
    fprintf(stderr, "Error creating .xlsx file\n");
    return 1;
  }
  // set row height
  xlsxiowrite_set_row_height(handle, 1);
  // how many rows to buffer to detect column widths
  xlsxiowrite_set_detection_rows(handle, 10);
  // write column names
  xlsxiowrite_add_column(handle, "Col1", 0);
  xlsxiowrite_add_column(handle, "Col2", 21);
  xlsxiowrite_add_column(handle, "Col3", 0);
  xlsxiowrite_add_column(handle, "Col4", 2);
  xlsxiowrite_add_column(handle, "Col5", 0);
  xlsxiowrite_add_column(handle, "Col6", 0);
  xlsxiowrite_add_column(handle, "Col7", 0);
  xlsxiowrite_next_row(handle);
  // write data
  int i;
  for (i = 0; i < 1000; i++) {
    xlsxiowrite_add_cell_string(handle, "Test");
    xlsxiowrite_add_cell_string(handle, "A b  c   d    e     f\nnew line");
    xlsxiowrite_add_cell_string(handle, "&% <test> \"'");
    xlsxiowrite_add_cell_string(handle, NULL);
    xlsxiowrite_add_cell_int(handle, i);
    xlsxiowrite_add_cell_datetime(handle, time(NULL));
    xlsxiowrite_add_cell_float(handle, 3.1415926);
    xlsxiowrite_next_row(handle);
  }
  // close .xlsx file
  xlsxiowrite_close(handle);

  // read .xlsx file
  xlsxioreader xlsxioread = xlsxioread_open("test_package.xlsx");

  // close .xlsx file
  xlsxioread_close(xlsxioread);

  return 0;
}
