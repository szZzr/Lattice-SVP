//
//  Tree.cpp
//  pythonic
//
//  Created by Giorgos Rizos on 7/3/21.
//  Copyright © 2021 Giorgos Rizos. All rights reserved.
//

#include "Tree.hpp"

///CONSTRUCTORS
template <class T>
Tree<T>::Tree(){
    this->root = nullptr;
    this->height = 0;
}

template<class T>
Tree<T>::Tree(Node<T> *root){
    insert_node(root);
}

///GETTERS
template<class T>
typename Tree<T>::NodesMap Tree<T>::get_vertices(){
    return this->vertices;
}

template<class T>
std::size_t Tree<T>::get_height() {
    return this->height;
}

template<class T>
std::size_t Tree<T>::get_no_nodes(){
    return this->vertices.size();
}

template<class T>
typename Tree<T>::LeavesSet
Tree<T>::get_leaves(){
    return this->leaves;
}

template<class T>
Node<T>* Tree<T>::find_node(std::size_t node_id) {
    return vertices.find(node_id)->second;
}
///OPERATION
template<class T>
inline void Tree<T>::new_vertex(std::size_t parent_id, Node<T> *node){
    if (parent_id != node->get_id()) //and leaves.find(parent_id)
        leaves.erase(parent_id);
    vertices.insert({node->get_id(), node});
    leaves.insert(node->get_id());
}

template<class T>
void Tree<T>::insert_node(Node<T> *root){ //ROOT NODE
//    typedef std::map<size_t, Node<T> *> NodesMap;
    this->root = root;
    this->root->depth = 0; //Node's Depth
    this->height = 0;

    new_vertex(root->get_id(), root);
}

template<class T>
void Tree<T>::insert_node(std::size_t parent_id, Node<T> *child){
//    typedef std::map<size_t, Node<T> *> NodesMap;
    typename NodesMap::iterator it;
    it = vertices.find(parent_id);
    Node<T> *parent = it->second;
    parent->new_child(child);
    child->depth = parent->depth + 1;
    if(child->depth > this->height)
        this->height = child->depth;

    new_vertex(parent_id, child);
}

template<class T>
Node<T>* Tree<T>::create_node(std::string tag , T data){
    Node<T> *root = new Node<T>(tag, data);
    this->insert_node(root);
    return root;
}

template<class T>
Node<T>* Tree<T>::create_node(size_t parent_id, std::string tag , T data){
    Node<T> *child = new Node<T>(tag, data);
    this->insert_node(parent_id, child);
    return child;
}

template<class T>
std::queue<size_t> Tree<T>::dfs(Node<T> *node){
    std::queue<size_t> dfs_queue;
    Node<T> *visitor;
    
    std::stack<size_t> Stack;
    Stack.push(node->get_id());
    while (!Stack.empty()) {
        visitor = vertices.find(Stack.top())->second;
        dfs_queue.push(visitor->get_id());
        Stack.pop();
        NodesMap children = visitor->get_children();
        typename NodesMap::iterator it;
        
        for(it = children.begin(); it != children.end(); ++it){
            Stack.push(it->first);
        }
    }
    return dfs_queue;
}

template<class T>
std::queue<size_t> Tree<T>::bfs(Node<T> *node){
    std::queue<size_t> bfs_queue;
    Node<T> *visitor;
    
    std::queue<size_t> Queue;
    Queue.push(node->get_id());
    while(!Queue.empty()){
        visitor = vertices.find(Queue.front())->second;
        bfs_queue.push(visitor->get_id());
        Queue.pop();
        NodesMap children = visitor->get_children();
        typename NodesMap::iterator it;
        
        for(it = children.begin(); it != children.end(); ++it){
            Queue.push(it->first);
        }
    }
    return bfs_queue;
}


template<class T>
void Tree<T>::show(Tree::Tree_Mode mode){
    std::queue<size_t> results;
    if (mode == DFS)
        results = dfs(root);
    else if (mode == BFS) {
        results = bfs(root);
        printf("MODE IS BFS\n");
    }
    Node<T> *visitor;
    int depth = 0;
    while(!results.empty()){
        visitor = vertices.find(results.front())->second;
//        T limit = visitor->get_data();
        results.pop();
        depth = visitor->depth;
        if (typeid(T) == typeid(Pair<long>))
            printf("%* |\n%* |\-\->%s\n",depth*5, depth*5, visitor->tag.c_str());
        else
            printf("%* |\n%* |\-\->%s:%d\n",depth*5, depth*5, visitor->tag.c_str());  //visitor->get_data()
    }
}

///OPERATORS
template<class T>
Tree<T> Tree<T>::operator=(Tree<T> tree){
    this->root = tree.root;
    this->vertices = tree.get_vertices();
    return *this;
}


///ITERATOR
template<class T> //prefix
typename Tree<T>::Iterator& Tree<T>::Iterator::operator++(){
    _ptr = this->bfs_q.front();
    this->bfs_q.pop();
    
    NodesMap children = _ptr->get_children();
    typename NodesMap::iterator it;
    for(it = children.begin(); it != children.end(); ++it){
        this->bfs_q.push(it->second);
    }
    this->_ptr = bfs_q.front();
    return *this;
}

template<class T>//postfix
typename Tree<T>::Iterator Tree<T>::Iterator::operator++(int){
    Iterator tmp = *this; //value_type
    tmp = this->bfs_q.front();
    this->bfs_q.pop();
    NodesMap children = tmp->get_children();
    typename NodesMap::iterator it;

    for(it = children.begin(); it != children.end(); ++it){
        this->bfs_q.push(it->second);
//        auto * node = (Node<Pair<long>>*)it->second;
//        auto pair = (Pair<long>) node->get_data();
//        pair.show();
    }
    this->_ptr = this->bfs_q.front();
    return tmp;
}

template<class T>
typename Tree<T>::Iterator Tree<T>::begin(){
    Iterator it = Iterator(root);
    it.bfs_q.push(root);
    return it;
}

template<class T>
bool Tree<T>::end(Iterator it){
    return !it.bfs_q.empty();
}



///DETERMING OBJECTS
template class Tree<int>;
template class Tree<long>;
template class Tree<Pair<long>>;
template class Tree<Pair<int>>;

