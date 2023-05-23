#include <stdio.h>
#include <sixel.h>

static int sixel_write(char *data, int size, void *priv)
{
    return fwrite(data, 1, size, (FILE *)priv);
}

int main() {
  SIXELSTATUS status = SIXEL_FALSE;
  sixel_output_t *output = NULL;

  status = sixel_output_new(&output, sixel_write, stdout, NULL);
  if (SIXEL_FAILED(status))
      return 1;

  return 0;
}

