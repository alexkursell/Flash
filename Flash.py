from maze_generator_3D import RandomMaze
from collections import namedtuple
import tkinter as tk

#maze = RandomMaze(2, 5, 5)
#print(maze.blockify("█", " ", "↑", "↓", "↕"))


class MainWindow(tk.Frame):
    def __init__(self, master):
        super().__init__()

        self.master = master
        self.master.resizable(0, 0)
        self.master.wm_title("Flash 2: Electric Bugaloo")

        self.FRAMES_PER_SECOND = 40
        self.BLOCK_SIZE = 10

        self.keysPressed = {"Left" :False,
                            "Right":False,
                            "Up"   :False,
                            "Down" :False,
                            "w"    :False,
                            "s"    :False}

        self.blocks = []
        self.Block = namedtuple("Block", ["x1", "y1", "x2", "y2", "type"])


        self.pack(fill=tk.BOTH, expand=1)
        self.create_widgets()
        print("WIDGETS LOADED")
        self.load_maze()
        print("MAZE LOADED")
        self.load_level(0)
        print("LEVEL LOADED")
        self.queue_loop()
        print("LEVEL START")


    def create_widgets(self):
        self.w = tk.Canvas(self)
        self.w.pack()

        self.w.bind_all("<KeyPress>", self.on_key_press)
        self.w.bind_all("<KeyRelease>", self.on_key_release)

        self.r = self.w.create_rectangle(self.BLOCK_SIZE,
           self.BLOCK_SIZE,
           self.BLOCK_SIZE * 2,
           self.BLOCK_SIZE * 2,
           fill="green")

    def load_maze(self):
        self.maze = RandomMaze(10, 10, 10)

    def load_level(self, level):
        self.level = level
        
        self.w.config(width=len(self.maze.asciimazes[level][0]) * self.BLOCK_SIZE,
            height = len(self.maze.asciimazes[level]) * self.BLOCK_SIZE)

        mazeGrid = self.maze.asciimazes

        for x in range(len(mazeGrid[level])):
            for y in range(len(mazeGrid[level][0])):
                if mazeGrid[level][x][y] == 's':
                    continue
                elif mazeGrid[level][x][y] == 'w':
                    color = "black"
                elif mazeGrid[level][x][y] == 'u':
                    color = "red"
                elif mazeGrid[level][x][y] == 'd':
                    color = "blue"
                elif mazeGrid[level][x][y] == 'b':
                    color = "purple"

                block = self.lookup_cell(x, y)
                self.blocks.append(block)
                self.w.create_rectangle(block.x1, block.y1, block.x2, block.y2, fill=color)


    def queue_loop(self):
        for key in self.keysPressed.keys():
            if self.keysPressed[key]:
                self.move_rect(key)

        self.after(1000 // self.FRAMES_PER_SECOND, self.queue_loop)

    def on_key_press(self, event):
        self.keysPressed[event.keysym] = True

    def on_key_release(self, event):
        self.keysPressed[event.keysym] = False

    def move_rect(self, key):
        dist = self.BLOCK_SIZE / 2
        if key == "Left":
            self.move(self.r, dist * -1, 0)
        elif key == "Right":
            self.move(self.r, dist, 0)
        elif key == "Up":
            self.move(self.r, 0, dist * -1)
        elif key == "Down":
            self.move(self.r, 0, dist)
        elif key == "w":
            self.keysPressed["w"] = False
            self.move(self.r, 0, 0, -1)
        elif key == "s":
            self.keysPressed["s"] = False
            self.move(self.r, 0, 0, 1)

    def is_collision(self, c1, c2):
        #Uses magic to determine whether two Block namedtuples
        #of the form (x1, y1, x2, y2) are overlaping.
        return c1.x1 < c2.x2 \
        and c1.x2 > c2.x1 \
        and c1.y1 < c2.y2 \
        and c1.y2 > c2.y1

    def intersected_blocks(self, cur):
        nearWalls = []
        nearWalls.append(self.lookup_cell(cur.x1 // self.BLOCK_SIZE, cur.y1 // self.BLOCK_SIZE))
        nearWalls.append(self.lookup_cell(cur.x1 // self.BLOCK_SIZE, cur.y2 // self.BLOCK_SIZE))
        nearWalls.append(self.lookup_cell(cur.x2 // self.BLOCK_SIZE, cur.y1 // self.BLOCK_SIZE))
        nearWalls.append(self.lookup_cell(cur.x2 // self.BLOCK_SIZE, cur.y2 // self.BLOCK_SIZE))
        return nearWalls



    def lookup_cell(self, x, y):
        x, y = int(x), int(y)
        return self.Block(
            x * self.BLOCK_SIZE,
            y * self.BLOCK_SIZE,
            (x + 1) * self.BLOCK_SIZE,
            (y + 1) * self.BLOCK_SIZE,
            self.maze.asciimazes[self.level][x][y])


    def move(self, itemId, xmov, ymov, zmov=0):
        current = self.w.coords(itemId)

        xsign = xmov // abs(xmov) if xmov != 0 else 0
        ysign = ymov // abs(ymov) if ymov != 0 else 0

        current = self.Block(current[0] + xmov,
            current[1] + ymov,
            current[2] + xmov,
            current[3] + ymov,
            'p')

        #Find what cells occupied by the current position are also
        #occupied by a wall
        
        nearWalls = self.intersected_blocks(current)
        
        for block in nearWalls:
            if block.type == 'w':
                #For each of these, step back the movement untill there is no collision
                while self.is_collision(current, block):
                    current = self.Block(current.x1 - xsign,
                        current.y1 - ysign,
                        current.x2 - xsign,
                        current.y2 - ysign,
                        'p')
            elif block.type in 'udb' and zmov != 0:
                if zmov == 1 and block.type == 'u':
                    continue
                elif zmov == -1 and block.type == 'd':
                    print("NO")
                    continue
                
                current = block

                self.w.delete("all")

                self.r = self.w.create_rectangle(block.x1,
                   block.y1,
                   block.x2,
                   block.y2,
                   fill="green")


                self.load_level(self.level + zmov)




        
        self.w.coords(itemId, (current.x1, current.y1, current.x2, current.y2))


if __name__ == "__main__":
    root = tk.Tk()
    app = MainWindow(root)
    app.mainloop()