#ifndef _TREE_H_

#define _TREE_H_

#include <string>
#include<cstdio>
#include<cstdlib>
#include<cstring>
#include<cstdarg>
#include <iostream>
#include <fstream>

extern char *yytext;
extern int yycol, yyrow;

using namespace std;

class TreeNode {
public:
    string content = "";
    string name = "";
    int row = 0;
    int col = 0;
    TreeNode *first_child;
    TreeNode *next_sibling;
    TreeNode()=default;
    TreeNode(string name);
    TreeNode(string name, string content);
    TreeNode(string name, int num, ...);
    void write_json(string path);
private:
    void traverse(TreeNode *node, ofstream &outfile);
};



#endif
