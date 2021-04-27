//
// Created by Giorgos Rizos on 13/3/21.
//

#include "JobsEstimator.h"
///CONSTRUCTOR
template<class TPair, class T, class U>
JobsEstimator<TPair,T,U>::JobsEstimator(std::size_t request, std::size_t dims, Condition condition) {
    this->request = request;
    this->condition = condition;
    this-> size_job = dims;
    this-> size_jobs = 0;
    this-> norms = nullptr;
    this-> M = nullptr;
    this->tree = new Tree<TPair>;
    if (condition == Condition::VIA_DEPTH and request>--dims){
        this->request = dims;
        std::cout<<"Your request is out of range. So, it initializes with default "
                   "constructor's settings, that means requested depth equals to dimensions.\n"
                   "\t- Requested Depth: "<<++dims<<std::endl;
    }
}

template<class TPair, class T, class U>
JobsEstimator<TPair,T,U>::JobsEstimator(std::size_t request, std::size_t dims,U R, Condition condition)
:JobsEstimator(request, dims, condition){
    this-> R = new U[this->size_job];
    for(int i=0; i<this->size_job;i++)
        this-> R[i] = R;
}

template<class TPair, class T, class U>
JobsEstimator<TPair,T,U>::JobsEstimator(std::size_t request, std::size_t dims,U *R, Condition condition)
:JobsEstimator(request, dims, condition){
    this-> R = R;
}

template<class TPair, class T, class U>
JobsEstimator<TPair,T,U>::~JobsEstimator(){
    delete this->tree;
}

///OVERWRITTEN
template<class TPair, class T, class U>
void JobsEstimator<TPair,T,U>::set_parameters(U *norms, U **M) {
    this->norms = norms;
    this->M = M;
}

template<class TPair, class T, class U>
void JobsEstimator<TPair,T,U>::set_parameters(U *norms, U *M) {
    /*Gets M-array as 1d-continuous array from cython and
     * converts it to 2d-carray. This happens because cython
     * handles M-array as a memoryview.
     * */
    this->norms = norms;
    this->M = new U*[this->size_job];
    std::size_t begin, end;
    for (int i=0; i<this->size_job;i++){
        begin = i*this->size_job;
        end = (i+1)*this->size_job;
        this->M[i] = new U[this->size_job];
        std::copy(&M[begin], &M[end], &this->M[i][0]);
    }
}

template<class TPair, class T, class U>
void JobsEstimator<TPair,T,U>::set_jobs() {
    jobs_intervals();
//    tree.show("BFS");
    typename Tree<TPair>::LeavesSet  leaves = tree->get_leaves();

    for(std::size_t leaf: leaves){
        Node<TPair> *node = tree->find_node(leaf);
        TPair task = node->get_data();
        this->jobs.push_back(task);
    }
    this->size_jobs = this->jobs.size();
    std::cout<<"SIZE OF JOBS: "<<this->size_jobs<<std::endl;
}


///OPERATION
template<class TPair, class T, class U>
U JobsEstimator<TPair,T,U>::c_help_fun(std::size_t index, T* x){
    /*
     * Sum of products of the GSO and Basis coefficients
    *
    *This is an inline function which has a lot of calls. The
    *first idea was to make a parallel implementation but the
    *parallel setting overhead increase the execution time, so
    *preferred the linear one.
    *:param i: the index of matrix-M
    *:param x: basis coefficients
    *:param M: the matrix of GSO coefficients
    *:param n: lattice's rank
    *:return: sum of product
     */
    U sum = 0;
    if (index+1>this->size_job) return sum; //FIXME: Swtich with try

    for(std::size_t i=index+1; i<this->size_job; i++){
//        printf("x[%d]: %d * M[%d][%d]: %f\n", (int) i,(int) x[i],(int) i,(int) index, (double) M[i][index]);
        sum += x[i]*M[i][index];
    }
    return sum;
}

