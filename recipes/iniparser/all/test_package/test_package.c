#include <iniparser/iniparser.h>
#include <iniparser/dictionary.h>

#include <stdio.h>

int main()
{
  dictionary *ini = iniparser_load("test_package.ini");
  if (ini == NULL)
  {
    fprintf(stderr, "cannot parse file: test_package.ini\n");
    return 1;
  }

  const char *value = iniparser_getstring(ini, "section:key", NULL);
  if (value == NULL)
  {
    fprintf(stderr, "cannot find key: section:key\n");
  }
  else
  {
    printf("section:key = %s\n", value);
  }

  iniparser_freedict(ini);
}
