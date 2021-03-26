#include "graphene.h"
#include <stdio.h>

int main (int argc, char **argv)
{
  graphene_point_t *p = graphene_point_init(graphene_point_alloc(), 3, 4);;
  graphene_vec2_t * vect = graphene_vec2_alloc();
  float res;
  graphene_point_to_vec2(p, vect);
  res = graphene_vec2_length(vect);
  graphene_vec2_free(vect);
  graphene_point_free(p);
  if(res != 5)
  {
    return 1;
  }
  return 0;
}