template<class TPair, class T, class U>
U JobsEstimator<TPair,T,U>::quot_help_fun(std::size_t index, T* x){
    /*
     *
     */
    U suml = 0;
    if (index+1>this->size_job) return suml; //FIXME: Swtich with try

    U* c = new U[this->size_job]();
    c[index] = c_help_fun(index, x);
    for(std::size_t i = index+1; i<this->size_job; i++){
        // suml += norms[j] * ((x[j] - c[j])**2)
        suml += this->norms[i] * (std::pow(x[i] - c[i],2));
    }
    // sqrt(R**2-suml)/norms[index]
    return std::sqrt(std::pow(this->R[index],2) - suml)/this->norms[index];
}

template<class TPair, class T, class U>
typename JobsEstimator<TPair,T,U>::Interval
JobsEstimator<TPair,T,U>::range_help_fun(std::size_t height, T* x){
    U sum = - c_help_fun(height, x);
    U quot = quot_help_fun(height, x);
    T lower = (T) sum - quot;
    T upper = (T) sum + quot;
    return  {lower, upper};
}

template<class TPair, class T, class U>
typename JobsEstimator<TPair,T,U>::expr_type
JobsEstimator<TPair,T,U>::define_expresion(){
    /* Support Constructor's Method
     * Define condition consist a support constructor's function.
     * Through this method is determined the termination condition of tasks
     * enumeration.
     * case VIA_NODES: user defines the requested number of nodes that is
     * the number of tasks-jobs
     * case VIA_DEPTH: user defines the requested depth of tree
     */
    switch(this->condition){
        case Condition::VIA_NODES:
            return [&](T range) -> bool {
                // Requested Nodes-Task
                return range < this->request;
            };
        case Condition::VIA_DEPTH:
            return [&](T) -> bool {
                // Requested Depth
                return this->request >= this->tree->get_height();
            };
        default:
            std::cout<<"Construction has FAILED\n";
            delete  this; //FOR NEW-OBJECT CASE
    }
}

template<class TPair, class T, class U>
inline void JobsEstimator<TPair,T,U>::
node_spawning(Node<TPair> node){
    /*
     * Method for node reproduction
     *
     * Takes as argument a node, parent node, applies enumeration techniques to
     * reproduce its children and imports them to jobs-tree. The height of tree
     */
    T range;
    TPair parent = node.get_data();
    std::size_t height = node.depth + 1;
    std::size_t index =  this->size_job - height;
    for (int i = 0; i<=parent.limit; i++){
        T* x =  new T[this->size_job]();
        std::copy(parent.get_job(), parent.get_job() + this->size_job, x);
        x[index] = i;
        range = range_help_fun(height, x).upper_bound;
        TPair child(range, this->size_job, x, index);
        std::ostringstream tag;
        tag<<height<<"::"<<this->tree->get_no_nodes()<<" => "<<i;
        this->tree->create_node(node.get_id(), tag.str(), child);
    }
}

template<class TPair, class T, class U>
void JobsEstimator<TPair,T,U>::jobs_intervals(){
    /*
     * The heart of Jobs Estimator.
     */
    T* x_root = new T[this->size_job]();
    T range = range_help_fun(this->tree->get_height() + 1, x_root).upper_bound;
    TPair root(range, this->size_job, x_root, this->size_job);
    this->tree->create_node("RooT", root); // data=(_range, x, depth-1)

    expr_type expr = define_expresion();
    typename Tree<TPair>::Iterator bfs = this->tree->begin();
    T total_range = 0;

    while(expr(total_range)){
        Node<TPair> parent = (*bfs);
        node_spawning(parent);
        total_range += parent.get_data().limit + 1;
        bfs++;
    }
    std::cout<<"TOTAL RANGE: "<<total_range<<std::endl;
}

template<class TPair, class T, class U>
void JobsEstimator<TPair,T,U>::show_tree() {
    tree->show(Tree<TPair>::Tree_Mode::DFS);
}
template class JobsEstimator<Pair<long>, long, double>;








