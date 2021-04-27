cdef extern from "<cmath>" namespace "std" nogil:
        #sqrt
        double sqrt(double x)
        float sqrt(float x);
        long double sqrt(long double x);
        long sqrt (long x);
        #ceil
        double ceil(double x);
        float ceil(float x);
        long double ceil(long double x);
        long ceil(long x);
        #abs
        double abs(double x)
        float abs(float x)
        int abs(int x)
        long double abs(long double x)
        long abs(long x)
        #round
        double round(double x)
        float roundf(float x)
        long double roundl(long double x)

cdef extern from "<cstring>" nogil:
    void* memcpy(void* destination, const void* source, size_t num)


cdef extern from "cpp_Lattice_SVP/include/Pair.hpp":
    cdef cppclass Pair[long]:
        int limit
        size_t length
        size_t pos
        long* job
        long* get_job()
        void show()
        bint operator =(Pair)
        Pair tempo(int t)
        void show_(char*)
        void deserialize(char*)


cdef extern from "cpp_Lattice_SVP/include/Jobs.hpp":
    cdef cppclass Condition:
        pass
    cdef cppclass Jobs[long]:
        Jobs()
        Jobs(size_t size_job)
        char* serialize(Jobs)
        char* next_pair()
        void set_jobs()
        void deserialize(char *)
        void set_parameters(int range, size_t size_jobs)
        void show()
        size_t get_size_jobs()
        void show_array(long* arr, size_t size)
        void show_array2d(long* arr, size_t size)
        # void show_array(double* arr, size_t size)
        # void show_array2d(double*arr, size_t size)


cdef extern from "cpp_Lattice_SVP/include/Jobs.hpp" namespace "Condition":
    cpdef Condition VIA_NODES
    cpdef Condition VIA_DEPTH


cdef extern from "cpp_Lattice_SVP/include/JobsPair.h":
    cdef cppclass JobsPair[long, double]:
        JobsPair(size_t request, size_t dims, double R, Condition condition)
        JobsPair(size_t request, size_t dims, double *R, Condition condition)
        char* serialize(Jobs)
        char* next_pair()
        void set_jobs()
        void deserialize(char *)
        void set_parameters(double* range, double* size_jobs)
        void show()
        size_t get_size_jobs()


