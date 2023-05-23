#include <mikktspace.h>
#include <stdlib.h>

static int GetNumFaces(const SMikkTSpaceContext *pContext)
{
    return 0;
}

int main()
{
    SMikkTSpaceInterface sInterface = {NULL};
    sInterface.m_getNumFaces = GetNumFaces;

    SMikkTSpaceContext sContext = {NULL};
    sContext.m_pInterface = &sInterface;

    genTangSpaceDefault(&sContext);

    return 0;
}
