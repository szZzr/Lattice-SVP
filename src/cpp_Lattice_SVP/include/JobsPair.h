//
// Created by Giorgos Rizos on 17/3/21.
//

#ifndef PYTHONIC_JOBSPAIR_H
#define PYTHONIC_JOBSPAIR_H
#include "JobsEstimator.h"
/*
 * This class is only a wrapper for JobsEstimator class
 * to encapsulate this class in cython's module. The main
 * issue is with template-classes in cython.
 */
template <class T, class U>
class JobsPair : public JobsEstimator< Pair<T>, T ,U> {
using JobsEstimator< Pair<T>, T ,U>::JobsEstimator;
};


#endif //PYTHONIC_JOBSPAIR_H
