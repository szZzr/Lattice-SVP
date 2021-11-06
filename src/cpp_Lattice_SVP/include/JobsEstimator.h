//
// Created by Giorgos Rizos on 13/3/21.
//

#ifndef PYTHONIC_JOBSESTIMATOR_H
#define PYTHONIC_JOBSESTIMATOR_H
#include "Jobs.hpp"
#include "Tree.hpp"
#include <cmath>
#include <cstdio>

//enum Condition {VIA_NODES, VIA_DEPTH};
//NOTE: typedef Pair<T> TPair;
template<class TPair, class T, class U>
class JobsEstimator: public Jobs<T> {
public:
    JobsEstimator(std::size_t req_nodes, std::size_t dims,U R, Condition cond);
    JobsEstimator(std::size_t req_nodes, std::size_t dims,U*R, Condition cond);
    ~JobsEstimator();
    void set_parameters(U *norms, U **M);
    void set_parameters(U *norms, U *M); //Cython wrapper
    void set_jobs();
    void show_tree();



    typedef std::function<bool(T)> expr_type;
private:
    JobsEstimator(std::size_t req_nodes, std::size_t dims, Condition cond);
    struct Interval{
        T lower_bound, upper_bound;
    };
    Tree<TPair> *tree;

    Condition condition;
    std::size_t request;
    U *norms, *R, **M;
    U c_help_fun(std::size_t, T*);
    U quot_help_fun(std::size_t, T*);
    Interval range_help_fun(std::size_t, T*);
    void jobs_intervals();
    expr_type define_expresion();
    inline bool  node_spawning(Node<TPair>);

};

typedef Pair<long> LPair;
#endif //PYTHONIC_JOBSESTIMATOR_H
