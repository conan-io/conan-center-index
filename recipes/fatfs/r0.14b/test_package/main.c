#include <fatfs/diskio.h>
#include <fatfs/ff.h>

DSTATUS disk_initialize(BYTE pdrv) { return STA_NOINIT; }
DSTATUS disk_status(BYTE pdrv) { return STA_NOINIT; }
DRESULT disk_read(BYTE pdrv, BYTE *buff, LBA_t sector, UINT count) {
  return RES_NOTRDY;
}
DRESULT disk_write(BYTE pdrv, const BYTE *buff, LBA_t sector, UINT count) {
  return RES_NOTRDY;
}
DRESULT disk_ioctl(BYTE pdrv, BYTE cmd, void *buff) { return RES_NOTRDY; }
DWORD get_fattime() { return 0; }

int main() {
  FATFS fs;
  f_mount(&fs, "", 0);
  return 0;
}
