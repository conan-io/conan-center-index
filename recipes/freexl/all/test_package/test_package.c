#include <freexl.h>

#include <stdlib.h>
#include <stdio.h>
#include <string.h>

int main(int argc, char **argv) {
  if (argc < 2) {
    fprintf(stderr, "Need at least one argument\n");
    return -1;
  }

  const void *handle;
  int ret;
  unsigned int info;
  const char *worksheet_name;
  unsigned short active_idx;
  unsigned int num_rows;
  unsigned short num_columns;
  FreeXL_CellValue cell_value;

  ret = freexl_open(argv[1], &handle);
  if (ret != FREEXL_OK) {
    fprintf(stderr, "OPEN ERROR: %d\n", ret);
    return -1;
  }

  ret = freexl_get_info(handle, FREEXL_CFBF_VERSION, &info);
  if (ret != FREEXL_OK) {
    fprintf(stderr, "GET_INFO ERROR for CFBF version: %d\n", ret);
    return -3;
  }
  if (info != FREEXL_UNKNOWN) {
    fprintf(stderr, "Unexpected CFBF_VERSION: %d\n", info);
    return -4;
  }

  ret = freexl_get_info(handle, FREEXL_CFBF_SECTOR_SIZE, &info);
  if (ret != FREEXL_OK) {
    fprintf(stderr, "GET_INFO ERROR for sector size: %d\n", ret);
    return -5;
  }
  if (info != FREEXL_UNKNOWN) {
    fprintf(stderr, "Unexpected CFBF_SECTOR_SIZE: %d\n", info);
    return -6;
  }

  ret = freexl_get_info(handle, FREEXL_CFBF_FAT_COUNT, &info);
  if (ret != FREEXL_OK) {
    fprintf(stderr, "GET_INFO ERROR for fat count: %d\n", ret);
    return -7;
  }
  if (info != 0) {
    fprintf(stderr, "Unexpected CFBF_FAT_COUNT: %d\n", info);
    return -8;
  }

  ret = freexl_get_info(handle, FREEXL_BIFF_VERSION, &info);
  if (ret != FREEXL_OK) {
    fprintf(stderr, "GET_INFO ERROR for BIFF version: %d\n", ret);
    return -9;
  }
  if (info != FREEXL_BIFF_VER_2) {
    fprintf(stderr, "Unexpected BIFF version: %d\n", info);
    return -10;
  }

  ret = freexl_get_info(handle, FREEXL_BIFF_MAX_RECSIZE, &info);
  if (ret != FREEXL_OK) {
    fprintf(stderr, "GET_INFO ERROR for BIFF record size: %d\n", ret);
    return -11;
  }
  if (info != FREEXL_UNKNOWN) {
    fprintf(stderr, "Unexpected BIFF max record size: %d\n", info);
    return -12;
  }

  ret = freexl_get_info(handle, FREEXL_BIFF_DATEMODE, &info);
  if (ret != FREEXL_OK) {
    fprintf(stderr, "GET_INFO ERROR for BIFF date mode: %d\n", ret);
    return -13;
  }
  if (info != FREEXL_BIFF_DATEMODE_1900) {
    fprintf(stderr, "Unexpected BIFF date mode: %d\n", info);
    return -14;
  }

  ret = freexl_get_info(handle, FREEXL_BIFF_PASSWORD, &info);
  if (ret != FREEXL_OK) {
    fprintf(stderr, "GET_INFO ERROR for BIFF password mode: %d\n", ret);
    return -15;
  }
  if (info != FREEXL_BIFF_PLAIN) {
    fprintf(stderr, "Unexpected BIFF password mode: %d\n", info);
    return -16;
  }

  ret = freexl_get_info(handle, FREEXL_BIFF_CODEPAGE, &info);
  if (ret != FREEXL_OK) {
    fprintf(stderr, "GET_INFO ERROR for BIFF codepage: %d\n", ret);
    return -17;
  }
  if (info != FREEXL_BIFF_CP1252) {
    fprintf(stderr, "Unexpected BIFF codepage: %d\n", info);
    return -18;
  }

  ret = freexl_get_info(handle, FREEXL_BIFF_SHEET_COUNT, &info);
  if (ret != FREEXL_OK) {
    fprintf(stderr, "GET_INFO ERROR for BIFF worksheet count: %d\n", ret);
    return -19;
  }
  if (info != 1) {
    fprintf(stderr, "Unexpected BIFF worksheet count: %d\n", info);
    return -20;
  }

  ret = freexl_get_info(handle, FREEXL_BIFF_FORMAT_COUNT, &info);
  if (ret != FREEXL_OK) {
    fprintf(stderr, "GET_INFO ERROR for BIFF format count: %d\n", ret);
    return -21;
  }
  if (info != 10) {
    fprintf(stderr, "Unexpected BIFF format count: %d\n", info);
    return -22;
  }

  ret = freexl_get_info(handle, FREEXL_BIFF_XF_COUNT, &info);
  if (ret != FREEXL_OK) {
    fprintf(stderr, "GET_INFO ERROR for BIFF extended format count: %d\n", ret);
    return -23;
  }
  if (info != 6) {
    fprintf(stderr, "Unexpected BIFF extended format count: %d\n", info);
    return -24;
  }

  /* We only have one worksheet, zero index */
  ret = freexl_get_worksheet_name(handle, 0, &worksheet_name);
  if (ret != FREEXL_OK) {
    fprintf(stderr, "Error getting worksheet name: %d\n", ret);
    return -25;
  }
  if (strcmp(worksheet_name, "Worksheet") != 0) {
    fprintf(stderr, "Unexpected worksheet name: %s\n", worksheet_name);
    return -26;
  }

  ret = freexl_select_active_worksheet(handle, 0);
  if (ret != FREEXL_OK) {
    fprintf(stderr, "Error setting active worksheet: %d\n", ret);
    return -27;
  }

  ret = freexl_get_active_worksheet(handle, &active_idx);
  if (ret != FREEXL_OK) {
    fprintf(stderr, "Error getting active worksheet: %d\n", ret);
    return -28;
  }
  if (active_idx != 0) {
    fprintf(stderr, "Unexpected active sheet: %d\n", info);
    return -29;
  }

  ret = freexl_worksheet_dimensions(handle, &num_rows, &num_columns);
  if (ret != FREEXL_OK) {
    fprintf(stderr, "Error getting worksheet dimensions: %d\n", ret);
    return -30;
  }
  if ((num_rows != 4) || (num_columns != 6)) {
    fprintf(stderr, "Unexpected active sheet dimensions: %u x %u\n",
    num_rows, num_columns);
    return -31;
  }

  ret = freexl_get_cell_value(handle, 0, 0, &cell_value);
  if (ret != FREEXL_OK) {
    fprintf(stderr, "Error getting cell value (0,0): %d\n", ret);
    return -32;
  }
  if (cell_value.type != FREEXL_CELL_TEXT) {
    fprintf(stderr, "Unexpected cell (0,0) type: %u\n", cell_value.type);
    return -33;
  }
  if (strcmp(cell_value.value.text_value, "Column 1") != 0) {
    fprintf(stderr, "Unexpected cell (0,0) value: %s\n", cell_value.value.text_value);
    return -34;
  }

  ret = freexl_get_cell_value(handle, 3, 0, &cell_value);
  if (ret != FREEXL_OK) {
    fprintf(stderr, "Error getting cell value (3,0): %d\n", ret);
    return -35;
  }
  if (cell_value.type != FREEXL_CELL_DOUBLE) {
    fprintf(stderr, "Unexpected cell (3,0) type: %u\n", cell_value.type);
    return -36;
  }
  if (cell_value.value.double_value != 3.14) {
    fprintf(stderr, "Unexpected cell (3,0) value: %g\n", cell_value.value.double_value);
    return -37;
  }

  ret = freexl_get_cell_value(handle, 3, 1, &cell_value);
  if (ret != FREEXL_OK) {
    fprintf(stderr, "Error getting cell value (3,1): %d\n", ret);
    return -38;
  }
  if (cell_value.type != FREEXL_CELL_DOUBLE) {
    fprintf(stderr, "Unexpected cell (3,1) type: %u\n", cell_value.type);
    return -39;
  }
  if (cell_value.value.double_value != -56.3089) {
    fprintf(stderr, "Unexpected cell (3,1) value: %g\n", cell_value.value.double_value);
    return -40;
  }

  ret = freexl_get_cell_value(handle, 3, 2, &cell_value);
  if (ret != FREEXL_OK) {
    fprintf(stderr, "Error getting cell value (3,2): %d\n", ret);
    return -41;
  }
  if (cell_value.type != FREEXL_CELL_DOUBLE) {
    fprintf(stderr, "Unexpected cell (3,2) type: %u\n", cell_value.type);
    return -42;
  }
  if (cell_value.value.double_value != 0.67) {
    fprintf(stderr, "Unexpected cell (3,2) value: %g\n", cell_value.value.double_value);
    return -43;
  }

  ret = freexl_get_cell_value(handle, 3, 3, &cell_value);
  if (ret != FREEXL_OK) {
    fprintf(stderr, "Error getting cell value (3,3): %d\n", ret);
    return -44;
  }
  if (cell_value.type != FREEXL_CELL_DATE) {
    fprintf(stderr, "Unexpected cell (3,3) type: %u\n", cell_value.type);
    return -45;
  }
  if (strcmp(cell_value.value.text_value, "1967-10-01") != 0) {
    fprintf(stderr, "Unexpected cell (3,3) value: %s\n", cell_value.value.text_value);
    return -46;
  }

  ret = freexl_get_cell_value(handle, 3, 4, &cell_value);
  if (ret != FREEXL_OK) {
    fprintf(stderr, "Error getting cell value (3,4): %d\n", ret);
    return -47;
  }
  if (cell_value.type != FREEXL_CELL_INT) {
    fprintf(stderr, "Unexpected cell (3,4) type: %u\n", cell_value.type);
    return -48;
  }
  if (cell_value.value.int_value != 4) {
    fprintf(stderr, "Unexpected cell (3,4) value: %d\n", cell_value.value.int_value);
    return -49;
  }

  ret = freexl_get_cell_value(handle, 3, 5, &cell_value);
  if (ret != FREEXL_OK) {
    fprintf(stderr, "Error getting cell value (3,5): %d\n", ret);
    return -50;
  }
  if (cell_value.type != FREEXL_CELL_INT) {
    fprintf(stderr, "Unexpected cell (3,5) type: %u\n", cell_value.type);
    return -51;
  }
  if (cell_value.value.int_value != 237) {
    fprintf(stderr, "Unexpected cell (3,5) value: %d\n", cell_value.value.int_value);
    return -52;
  }

  ret = freexl_get_cell_value(handle, 1, 5, &cell_value);
  if (ret != FREEXL_OK) {
    fprintf(stderr, "Error getting cell value (1,5): %d\n", ret);
    return -53;
  }
  if (cell_value.type != FREEXL_CELL_TIME) {
    fprintf(stderr, "Unexpected cell (1,5) type: %u\n", cell_value.type);
    return -54;
  }
  if (strcmp(cell_value.value.text_value, "23:34:04") != 0) {
    fprintf(stderr, "Unexpected cell (1,5) value: %s\n", cell_value.value.text_value);
    return -55;
  }

  /* error cases */
  ret = freexl_get_cell_value(handle, 7, 3, &cell_value);
  if (ret != FREEXL_ILLEGAL_CELL_ROW_COL) {
    fprintf(stderr, "Unexpected result for (7,3): %d\n", ret);
    return -56;
  }
  ret = freexl_get_cell_value(handle, 2, 99, &cell_value);
  if (ret != FREEXL_ILLEGAL_CELL_ROW_COL) {
    fprintf(stderr, "Unexpected result for (2,99): %d\n", ret);
    return -57;
  }
  ret = freexl_get_cell_value(handle, 4, 2, &cell_value);
  if (ret != FREEXL_ILLEGAL_CELL_ROW_COL) {
    fprintf(stderr, "Unexpected result for (4,2): %d\n", ret);
    return -58;
  }
  ret = freexl_get_cell_value(handle, 3, 6, &cell_value);
  if (ret != FREEXL_ILLEGAL_CELL_ROW_COL) {
    fprintf(stderr, "Unexpected result for (3,6): %d\n", ret);
    return -59;
  }

  ret = freexl_close(handle);
  if (ret != FREEXL_OK) {
    fprintf(stderr, "CLOSE ERROR: %d\n", ret);
    return -2;
  }

  return 0;
}
