/* This is part of Unidata's netCDF package. Copyright 2018.
   This is a test program for the nc-config utility. */
#include <netcdf.h>
#include <stdio.h>

int
main()
{
   printf("NetCDF version: %s\n", nc_inq_libvers());
   printf("*** SUCCESS!\n");
   return 0;
}
