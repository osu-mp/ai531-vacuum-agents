#!/us#!/usr/bin/python3

# AI 531 - Project 2 - 15 Puzzle
# Wadood Alam
# Joe Nguyen
# Matthew Pacey

import csv
import random
import time
import unittest

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
debug = False               # prints debug messages when enabled

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

    def isPuzzleSolved(self):
        return self.puzzle == self.getSolvedPuzzle()

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
            if debug:
                print("Scramble: moved %d to empty cell" % next)
            lastMoved = next

        # return a copy for data collection (allows to use same scrambled puzzle for different configs)
        return self.puzzle.copy()

    def print(self):
        """
        Print the current configuration
        :return:
        """
        str = ""
        for row in self.puzzle:
            for col in row:
                if col == emptySquare:
                    str += "   "
                else:
                    str += "%2d " % col
            str += "\n"
        print(str)



    def getPosition(self, target):
        """
        Return the row and col of the target number (or empty cell)
        :param target:
        :return:
        """
        # TODO does using modulo or caching significantly help?
        for row in range(puzzleSize):
            for col in range(puzzleSize):
                if self.puzzle[row][col] == target:
                    return(row, col)


    def getEmptyPosition(self):
        """
        Return the row and col where the empty square is
        :return:
        """
        return self.getPosition(emptySquare)

    def getNeighbors(self, target):
        """
        Return neighbors of the given target (numbers that it can swap with)
        :param target:
        :return:
        """
        row, col = self.getPosition(target)

        neighbors = []
        # up
        if row > 0:
            neighbors.append(self.puzzle[row - 1][col])
        # left
        if col > 0:
            neighbors.append(self.puzzle[row][col - 1])
        # right
        if col < puzzleSize - 1:
            neighbors.append(self.puzzle[row][col + 1])
        # down
        if row < puzzleSize - 1:
            neighbors.append(self.puzzle[row + 1][col])

        return neighbors

    def moveToEmptyCell(self, target):
        """
        Move the given number into the empty cell
        :param target:
        :return: True if moved, Exception if blocked
        """
        neighbors = self.getNeighbors(target)
        if emptySquare not in neighbors:
            raise Exception("Target number %d is not adjacent to empty cell, cannot move")

        # if they are neighbors, swap the positions
        tarRow, tarCol = self.getPosition(target)       # position of target number that is moving
        empRow, empCol = self.getEmptyPosition()        # position of empty cell

        self.puzzle[tarRow][tarCol] = emptySquare
        self.puzzle[empRow][empCol] = target

        return True

    def cityBlock(self):
        """
        City block heuristic: estimate number of moves for each tile to intended location
        This is admissible since it never over-estimates the number of moves
        :return:
        """
        # for each tile, count the number of moves to its intended position (assume no other tiles)
        sum = 0

        for row in range(puzzleSize):
            for col in range(puzzleSize):
                # expected tile position (+1 because arrays start at 0, tiles start at 1)
                expectedTile = row * puzzleSize + col + 1

                # the last spot in the board is reserved for empty space, ignore for this heuristic
                if expectedTile == (puzzleSize * puzzleSize):
                    continue

                # get location of expected tile and calculate distance (absolute in case it moves up/left)
                actRow, actCol = self.getPosition(expectedTile)
                dist = abs(actRow - row) + abs(actCol - col)
                if debug:
                    print(f'Expected at {row},{col} is Tile {expectedTile}; actually at {actRow},{actCol} (dist={dist})')

                sum += dist

        return sum

    def myHeuristic(self):
        """
        Heuristic defined by us
        Use the city block estimate plus the distance to the empty square
        This is not admissible since it may over-estimate the number of moves
        -i.e. if the give tile is one move away from its intended location and the emtpy square
        is there, it only needs to move once (but this algo returns 2 for that tile)
        :return:
        """
        sum = 0
        (emptyRow, emptyCol) = self.getEmptyPosition()

        for row in range(puzzleSize):
            for col in range(puzzleSize):
                # expected tile position (+1 because arrays start at 0, tiles start at 1)
                expectedTile = row * puzzleSize + col + 1

                # the last spot in the board is reserved for empty space, ignore for this heuristic
                if expectedTile == (puzzleSize * puzzleSize):
                    continue

                # get location of expected tile and calculate distance (absolute in case it moves up/left)
                actRow, actCol = self.getPosition(expectedTile)
                dist = abs(actRow - row) + abs(actCol - col)
                if debug:
                    print(f'Expected at {row},{col} is Tile {expectedTile}; actually at {actRow},{actCol} (dist={dist})')

                # if at correct spot, do not consider moving empty tile
                if dist == 0:
                    continue

                # otherwise add distance to empty tile (this makes the algo not admissible)
                emptyDist = abs(actRow - emptyRow) + abs(actCol - emptyCol)
                if debug:
                    print('myHeuristic moves from emtpy: %d' % emptyDist)
                sum += dist + emptyDist

        return sum

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
        estimate = whichHeuristic()
        print('rbfs search with %s (estimate %d)' % (whichHeuristic.__name__, estimate))
        time.sleep(2)
        #raise Exception('TODO: Matthew')
        nodesChecked = 20
        return nodesChecked


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

    def test_cityBlock(self):
        """
        Unit tests for city block heuristic
        :return:
        """
        puzzle = Puzzle()

        # base case: solved puzzle, city block should return 0
        self.assertEqual(0, puzzle.cityBlock())

        scrambled = [
            [4,   1, 3,           2],
            [5,   6, emptySquare, 8],
            [10,  9, 7,          11],
            [15, 14, 13,         12]
        ]

        puzzle.puzzle = scrambled

        # using above puzzle, expected city block is (tiles 1 through 15 distances added):
        # e.g. tile 1 is 1 spot away, tile 2 is 2, tile 3 is where it belongs, etc
        expected = 1 + 2 + 0 + 3 + 0 + 0 + 1 + 0 + 1 + 1 + 1 + 1 + 2 + 0 + 2
        # tiles    1   2   3   4   5   6   7   8   9  10  11  12  13  14  15
        self.assertEqual(expected, puzzle.cityBlock())

    def test_myHeuristic(self):
        """
        Unit tests for my heuristic
        :return:
        """
        puzzle = Puzzle()

        # base case: solved puzzle, city block should return 0
        self.assertEqual(0, puzzle.cityBlock())

        scrambled = [
            [4,   1, 3,           2],
            [5,   6, emptySquare, 8],
            [10,  9, 7,          11],
            [15, 14, 13,         12]
        ]

        puzzle.puzzle = scrambled

        # using above puzzle, expected my heuristic is (tiles 1 through 15 distances added):
        # e.g. tile 1 is 1 spot away from target and 2 away from emtpy,
        # tile 2 is 2 away from target and 2 from empty,
        # tile 3 is where it belongs, etc
        expected =  (1 + 2) + (2 + 2) + 0 + (3 + 3) + 0 + 0 + (1 + 1) + 0
        # tile       1         2        3    4        5   6    7        8
        expected += (1 + 2) + (1 + 3) + (1 + 2) + (1 + 3) + (2 + 2) + 0 + (2 + 4)
        #            9         10        11       12        13        14   15
        self.assertEqual(expected, puzzle.myHeuristic())

if __name__ == '__main__':
    unittest.main()
