#include "libqhull_r/qhull_ra.h"

/*-------------------------------------------------
-internal function prototypes
*/
void print_summary(qhT *qh);
void makecube(coordT *points, int numpoints, int dim);
void makeDelaunay(qhT *qh, coordT *points, int numpoints, int dim, int seed);
void findDelaunay(qhT *qh, int dim);
void makehalf(coordT *points, int numpoints, int dim);

/*-------------------------------------------------
-print_summary(qh)
*/
void print_summary(qhT *qh) {
  facetT *facet;
  int k;

  printf("\n%d vertices and %d facets with normals:\n",
                 qh->num_vertices, qh->num_facets);
  FORALLfacets {
    for (k=0; k < qh->hull_dim; k++)
      printf("%6.2g ", facet->normal[k]);
    printf("\n");
  }
}

/*--------------------------------------------------
-makecube- set points to vertices of cube
  points is numpoints X dim
*/
void makecube(coordT *points, int numpoints, int dim) {
  int j,k;
  coordT *point;

  for (j=0; j<numpoints; j++) {
    point= points + j*dim;
    for (k=dim; k--; ) {
      if (j & ( 1 << k))
        point[k]= 1.0;
      else
        point[k]= -1.0;
    }
  }
} /*.makecube.*/

/*--------------------------------------------------
-makeDelaunay- set points for dim Delaunay triangulation of random points
  points is numpoints X dim.
notes:
  makeDelaunay() in user_eg2_r.c uses qh_setdelaunay() to project points in place.
*/
void makeDelaunay(qhT *qh, coordT *points, int numpoints, int dim, int seed) {
  int j,k;
  coordT *point, realr;

  printf("seed: %d\n", seed);
  qh_RANDOMseed_(qh, seed);
  for (j=0; j<numpoints; j++) {
    point= points + j*dim;
    for (k=0; k < dim; k++) {
      realr= qh_RANDOMint;
      point[k]= 2.0 * realr/(qh_RANDOMmax+1) - 1.0;
    }
  }
} /*.makeDelaunay.*/

/*--------------------------------------------------
-findDelaunay- find the Delaunay triangle or adjacent triangle for [0.5,0.5,...]
  assumes dim < 100
notes:
  See <a href="../../html/qh-code.htm#findfacet">locate a facet with qh_findbestfacet()</a>
  calls qh_setdelaunay() to project the point to a parabaloid
warning:
  Errors if it finds a tricoplanar facet ('Qt').  The corresponding Delaunay triangle
  is in the set of tricoplanar facets or one of their neighbors.  This search
  is not implemented here.
*/
void findDelaunay(qhT *qh, int dim) {
  int k;
  coordT point[ 100];
  boolT isoutside;
  realT bestdist;
  facetT *facet;
  vertexT *vertex, **vertexp;

  for (k=0; k < dim; k++)
    point[k]= 0.5;
  qh_setdelaunay(qh, dim+1, 1, point);
  facet= qh_findbestfacet(qh, point, qh_ALL, &bestdist, &isoutside);
  if (facet->tricoplanar) {
    fprintf(stderr, "findDelaunay: search not implemented for triangulated, non-simplicial Delaunay regions (tricoplanar facet, f%d).\n",
       facet->id);
    qh_errexit(qh, qh_ERRqhull, facet, NULL);
  }
  FOREACHvertex_(facet->vertices) {
    for (k=0; k < dim; k++)
      printf("%5.2f ", vertex->point[k]);
    printf("\n");
  }
} /*.findDelaunay.*/

/*--------------------------------------------------
-makehalf- set points to halfspaces for a (dim)-dimensional diamond
  points is numpoints X dim+1

  each halfspace consists of dim coefficients followed by an offset
*/
void makehalf(coordT *points, int numpoints, int dim) {
  int j,k;
  coordT *point;

  for (j=0; j<numpoints; j++) {
    point= points + j*(dim+1);
    point[dim]= -1.0; /* offset */
    for (k=dim; k--; ) {
      if (j & ( 1 << k))
        point[k]= 1.0;
      else
        point[k]= -1.0;
    }
  }
} /*.makehalf.*/

