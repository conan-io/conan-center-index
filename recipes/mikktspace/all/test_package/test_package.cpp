#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>

#include <mikktspace.h>

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
