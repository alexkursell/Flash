import random
import sys
from pprint import pprint


class RandomMaze(object):
    def __init__(self, levels=1, height=10, width=10):
        self.levels = levels
        self.height = height
        self.width = width
        self.asciimaze = ""
        self.asciimazes = []
        
        self.generate_maze()
        self.blockify('w', 's', 'u', 'd', 'b', 'f')

    def generate_maze(self):
        #Uses iterative depth-first search, using a stack, to generate a random maze
        #Iterative, not recursive, because recursion causes a stack overflow with large mazes (or hits recursionlimit)

        a = [[[[] for z in range(self.width)] for y in range(self.height)] for x in range(self.levels)]
        dirs = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
        stack = [(self.levels - 1, self.height - 1, self.width - 1, 0, 0, 0)]

        while stack:
            x, y, z, oldxdir, oldydir, oldzdir = stack.pop()

            if x < 0 or x >= len(a):
                continue
            if y < 0 or y >= len(a[0]):
                continue
            if z < 0 or z >= len(a[0][0]):
                continue
            if a[x][y][z] != []:
                continue

            a[x][y][z].append((oldxdir, oldydir, oldzdir))

            randdirs = random.sample(dirs, len(dirs))
            while randdirs:
                (xdir, ydir, zdir) = randdirs.pop()

                #Greatly prefer connections that do not cross levels.
                if xdir == 0 and random.random() > 0.1: 
                    randdirs.insert(0, (xdir, ydir, zdir))
                    continue

                
                newx, newy, newz = x + xdir, y + ydir, z + zdir
                stack.append((newx, newy, newz, xdir * -1, ydir * -1, zdir * -1))

        self.raw_maze = a
                
    def add_tuple(self, t1, t2):
        return tuple([t1[x] + t2[x] for x in range(len(t1))])

    def blockify(self, wallchr, spacechr, upchr, downchr, bothchr, flagchr):
        asciimaze = [[[wallchr for z in range(self.width * 2 + 1)]
                      for y in range(self.height * 2 + 1)]
                     for x in range(self.levels)]
        a = self.raw_maze

        #A little pre-processing to ensure that every "staircase" is two-way
        for x in range(len(a)):
            for y in range(len(a[0])):
                for z in range(len(a[0][0])):
                    if (-1, 0, 0) in a[x][y][z]:
                        a[x - 1][y][z].append((1, 0, 0))
                    if (1, 0, 0) in a[x][y][z]:
                        a[x + 1][y][z].append((-1, 0, 0))

        
        for x in range(len(a)):
            for y in range(len(a[0])):
                for z in range(len(a[0][0])):
                    #Cell has a different character depending on whether or not
                    #it contains a "staircase", and what direction the stairs lead
                    if (1, 0, 0) in a[x][y][z] and (-1, 0, 0) in a[x][y][z]:
                        asciimaze[x][y * 2 + 1][z * 2 + 1] = bothchr
                    elif (-1, 0, 0) in a[x][y][z]:
                        asciimaze[x][y * 2 + 1][z * 2 + 1] = upchr
                    elif (1, 0, 0) in a[x][y][z]:
                        asciimaze[x][y * 2 + 1][z * 2 + 1] = downchr
                    else:
                        asciimaze[x][y * 2 + 1][z * 2 + 1] = spacechr

                    #'Tunnel' to connected adjacent cells.
                    for d in a[x][y][z]:
                        if d[0] != 0: 
                            continue
                        t = self.add_tuple((x, y * 2 + 1, z * 2 + 1), d)
                        asciimaze[t[0]][t[1]][t[2]] = spacechr


        self.asciimaze = ""
        self.asciimazes = []
        for x in asciimaze:
            self.asciimaze += "\n"
            self.asciimazes.append([])
            for y in x:
                self.asciimazes[-1].append(y)
                self.asciimaze += "".join(y) + "\n"
        
        #The bottom right corner on the last level is the "goal" block.
        self.asciimazes[-1][-2][-2] = flagchr
        
        return self.asciimaze
                        
                        
                        
                        
if __name__ == "__main__":
    maze = RandomMaze(2, 4, 4)
    print(maze.blockify("█", " ", "↑", "↓", "↕"))
    #pprint(maze.asciimazes)
    #print()







'''
def dfs(x, y):
    if x < 0 or x >= len(a):
        return False
    if y < 0 or y >= len(a[0]):
        return False
    if a[x][y] != []:
        return False
    a[x][y].append("T")

    for (xdir, ydir) in sample(dirs, len(dirs)):
        r = dfs(x + xdir, y + ydir)
        if r:
            a[x][y].append((xdir, ydir))
    return True'''
                



