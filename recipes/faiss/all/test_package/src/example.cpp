#include <faiss/IndexFlat.h>
#ifdef WITH_GPU
#include <faiss/gpu/GpuIndexFlat.h>
#include <faiss/gpu/StandardGpuResources.h>
#endif

using faiss::idx_t;

int main() {
    int d = 64;     // dimension
    int nb = 10000; // database size
    int nq = 10;    // nb of queries
    float* xb = new float[d * nb];
    float* xq = new float[d * nq];
    for (int i = 0; i < nb; i++) {
        for (int j = 0; j < d; j++)
            xb[d * i + j] = drand48();
        xb[d * i] += i / 1000.;
    }
    for (int i = 0; i < nq; i++) {
        for (int j = 0; j < d; j++)
            xq[d * i + j] = drand48();
        xq[d * i] += i / 1000.;
    }

#ifndef WITH_GPU
    faiss::IndexFlatL2 index(d); // call constructor
    printf("CPU index:\n");
#else
    faiss::gpu::StandardGpuResources res;
    faiss::gpu::GpuIndexFlatL2 index(&res, d);
    printf("GPU index:\n");
#endif

    printf("is_trained = %s\n", index.is_trained ? "true" : "false");
    index.add(nb, xb); // add vectors to the index
    printf("ntotal = %ld\n", index.ntotal);

    int k = 4;
    { // sanity check: search 5 first vectors of xb
        idx_t* I = new idx_t[k * 5];
        float* D = new float[k * 5];
        index.search(5, xb, k, D, I);
        printf("I=\n");
        for (int i = 0; i < 5; i++) {
            for (int j = 0; j < k; j++)
                printf("%5ld ", I[i * k + j]);
            printf("\n");
        }
        delete[] I;
        delete[] D;
    }
    { // search xq
        idx_t* I = new idx_t[k * nq];
        float* D = new float[k * nq];
        index.search(nq, xq, k, D, I);
        for (int i = 0; i < 5; i++) {
            for (int j = 0; j < k; j++)
                printf("%5ld ", I[i * k + j]);
            printf("\n");
        }
        delete[] I;
        delete[] D;
    }
}
