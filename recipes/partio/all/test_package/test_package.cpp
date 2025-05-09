#include <cstdlib>
#include <Partio.h>
#ifdef PARTIO_WIN32
#define M_PI (3.14159265359893238)
#endif

#include <cmath>

using namespace Partio;
int main(void) {
    ParticlesDataMutable* p=create();
    ParticleAttribute positionAttr=p->addAttribute("position",VECTOR,3);
    ParticleAttribute normalAttr=p->addAttribute("normal",VECTOR,3);
    int n=30;
    for(int i=0;i<n;i++){
        int particle=p->addParticle();
        float* pos=p->dataWrite<float>(positionAttr,particle);
        float* norm=p->dataWrite<float>(normalAttr,particle);
        float theta=i*2*M_PI/(float)n;
        pos[2]=cos(theta);
        pos[0]=sin(theta);
        pos[1]=0;
        norm[0]=cos(theta);
        norm[2]=-sin(theta);
        norm[1]=0;
        
    }
    write("circle.00001.bgeo",*p);
    write("circle.00001.geo",*p);
    write("circle.00001.bin",*p);
    write("circle.00001.pdc",*p);
    write("circle.00001.pdb",*p);
    write("circle.00001.pda",*p);
    write("circle.00001.ptc",*p);
    write("circle.00001.rib",*p);
    write("circle.00001.mc",*p);

   
    p->release();

    return EXIT_SUCCESS;
}