#define DIM 3     /* dimension of points, must be < 31 for SIZEcube */
#define SIZEcube (1<<DIM)
#define SIZEdiamond (2*DIM)
#define TOTpoints (SIZEcube + SIZEdiamond)

/*--------------------------------------------------
-main- derived from Qhull-template in user_r.c

  see program header

  this contains three runs of Qhull for convex hull, Delaunay
  triangulation or Voronoi vertices, and halfspace intersection

*/
int main(int argc, char *argv[]) {
  int dim= DIM;             /* dimension of points */
  int numpoints;            /* number of points */
  coordT points[(DIM+1)*TOTpoints]; /* array of coordinates for each point */
  coordT *rows[TOTpoints];
  boolT ismalloc= False;    /* True if qhull should free points in qh_freeqhull() or reallocation */
  char flags[250];          /* option flags for qhull, see qh-quick.htm */
  FILE *outfile= stdout;    /* output from qh_produce_output()
                               use NULL to skip qh_produce_output() */
  FILE *errfile= stderr;    /* error messages from qhull code */
  int exitcode;             /* 0 if no error from qhull */
  facetT *facet;            /* set by FORALLfacets */
  int curlong, totlong;     /* memory remaining after qh_memfreeshort, used if !qh_NOmem  */
  int i;

  qhT qh_qh;                /* Qhull's data structure.  First argument of most calls */
  qhT *qh= &qh_qh;

  QHULL_LIB_CHECK

  qh_zero(qh, errfile);

  printf("\n========\nuser_eg 'cube qhull options' 'Delaunay options' 'halfspace options'\n\
\n\
This is the output from user_eg_r.c.  It shows how qhull() may be called from\n\
an application, via Qhull's shared, reentrant library.  user_eg is not part of\n\
Qhull itself.  If user_eg fails immediately, user_eg_r.c was incorrectly linked\n\
to Qhull's non-reentrant library, libqhull.\n\
Try -- user_eg 'T1' 'T1' 'T1'\n\
\n");

  /*
    Run 1: convex hull
  */
  printf( "\n========\ncompute convex hull of cube after rotating input\n");
  sprintf(flags, "qhull s Tcv %s", argc >= 2 ? argv[1] : "");
  numpoints= SIZEcube;
  makecube(points, numpoints, DIM);
  for (i=numpoints; i--; )
    rows[i]= points+dim*i;
  qh_printmatrix(qh, outfile, "input", rows, numpoints, dim);
  fflush(NULL);
  exitcode= qh_new_qhull(qh, dim, numpoints, points, ismalloc,
                      flags, outfile, errfile);
  fflush(NULL);
  if (!exitcode) {                  /* if no error */
    /* 'qh->facet_list' contains the convex hull */
    print_summary(qh);
    FORALLfacets {
       /* ... your code ... */
    }
  }
#ifdef qh_NOmem
  qh_freeqhull(qh, qh_ALL);
#else
  qh_freeqhull(qh, !qh_ALL);                   /* free long memory  */
  qh_memfreeshort(qh, &curlong, &totlong);    /* free short memory and memory allocator */
  if (curlong || totlong)
    fprintf(errfile, "qhull internal warning (user_eg, #1): did not free %d bytes of long memory (%d pieces)\n", totlong, curlong);
#endif

  /*
    Run 2: Delaunay triangulation, reusing the previous qh/qh_qh
  */

  printf( "\n========\ncompute %d-d Delaunay triangulation\n", dim);
  sprintf(flags, "qhull s d Tcv %s", argc >= 3 ? argv[2] : "");
  numpoints= SIZEcube;
  makeDelaunay(qh, points, numpoints, dim, (int)time(NULL));
  for (i=numpoints; i--; )
    rows[i]= points+dim*i;
  qh_printmatrix(qh, outfile, "input", rows, numpoints, dim);
  fflush(NULL);
  exitcode= qh_new_qhull(qh, dim, numpoints, points, ismalloc,
                      flags, outfile, errfile);
  fflush(NULL);
  if (!exitcode) {                  /* if no error */
    /* 'qh->facet_list' contains the convex hull */
    /* If you want a Voronoi diagram ('v') and do not request output (i.e., outfile=NULL),
       call qh_setvoronoi_all() after qh_new_qhull(). */
    print_summary(qh);
    FORALLfacets {
       /* ... your code ... */
    }
    printf( "\nfind %d-d Delaunay triangle or adjacent triangle closest to [0.5, 0.5, ...]\n", dim);
    exitcode= setjmp(qh->errexit);
    if (!exitcode) {
      /* Trap Qhull errors from findDelaunay().  Without the setjmp(), Qhull
         will exit() after reporting an error */
      qh->NOerrexit= False;
      findDelaunay(qh, DIM);
    }
    qh->NOerrexit= True;
  }
  {
    coordT pointsB[DIM*TOTpoints]; /* array of coordinates for each point */

    qhT qh_qhB;    /* Create a new instance of Qhull (qhB) */
    qhT *qhB= &qh_qhB;
    qh_zero(qhB, errfile);

    printf( "\n========\nCompute a new triangulation as a separate instance of Qhull\n");
    sprintf(flags, "qhull s d Tcv %s", argc >= 3 ? argv[2] : "");
    numpoints= SIZEcube;
    makeDelaunay(qhB, pointsB, numpoints, dim, (int)time(NULL)+1);
    for (i=numpoints; i--; )
      rows[i]= pointsB+dim*i;
    qh_printmatrix(qhB, outfile, "input", rows, numpoints, dim);
    fflush(NULL);
    exitcode= qh_new_qhull(qhB, dim, numpoints, pointsB, ismalloc,
                      flags, outfile, errfile);
    fflush(NULL);
    if (!exitcode)
      print_summary(qhB);
    printf( "\n========\nFree memory allocated by the new instance of Qhull, and redisplay the old results.\n");
#ifdef qh_NOmem
    qh_freeqhull(qh, qh_ALL);
#else
    qh_freeqhull(qhB, !qh_ALL);                 /* free long memory */
    qh_memfreeshort(qhB, &curlong, &totlong);  /* free short memory and memory allocator */
    if (curlong || totlong)
        fprintf(errfile, "qhull internal warning (user_eg, #4): did not free %d bytes of long memory (%d pieces)\n", totlong, curlong);
#endif
    printf( "\n\n");
    print_summary(qh);  /* The other instance is unchanged */
    /* Exiting the block frees qh_qhB */
  }
#ifdef qh_NOmem
  qh_freeqhull(qh, qh_ALL);
#else
  qh_freeqhull(qh, !qh_ALL);                 /* free long memory */
  qh_memfreeshort(qh, &curlong, &totlong);  /* free short memory and memory allocator */
  if (curlong || totlong)
    fprintf(errfile, "qhull internal warning (user_eg, #2): did not free %d bytes of long memory (%d pieces)\n", totlong, curlong);
#endif

  /*
    Run 3: halfspace intersection about the origin
  */
  printf( "\n========\ncompute halfspace intersection about the origin for a diamond\n");
  sprintf(flags, "qhull H0 s Tcv %s", argc >= 4 ? argv[3] : "Fp");
  numpoints= SIZEcube;
  makehalf(points, numpoints, dim);
  for (i=numpoints; i--; )
    rows[i]= points+(dim+1)*i;
  qh_printmatrix(qh, outfile, "input as halfspace coefficients + offsets", rows, numpoints, dim+1);
  fflush(NULL);
  /* use qh_sethalfspace_all to transform the halfspaces yourself.
     If so, set 'qh->feasible_point and do not use option 'Hn,...' [it would retransform the halfspaces]
  */
  exitcode= qh_new_qhull(qh, dim+1, numpoints, points, ismalloc,
                      flags, outfile, errfile);
  fflush(NULL);
  if (!exitcode)
    print_summary(qh);
#ifdef qh_NOmem
  qh_freeqhull(qh, qh_ALL);
#else
  qh_freeqhull(qh, !qh_ALL);
  qh_memfreeshort(qh, &curlong, &totlong);
  if (curlong || totlong)  /* could also check previous runs */
    fprintf(stderr, "qhull internal warning (user_eg, #3): did not free %d bytes of long memory (%d pieces)\n",
       totlong, curlong);
#endif
  return exitcode;
} /* main */
