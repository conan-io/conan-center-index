#include <hdr_histogram.h>

#include <stdio.h>

int main()
{
  struct hdr_histogram* h = NULL;

  if(!hdr_alloc(1, 2, &h))
  {
    hdr_percentiles_print(h, stdout, 5, 1.0, CLASSIC);
  }

  return 0;
}
