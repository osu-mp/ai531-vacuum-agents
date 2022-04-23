#!/us#!/usr/bin/python3

# AI 531 - Project 2 - 15 Puzzle
# Wadood Alam
# Joe Nguyen
# Matthew Pacey

import copy
import csv
import random
import time
import unittest

from queue import PriorityQueue
"""
TODO: Define classes/tests
Heuristic: City Block
Heuristic: MY: Any other heuristic (>= CB) that you can come up with that performs better in terms of the number of nodes searched by one or both of the algorithms. This heuristic may or may not be admissible.

Helpers:
scramble(goal, m): given a valid board, scramble by m moves (watch out for moves that cancel each other out, e.g. up followed by down)
timer: time how long a function takes
correctCount: return how many numbers are in their correct cell
distanceFromEmpty: return 

Searches:
generic:    count number of nodes searched? 
            set some max node threshold?
            set some max time threshold?
aStar:
RBFS

Min Heap walkthrough: https://www.geeksforgeeks.org/min-heap-in-python/
A* algo 

"""

"""
Assignment Description
------------------------------------------
In this assignment you will implement and compare A* and RBFS, and experiment with heuristics for 15-puzzle (8-puzzle generalized to 4 X 4 board). Fix the goal configuration to be the one on the right. The problem is to take any initial configuration of the puzzle to the goal configuration with a sequence of moves in the smallest number of steps. It turns out that only half of the problems are solvable for any goal in this domain. For example, the following problem is solvable.

1  5  9  13      1  2  3  4
2  6  10 14  =>  5  6  7  8
3  7  11 15      9  10 11 12 
4  8  12         13 14 15 
Implement and experiment with the following heuristic functions.

CB: City block distance

MY: Any other heuristic (>= CB) that you can come up with that performs better in terms of the number of nodes searched by one or both of the algorithms. This heuristic may or may not be admissible.

To study how the amount of search varies with the problem difficulty, we will generate random solvable problems by perturbing the goal state with a random sequence of moves. Define Scramble(Goal, m) to be the distribution of problems generated by applying a random m-move sequence to the goal state.  Make sure that the successive moves in the random sequence are not reversals of each other (eg. Right followed by Left).

  For m= 10, 20, 30, 40, 50 do  
    For n=10 random problems p generated by Scramble(m) 
       For the two algorithms A
	  For each heuristic function h, 
            Solve p using A and h 
	    Record the length of the solution found, the number of nodes 
	         searched, and the total CPU time spent on evaluating
                 the heuristic and on solving the whole problem. 
For each m, plot the average time consumed, nodes searched, and the optimal solution lengths for the 2 algorithms and the 2 heuristics. You might find that your algorithm is taking too long for some inputs and heuristics. Bound the time and/or the number of nodes searched to a maximum and report what fraction of the problems are solved in that bound. Report the other statistics on the solved problems.
"""

emptySquare = '_'
puzzleSize = 4              # number of rows and cols for puzzle (4 means 4x4 grid with 15 numbers and one emtpy cell)
collectData = False         # set to True to generate test data (long runtime)
maxNodes = 1000             # TODO tune to a sensible value
csvFilename = 'data.csv'    # where test runtimes are written

