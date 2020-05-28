#include "libqhull/qhull_a.h"

/*-------------------------------------------------
-internal function prototypes
*/
void print_summary(void);
void makecube(coordT *points, int numpoints, int dim);
void makeDelaunay(coordT *points, int numpoints, int dim, int seed);
void findDelaunay(int dim);
void makehalf(coordT *points, int numpoints, int dim);

/*-------------------------------------------------
-print_summary( )
*/
void print_summary(void) {
  facetT *facet;
  int k;

  printf("\n%d vertices and %d facets with normals:\n",
                 qh num_vertices, qh num_facets);
  FORALLfacets {
    for (k=0; k < qh hull_dim; k++)
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
  makeDelaunay() in user_eg2.c uses qh_setdelaunay() to project points in place.
*/
void makeDelaunay(coordT *points, int numpoints, int dim, int seed) {
  int j,k;
  coordT *point, realr;

  printf("seed: %d\n", seed);
  qh_RANDOMseed_(seed);
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
void findDelaunay(int dim) {
  int k;
  coordT point[ 100];
  boolT isoutside;
  realT bestdist;
  facetT *facet;
  vertexT *vertex, **vertexp;

  for (k=0; k < dim; k++)
    point[k]= 0.5;
  qh_setdelaunay(dim+1, 1, point);
  facet= qh_findbestfacet(point, qh_ALL, &bestdist, &isoutside);
  if (facet->tricoplanar) {
    fprintf(stderr, "findDelaunay: search not implemented for triangulated, non-simplicial Delaunay regions (tricoplanar facet, f%d).\n",
       facet->id);
    qh_errexit(qh_ERRqhull, facet, NULL);
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
-main- derived from Qhull-template in user.c

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

  QHULL_LIB_CHECK


  printf("\n========\nuser_eg 'cube qhull options' 'Delaunay options' 'halfspace options'\n\
\n\
This is the output from user_eg.c.  It shows how qhull() may be called from\n\
an application, via Qhull's shared, non-rentrant library.  user_eg is not part of\n\
Qhull itself.  If user_eg fails immediately, user_eg.c was incorrectly linked\n\
to Qhull's reentrant library, libqhull_r.\n\
Try -- user_eg 'T1' 'T1' 'T1'\n\
\n");

#if qh_QHpointer  /* see user.h */
  if (qh_qh){
      printf("QH6233: Qhull link error.  The global variable qh_qh was not initialized\n\
to NULL by global.c.  Please compile user_eg.c with -Dqh_QHpointer_dllimport\n\
as well as -Dqh_QHpointer, or use libqhullstatic, or use a different tool chain.\n\n");
      return -1;
  }
#endif

  /*
    Run 1: convex hull
  */
  printf( "\n========\ncompute convex hull of cube after rotating input\n");
  sprintf(flags, "qhull s Tcv %s", argc >= 2 ? argv[1] : "");
  numpoints= SIZEcube;
  makecube(points, numpoints, DIM);
  for (i=numpoints; i--; )
    rows[i]= points+dim*i;
  qh_printmatrix(outfile, "input", rows, numpoints, dim);
  fflush(NULL);
  exitcode= qh_new_qhull(dim, numpoints, points, ismalloc,
                      flags, outfile, errfile);
  fflush(NULL);
  if (!exitcode) {                  /* if no error */
    /* 'qh facet_list' contains the convex hull */
    print_summary();
    FORALLfacets {
       /* ... your code ... */
    }
  }
#ifdef qh_NOmem
  qh_freeqhull(qh_ALL);
#else
  qh_freeqhull(!qh_ALL);                   /* free long memory  */
  qh_memfreeshort(&curlong, &totlong);    /* free short memory and memory allocator */
  if (curlong || totlong)
    fprintf(errfile, "qhull internal warning (user_eg, #1): did not free %d bytes of long memory (%d pieces)\n", totlong, curlong);
#endif

  /*
    Run 2: Delaunay triangulation, reusing the previous qh/qh_qh
  */

  printf( "\n========\ncompute %d-d Delaunay triangulation\n", dim);
  sprintf(flags, "qhull s d Tcv %s", argc >= 3 ? argv[2] : "");
  numpoints= SIZEcube;
  makeDelaunay(points, numpoints, dim, (int)time(NULL));
  for (i=numpoints; i--; )
    rows[i]= points+dim*i;
  qh_printmatrix(outfile, "input", rows, numpoints, dim);
  fflush(NULL);
  exitcode= qh_new_qhull(dim, numpoints, points, ismalloc,
                      flags, outfile, errfile);
  fflush(NULL);
  if (!exitcode) {                  /* if no error */
    /* 'qh facet_list' contains the convex hull */
    /* If you want a Voronoi diagram ('v') and do not request output (i.e., outfile=NULL),
       call qh_setvoronoi_all() after qh_new_qhull(). */
    print_summary();
    FORALLfacets {
       /* ... your code ... */
    }
    printf( "\nfind %d-d Delaunay triangle or adjacent triangle closest to [0.5, 0.5, ...]\n", dim);
    exitcode= setjmp(qh errexit);
    if (!exitcode) {
      /* Trap Qhull errors from findDelaunay().  Without the setjmp(), Qhull
         will exit() after reporting an error */
      qh NOerrexit= False;
      findDelaunay(DIM);
    }
    qh NOerrexit= True;
  }
#if qh_QHpointer  /* see user.h */
  {
    qhT *oldqhA, *oldqhB;
    coordT pointsB[DIM*TOTpoints]; /* array of coordinates for each point */

    printf( "\n========\nCompute a new triangulation as a separate instance of Qhull\n");
    oldqhA= qh_save_qhull();
    sprintf(flags, "qhull s d Tcv %s", argc >= 3 ? argv[2] : "");
    numpoints= SIZEcube;
    makeDelaunay(pointsB, numpoints, dim, (int)time(NULL)+1);
    for (i=numpoints; i--; )
      rows[i]= pointsB+dim*i;
    qh_printmatrix(outfile, "input", rows, numpoints, dim);
    fflush(NULL);
    exitcode= qh_new_qhull(dim, numpoints, pointsB, ismalloc,
                      flags, outfile, errfile);
    fflush(NULL);
    if (!exitcode)
      print_summary();
    printf( "\n========\nFree memory allocated by the new instance of Qhull, and redisplay the old results.\n");
    oldqhB= qh_save_qhull();
    qh_restore_qhull(&oldqhA);
    print_summary();
    printf( "\nfree first triangulation and restore second one.\n");
    qh_freeqhull(qh_ALL);               /* free short and long memory used by first call */
                                         /* do not use qh_memfreeshort */
    qh_restore_qhull(&oldqhB);
    printf( "\n\n");
    print_summary();
  }
#endif

#ifdef qh_NOmem
  qh_freeqhull(qh_ALL);
#else
  qh_freeqhull(!qh_ALL);                 /* free long memory */
  qh_memfreeshort(&curlong, &totlong);  /* free short memory and memory allocator */
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
  qh_printmatrix(outfile, "input as halfspace coefficients + offsets", rows, numpoints, dim+1);
  fflush(NULL);
  /* use qh_sethalfspace_all to transform the halfspaces yourself.
     If so, set 'qh feasible_point and do not use option 'Hn,...' [it would retransform the halfspaces]
  */
  exitcode= qh_new_qhull(dim+1, numpoints, points, ismalloc,
                      flags, outfile, errfile);
  fflush(NULL);
  if (!exitcode)
    print_summary();
#ifdef qh_NOmem
  qh_freeqhull(qh_ALL);
#else
  qh_freeqhull(!qh_ALL);
  qh_memfreeshort(&curlong, &totlong);
  if (curlong || totlong)  /* could also check previous runs */
    fprintf(stderr, "qhull internal warning (user_eg, #3): did not free %d bytes of long memory (%d pieces)\n",
       totlong, curlong);
#endif
  return exitcode;
} /* main */
