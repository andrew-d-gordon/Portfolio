# Improving Find Lines Algorithms
The following algorithm I will lay out should be as reliable as, and faster than, find_max_unique_point_lines. I am 
unsure in practice if it would be viable, but improving upon the current, troublesome O(2^n) that it runs in would make
this library much more suitable for large volume input data. This algorithm, like find_max_unique_point_lines, would
rely upon the output of find_unique_lines, which is the set of unique lines that satisfy the point threshold (and 
potentially share points). find_unique_lines currently runs in about O(n*n) which does not provide the same trouble that
find_max_unique_point_lines O(2^n) does on the larger unit test files available in unit_tests. Anyways, on with the
potential algorithm.

# Finding the fewest amount of lines we can remove, such that each remaining line has no points in common with the others
Take the set of all unique lines `all_lines`, where each line in `all_lines` has reference to every point it crossed.
Now consider that each line in `all_lines` is a vertex in a graph, and an edge represents a shared point with another line.
To find the largest set of lines from `all_lines` that do not share any points, we want to:
Remove the fewest vertices in the graph, such that every remaining vertex is isolated.

After creating the adjacency matrix in `O(n+m)`, we want to build sets of every disconnected set of vertices in the graph.
This can be done with starting DFS at each untouched vertex until every possible disconnected set (island) is discovered.
[Here](https://math.stackexchange.com/questions/277045/easiest-way-to-determine-all-disconnected-sets-from-a-graph) is 
example of how this "island building" should work in practice. This version of DFS which finds each disconnected set 
should run in `O(n+m)` because each edge and node is touched once.

We want to track each "island" present in the graph and run the following algorithm on each:

**Step 1** 

Put every vertex for an island into a max heap which is prioritized by the number of edges a vertex has.

**Step 2**

Pop the top vertex, go to it's neighboring vertices and remove the edge (decrement their edge count by 1). 
Run heap sort on the heap with the updated edge counts for each vertex.

Repeat Step 2 until no vertex in the island has any edges.

**Step 3** 

Add the remaining vertices (which have no edges, and represented by line eqs) to the output set of lines.

After doing this for every island in the graph, you are left with the largest possible set of lines which have no points
in common.

If the above description was not clear, here is a (admittedly MS Paint berthed) run of the algorithm on test_9_set_9. 

![alt_text](https://github.com/andrew-d-gordon/coding-challenges/blob/main/line-set/docs/improving_find_lines_algorithm_visualizer.png?raw=true)

# Rough runtime analysis

**Step 1**

For any given island the runtime is likely O(n) assuming optimal build heap function.

Step 1 Total: `O(n)`

**Step 2**

For every vertex removed, we perform:
* an `O(m)` operation where we remove the m edges that the vertex had (also decrementing edge count for adjacent vertices by 1)
* an `O(n*logn)` heap sort where n is number of vertices remaining in the graph

Because Step 2 will be repeated until there are no more edges in the graph, this process at maximum should repeat a 
maximum of n-1 times where n is number of vertices in an island.

Step 2 Total: `O(n*nlogn) + O(n*m)`

**Step 3**

We add remaining vertices to output set. Realistically this could be n-1 where n vertices in island (e.g. only one vertex in island connected to one other, remaining connected to two).

Total: O(n)

**Total run time**
 
`O(n*nlogn) + O(n*m) + O(2n) + O(n+m)` => `O(n*nlogn) + O(n*m)` => `O(n*nlogn)`

The `O(n+m)` is the overhead of creating the graph and finding the various islands (DFS for disconnected sets).
Also, `O(n*m)` could certainly provide considerable computation time, but I feel compared to `O(n*nlogn)`, especially 
when the input is guaranteed to not be a fully connected graph (each line cannot not share all of it's points with 
another), `O(n*nlogn)` is more likely a better estimate of the computation time.

While this algorithm may not be completely optimal, should it work in practice, it would certainly be superior to the 
current O(2^n), find_max_unique_point_lines implementation.