class Puzzle:
    def __init__(self):
        self.puzzleSize = puzzleSize
        self.puzzle = self.getSolvedPuzzle()

    def graphPuzzle(self):
        """

        :return:
        """
        '''
        16 nodes: e.g. 1 connected to 2 and 5, 
        
        Use heap: 
        '''
        pass

    def getSolvedPuzzle(self):
        """
        Build and return an ordered grid of puzzleSize x puzzleSize (last cell is empty)
        For a 4x4 grid, it should look like:
        [1,   2,  3,  4],
        [5,   6,  7,  8],
        [9,  10, 11, 12],
        [13, 14, 15, emptySquare]
        :return:
        """
        puzzle = []
        for row in range(puzzleSize):
            line = []
            for col in range(puzzleSize):
                line.append(row * puzzleSize + col + 1)         # add 1 to start tiles at 1 instead of 0
            puzzle.append(line)

        # set the last sqaure to blank
        puzzle[puzzleSize - 1][puzzleSize - 1] = emptySquare
        return puzzle

    def isPuzzleSolved(self, puzzle=None):
        if not puzzle:                          # allow caller to pass in puzzle config
            puzzle = self.puzzle                # use class member if not supplied

        return puzzle == self.getSolvedPuzzle()

    def scramblePuzzle(self, m):
        """
        Scramble the current puzzle by moving m random tiles
        :param m: Number of moves to scramble puzzle
        :return: Nothing (self.puzzle is now scrambled)
        """
        lastMoved = None
        for i in range(m):
            # get neighbors of empty cell
            neighbors = self.getNeighbors(emptySquare)

            # pick a random number from those
            next = random.choice(neighbors)

            # as long as it is not 'last' move it
            while next == lastMoved:
                next = random.choice(neighbors)

            self.moveToEmptyCell(next)
            print("Scramble: moved %d to empty cell" % next)
            lastMoved = next

        # return a copy for data collection (allows to use same scrambled puzzle for different configs)
        return self.puzzle.copy()

    def print(self, puzzle=None):
        """
        Print the current configuration
        :return:
        """
        if not puzzle:                          # allow caller to pass in puzzle config
            puzzle = self.puzzle                # use class member if not supplied

        str = ""
        for row in puzzle:
            for col in row:
                if col == emptySquare:
                    str += "   "
                else:
                    str += "%2d " % col
            str += "\n"
        print(str)

    def getPosition(self, target, puzzle=None):
        """
        Return the row and col of the target number (or empty cell)
        :param target:
        :return:
        """
        if not puzzle:                          # allow caller to pass in puzzle config
            puzzle = self.puzzle                # use class member if not supplied

        # TODO does using modulo or caching significantly help?
        for row in range(puzzleSize):
            for col in range(puzzleSize):
                if puzzle[row][col] == target:
                    return(row, col)

    def getEmptyPosition(self, puzzle=None):
        """
        Return the row and col where the empty square is
        :return:
        """
        if not puzzle:                          # allow caller to pass in puzzle config
            puzzle = self.puzzle                # use class member if not supplied

        return self.getPosition(emptySquare, puzzle)

    def getNeighbors(self, target, puzzle=None):
        """
        Return neighbors of the given target (numbers that it can swap with)
        :param target:
        :return:
        """
        if not puzzle:                          # allow caller to pass in puzzle config
            puzzle = self.puzzle                # use class member if not supplied

        row, col = self.getPosition(target, puzzle)

        neighbors = []
        # up
        if row > 0:
            neighbors.append(puzzle[row - 1][col])
        # left
        if col > 0:
            neighbors.append(puzzle[row][col - 1])
        # right
        if col < puzzleSize - 1:
            neighbors.append(puzzle[row][col + 1])
        # down
        if row < puzzleSize - 1:
            neighbors.append(puzzle[row + 1][col])

        return neighbors

    def moveToEmptyCell(self, target, puzzle=None):
        """
        Move the given number into the empty cell
        :param target:
        :return: True if moved, Exception if blocked
        """
        if not puzzle:                          # allow caller to pass in puzzle config
            puzzle = self.puzzle                # use class member if not supplied

        neighbors = self.getNeighbors(target, puzzle)
        if emptySquare not in neighbors:
            raise Exception("Target number %d is not adjacent to empty cell, cannot move" % target)

        # if they are neighbors, swap the positions
        tarRow, tarCol = self.getPosition(target, puzzle)       # position of target number that is moving
        empRow, empCol = self.getEmptyPosition(puzzle)        # position of empty cell

        puzzle[tarRow][tarCol] = emptySquare
        puzzle[empRow][empCol] = target

        return True

    def cityBlock(self):
        """
        City block heuristic: estimate number of cells
        :return:
        """
        print('This is the cityBlock heuristic')
        return 8
        # raise Exception('TODO: Joe')

    def myHeuristic(self):
        """
        TBD heuristic defined by us
        :return:
        """
        print('This is my heuristic')
        return 9
        # raise Exception('TODO: Joe')

    def aStar(self, whichHeuristic, maxNodes=1000):
        """
        A* search
        :return: Number of nodes checked
        """
        estimate = whichHeuristic()
        print('astar search with %s (estimate %d)' % (whichHeuristic.__name__, estimate))
        time.sleep(1)
        #raise Exception('TODO: Wadood & Joe')
        nodesChecked = 10
        return nodesChecked

    def rbfs(self, whichHeuristic, maxNodes=1000):
        """
        Recursive best first search
        :return: Number of nodes checked
        """
        (solution, fValue) = self.rbfsMain(self.puzzle, float('inf'), whichHeuristic, 0)
        return solution

    def rbfsMain(self, node, fLimit, whichHeuristic, nodeCount):
        """

        :param puzzle:
        :param node:
        :param fLimit:
        :param whichHeuristic:
        :return:
        """
        # see page 93 in book
        if self.isPuzzleSolved(node):
            #raise Exception('solved')
            return node, -1

        successorNodes = self.generateNodes(node)
        if not successorNodes:
            return (False, float('inf'))

        q = PriorityQueue()
        for successorNode in successorNodes:
            estimate = max(nodeCount + whichHeuristic(successorNode), nodeCount)
            q.put((estimate, successorNode))

        while True:
            (bestF, bestNode) = q.get()
            if bestF > fLimit:
                return False, bestF

            (altF, altNode) = q.get()
            nextF = min(fLimit, altF)
            nodeCount += len(successorNodes)
            result, bestF = self.rbfsMain(bestNode, nextF, whichHeuristic, nodeCount)
            if result:
                return True, bestF
            a = 1
        '''
        
        for successor in sucessors:
            sf = max(sp - cost + whichHeuristic(s), node.f))

        while True:
            best = successor node with lowest f-value
            if best.f > fLimit:
                return (False, best.f)
            alternative = second lowest successor node
            result, best.f = self.rbfsMain(puzzle, best, min(fLimit, alternative))
            if result != False:
                return (result, best.f)

        raise Exception('TODO: Matthew')

        estimate = whichHeuristic()
        print('rbfs search with %s (estimate %d)' % (whichHeuristic.__name__, estimate))
        time.sleep(2)
        #raise Exception('TODO: Matthew')
        nodesChecked = 20
        return nodesChecked
        '''

    def generateNodes(self, puzzle=None):
        """
        Using the current configuration, generate 1 node for each direction the empty square can move
        This will generate 2-4 nodes
        :param self:
        :return:
        """
        if not puzzle:                          # allow caller to pass in puzzle config
            puzzle = self.puzzle                # use class member if not supplied

        nodes = []
        currPuzzle = puzzle.copy()
        neighbors = self.getNeighbors(emptySquare, puzzle)
        for neighbor in neighbors:
            node = copy.deepcopy(currPuzzle)
            self.moveToEmptyCell(neighbor, node)
            nodes.append(node)

        return nodes

