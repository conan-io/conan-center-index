/* This is simple demonstration of how to use expat. This program
   reads an XML document from standard input and writes a line with
   the name of each element to standard output indenting child
   elements by one tab stop more than their parent element.
   It must be used with Expat compiled for UTF-8 output.
*/

#include <stdio.h>
#include "expat.h"

#ifdef XML_UNICODE_WCHAR_T
#include <wchar.h>
#endif

#ifdef XML_LARGE_SIZE
#if defined(XML_USE_MSC_EXTENSIONS) && _MSC_VER < 1400
#define XML_FMT_INT_MOD "I64"
#else
#define XML_FMT_INT_MOD "ll"
#endif
#else
#define XML_FMT_INT_MOD "l"
#endif

static void XMLCALL
startElement(void *userData, const XML_Char *name, const XML_Char **atts)
{
  int i;
  int *depthPtr = (int *)userData;
  (void)atts;

  for (i = 0; i < *depthPtr; i++)
    putchar('\t');
#ifdef XML_UNICODE_WCHAR_T
  fputws(name, stdout);
#else
  puts(name);
#endif
  *depthPtr += 1;
}

static void XMLCALL
endElement(void *userData, const XML_Char *name)
{
  int *depthPtr = (int *)userData;
  (void)name;

  *depthPtr -= 1;
}

int
main(int argc, char *argv[])
{
  XML_Parser parser = XML_ParserCreate(NULL);
  int depth = 0;
  (void)argc;
  (void)argv;

  XML_SetUserData(parser, &depth);
  XML_SetElementHandler(parser, startElement, endElement);
  XML_ParserFree(parser);
  printf("Test application successfully ran!\n");
  return 0;
}
