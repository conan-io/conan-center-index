#include <faac.h>
#include <stdio.h>

int main()
{
    char *faac_id_string;
    char *faac_copyright_string;
    // get faac version
    if (faacEncGetVersion(&faac_id_string, &faac_copyright_string) ==
        FAAC_CFG_VERSION)
    {
        fprintf(stderr, "Freeware Advanced Audio Coder\nFAAC %s\n",
                faac_id_string);
    }
    else
    {
        fprintf(stderr, __FILE__ "(%d): wrong libfaac version\n", __LINE__);
        return 1;
    }
    return 0;
}