class Successor():
    def __init__(self, node, value):
        self.node = node
        self.value = value

class TestPuzzle(unittest.TestCase):

    def test_scramble(self):
        puzzle = Puzzle()
        solved = puzzle.getSolvedPuzzle()
        puzzle.scramblePuzzle(10)
        self.assertNotEqual(solved, puzzle.puzzle)
        puzzle.print()

    def test_getPosition(self):
        """
        Tests for getPosition
        :return:
        """
        puzzle = Puzzle()
        target = 1
        exp = (0, 0)
        self.assertEqual(exp, puzzle.getPosition(target))

    def test_getEmptyPosition(self):
        """
        Test the get empty position function.
        For a solved puzzle, it should be in the final cell (row = puzzleSize - 1, col = puzzleSize - 1)
        FOr a 4x4 grid, this will be in position 3,3
        :return:
        """
        puzzle = Puzzle()
        row, col = puzzle.getEmptyPosition()
        self.assertEqual(3, row)
        self.assertEqual(3, col)

    def test_getNeighbors(self):
        """
        Test the getNeighbors function in various positions.
        Use the solved puzzle (below) as a reference
        1  2  3  4
        5  6  7  8
        9  10 11 12
        13 14 15 _
        :return:
        """
        puzzle = Puzzle()

        # top left (only 2 neighbors)
        target = 1
        exp = [2, 5]
        self.assertEqual(exp, puzzle.getNeighbors(target))

        # top right (only 2 neighbors)
        target = 4
        exp = [3, 8]
        self.assertEqual(exp, puzzle.getNeighbors(target))

        # middle number (4 neighbors)
        target = 7
        exp = [3, 6, 8, 11]
        self.assertEqual(exp, puzzle.getNeighbors(target))

        # bottom left (2 neighbors)
        target = 13
        exp = [9, 14]
        self.assertEqual(exp, puzzle.getNeighbors(target))

        # middle bottom (3 neighbors)
        target = 14
        exp = [10, 13, 15]
        self.assertEqual(exp, puzzle.getNeighbors(target))

        # bottom left (2 neighbors)
        target = emptySquare
        exp = [12, 15]
        self.assertEqual(exp, puzzle.getNeighbors(target))

    def test_moveToEmptyCell(self):
        """
        Verify the move command works as expected. Start with solved puzzle:
        1  2  3  4
        5  6  7  8
        9  10 11 12
        13 14 15 _
        :return:
        """
        puzzle = Puzzle()

        # try to move number 1 (it is not adjacent to empty cell so exception expected)
        self.assertRaises(Exception, puzzle.moveToEmptyCell, 1)

        # move 12 to empty cell (adjacent so valid)
        puzzle.moveToEmptyCell(12)
        """ Current configuration
        1  2  3  4
        5  6  7  8
        9  10 11 _
        13 14 15 12        
        """

        puzzle.moveToEmptyCell(11)
        """ Current configuration
        1  2  3  4
        5  6  7  8
        9  10 _  11
        13 14 15 12        
        """

        puzzle.moveToEmptyCell(7)
        """ Current configuration
        1  2  3  4
        5  6  _  8
        9  10 7  11
        13 14 15 12        
        """
        expected = [
            [1,   2, 3,           4],
            [5,   6, emptySquare, 8],
            [9,  10, 7,          11],
            [13, 14, 15,         12]
        ]
        self.assertEqual(puzzle.puzzle, expected)

    def runTest(self, puzzleObj, searchFunc, heuristic):
        """
        Run the specified search function using given heuristic and return runtime in seconds
        :param puzzle:
        :param searchFunc:
        :param heuristic:
        :return:
        """
        start = time.time()                             # get start time
        nodesChecked = searchFunc(heuristic)            # run the search function with selected heuristic
        end = time.time()                               # record runtime

        return (nodesChecked, end - start)              # return number of nodes checked and runtime

    def test_data_collection(self):
        """
        Try all combinations of searches and collect performance data into a csv
        :return:
        """
        if not collectData:
            self.skipTest("Data collection skipped")

        # TODO save to csv
        csvFH = open(csvFilename, 'w', newline='')
        writer = csv.writer(csvFH)
        writer.writerow(['m', 'puzzleNum', 'searchFunc', 'heuristic', 'nodesChecked', 'runTime (seconds)'])

        # collect data into run data and write it later
        runData = {}
        for algo in ['astar', 'rbfs']:
            runData[algo] = {}
            for heuristic in ['cityBlock', 'myHeuristic']:
                runData[algo][heuristic] = {}

        puzzle = Puzzle()
        for m in [10, 20, 30, 40, 50]:                      # run for increasing number of moves from solved puzzle

            runData['astar']['cityBlock'][m] = []
            runData['astar']['myHeuristic'][m] = []
            runData['rbfs']['cityBlock'][m] = []
            runData['rbfs']['myHeuristic'][m] = []

            for n in range(10):                             # run 10 trials at each m
                base = Puzzle()
                basePuzzle = base.scramblePuzzle(m)         # ensure all 4 configurations use the same scrambled puzzle
                print('Puzzle Number %d' % n)
                print(base.print())

                # astar with city block heuristic
                test = Puzzle()
                test.puzzle = basePuzzle
                (nodesChecked, runTime) = self.runTest(test, puzzle.aStar, puzzle.cityBlock)
                runData['astar']['cityBlock'][m].append([nodesChecked, runTime])

                # astar with my heuristic
                test = Puzzle()
                test.puzzle = basePuzzle
                (nodesChecked, runTime) = self.runTest(test, puzzle.aStar, puzzle.myHeuristic)
                runData['astar']['myHeuristic'][m].append([nodesChecked, runTime])

                # rbfs with city block heuristic
                test = Puzzle()
                test.puzzle = basePuzzle
                (nodesChecked, runTime) = self.runTest(basePuzzle, puzzle.rbfs, puzzle.cityBlock)
                runData['rbfs']['cityBlock'][m].append([nodesChecked, runTime])

                # rbfs with my heuristic
                test = Puzzle()
                test.puzzle = basePuzzle
                (nodesChecked, runTime) = self.runTest(basePuzzle, puzzle.rbfs, puzzle.myHeuristic)
                runData['rbfs']['myHeuristic'][m].append([nodesChecked, runTime])

        # now that all data has been collected, write it grouped by algo/heuristic
        for algo in runData:
            for heuristic in runData[algo]:
                for mValue in runData[algo][heuristic]:
                    for puzzleNum, trial in enumerate(runData[algo][heuristic][m]):
                        (nodesChecked, runTime) = trial
                        writer.writerow([mValue, puzzleNum, algo, heuristic, nodesChecked, runTime])
        print('Data collection complete, results written to: %s' % csvFilename)

    def test_generateNodes(self):
        """
        Test for generateNodes. Show nodes generated for branch checking
        :return:
        """
        puzzle = Puzzle()
        # puzzle is solved, so empty tile is in bottom right. There are two possible nodes
        # from here: empty can move up or left (verify both are created)
        nodes = puzzle.generateNodes()
        expectedNodeUp = [
            [1,   2, 3,   4],
            [5,   6, 7,   8],
            [9,  10, 11, emptySquare],
            [13, 14, 15, 12]
        ]
        expectedNodeLeft = [
            [1,   2, 3,   4],
            [5,   6, 7,   8],
            [9,  10, 11, 12],
            [13, 14, emptySquare, 15]
        ]
        self.assertEqual(nodes, [expectedNodeUp, expectedNodeLeft])

    def test_rbfs(self):
        """
        Functional tests for rbfs search algo
        :return:
        """
        puzzle = Puzzle()
        solvedPuzzle = puzzle.getSolvedPuzzle()
        result = puzzle.rbfs(puzzle.cityBlock)
        self.assertTrue(result != None)

        puzzle.moveToEmptyCell(12)
        result = puzzle.rbfs(puzzle.cityBlock)
        self.assertTrue(puzzle.isPuzzleSolved(result))


if __name__ == '__main__':
    unittest.main()
