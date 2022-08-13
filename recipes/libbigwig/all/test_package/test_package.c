#include "libbigwig/bigWig.h"

int main(int argc, char *argv[]) {
  bigWigFile_t *fp = NULL;
  const char *chroms[] = {"1", "2"};
  const char *chromsUse[] = {"1", "1", "1"};
  uint32_t chrLens[] = {1000000, 1500000};
  uint32_t starts[] = {0, 100, 125,
                       200, 220, 230,
                       500, 600, 625,
                       700, 800, 850};
  uint32_t ends[] = {5, 120, 126,
                     205, 226, 231};
  float values[] = {0.0f, 1.0f, 200.0f,
                    -2.0f, 150.0f, 25.0f,
                    0.0f, 1.0f, 200.0f,
                    -2.0f, 150.0f, 25.0f,
                    -5.0f, -20.0f, 25.0f,
                    -5.0f, -20.0f, 25.0f};


  if(bwInit(1<<17) != 0) {
    fprintf(stderr, "Received an error in bwInit\n");
    return 1;
  }

  fp = bwOpen("example_output.bw", NULL, "w");
  if(!fp) {
    fprintf(stderr, "An error occurred while opening example_output.bw for writingn\n");
    return 1;
  }

  //Allow up to 10 zoom levels, though fewer will be used in practice
  if(bwCreateHdr(fp, 10)) goto error;

  //Create the chromosome lists
  fp->cl = bwCreateChromList(chroms, chrLens, 2);
  if(!fp->cl) goto error;

  //Write the header
  if(bwWriteHdr(fp)) goto error;

  //Some example bedGraph-like entries
  if(bwAddIntervals(fp, chromsUse, starts, ends, values, 3)) goto error;
  //We can continue appending similarly formatted entries
  //N.B. you can't append a different chromosome (those always go into different
  if(bwAppendIntervals(fp, starts+3, ends+3, values+3, 3)) goto error;

  //Add a new block of entries with a span. Since bwAdd/AppendIntervals was just used we MUST create a new block
  if(bwAddIntervalSpans(fp, "1", starts+6, 20, values+6, 3)) goto error;
  //We can continue appending similarly formatted entries
  if(bwAppendIntervalSpans(fp, starts+9, values+9, 3)) goto error;

  //Add a new block of fixed-step entries
  if(bwAddIntervalSpanSteps(fp, "1", 900, 20, 30, values+12, 3)) goto error;
  //The start is then 760, since that's where the previous step ended
  if(bwAppendIntervalSpanSteps(fp, values+15, 3)) goto error;

  //Add a new chromosome
  chromsUse[0] = "2";
  chromsUse[1] = "2";
  chromsUse[2] = "2";
  if(bwAddIntervals(fp, chromsUse, starts, ends, values, 3)) goto error;

  //Closing the file causes the zoom levels to be created
  bwClose(fp);
  bwCleanup();

  return 0;

  error:
  fprintf(stderr, "Received an error somewhere!\n");
  bwClose(fp);
  bwCleanup();
  return 1;
}
