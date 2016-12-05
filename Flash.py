from maze_generator_3D import RandomMaze
from collections import namedtuple
import tkinter as tk

class MainWindow(tk.Frame):
    def __init__(self, master):
        super().__init__()

        self.master = master
        self.master.resizable(0, 0)
        self.master.wm_title("Flash!")

        self.FRAMES_PER_SECOND = 40
        
        #Block size must be even.
        self.BLOCK_SIZE = 14

        self.isLooping = False

        self.keysPressed = {"Left" :False,
                            "Right":False,
                            "Up"   :False,
                            "Down" :False,
                            "w"    :False,
                            "s"    :False}

        
        #Using a namedtuple for more understandable reference to various block attributes
        self.Block = namedtuple("Block", ["x1", "y1", "x2", "y2", "type"])


        self.pack(fill=tk.BOTH, expand=1)
        self.create_widgets()
        print("WIDGETS LOADED")
        self.event_loop()
        print("EVENT LOOP STARTED")


    def create_widgets(self):
        #Create panel for specifying new maze dimensions.
        self.setupFrame = tk.Frame(self)

        self.levelLabel = tk.Label(self.setupFrame, text="# Levels:")
        self.levelLabel.pack(side="left")
        self.levelEntry = tk.Entry(self.setupFrame, width=2)
        self.levelEntry.pack(side="left")

        self.widthLabel = tk.Label(self.setupFrame, text="Width:")
        self.widthLabel.pack(side="left")
        self.widthEntry = tk.Entry(self.setupFrame, width=2)
        self.widthEntry.pack(side="left")

        self.heightLabel = tk.Label(self.setupFrame, text="Height:")
        self.heightLabel.pack(side="left")
        self.heightEntry = tk.Entry(self.setupFrame, width=2)
        self.heightEntry.pack(side="left")

        self.generateButton = tk.Button(self.setupFrame, text="Generate!")
        self.generateButton.bind("<Button-1>", self.new_maze)
        self.generateButton.pack(side="left")

        self.setupFrame.pack(anchor="center")

        #Create canvas that displays the game area.
        self.w = tk.Canvas(self)
        self.w.pack()

        #Bind all canvas keypresses and keyreleases to proper methods
        self.w.bind_all("<KeyPress>", self.on_key_press)
        self.w.bind_all("<KeyRelease>", self.on_key_release)

        #Create label to show messages
        self.statusLabel = tk.Label(self, 
            text="Specify the maze dimensions to start!",
            borderwidth=0,
            anchor="w",
            justify='left')
        self.statusLabel.pack(fill="both", side="left")

        #Create label to show the current level.
        self.levelLabel = tk.Label(self,
            anchor="e",
            borderwidth=0)
        self.levelLabel.pack(fill="both", side="right")

    def display_text(self, text):
        self.statusLabel.config(text=text)

    def new_maze(self, event):
        try: #Do nothing if user input is screwy. Restricted to certain bounds.
            levels = max(1, min(20, int(self.levelEntry.get())))
            height = max(2, min(25, int(self.heightEntry.get())))
            width = max(2, min(40, int(self.widthEntry.get())))
        except:
            return
        
        #Display loading message
        self.display_text("Loading new level...")
        
        #Clear input boxes
        self.levelEntry.delete(0, "end")
        self.heightEntry.delete(0, "end")
        self.widthEntry.delete(0, "end")

        #Reset canvas.
        self.w.delete("all")
        
        #Create player rectangle, start in top right cell.
        self.r = self.w.create_rectangle(self.BLOCK_SIZE,
           self.BLOCK_SIZE,
           self.BLOCK_SIZE * 2,
           self.BLOCK_SIZE * 2,
           fill="green")
        
        #Load new maze, load first level, begin event loop
        self.load_maze(levels, width, height)
        self.load_level(0)
        self.isLooping = True

        #Set focus on canvas
        self.w.focus_set()

        #Display goal message.
        self.display_text("Reach the lowest bottom right corner!")

    def load_maze(self, levels, width, height):
        self.maze = RandomMaze(levels=levels, height=width, width=height)

    def load_level(self, level):
        self.level = level
        
        self.w.config(height=len(self.maze.asciimazes[level][0]) * self.BLOCK_SIZE,
            width=len(self.maze.asciimazes[level]) * self.BLOCK_SIZE)

        mazeGrid = self.maze.asciimazes
        self.levelLabel.config(text="Level %i/%i" % (level + 1, len(mazeGrid)))

        for x in range(len(mazeGrid[level])):
            for y in range(len(mazeGrid[level][0])):
                #The bottom right corner on the last level is the "goal" block.
                if mazeGrid[level][x][y] == 'f':
                    color = "orange"
                elif mazeGrid[level][x][y] == 'w':#Wall
                    color = "black"
                elif mazeGrid[level][x][y] == 'u':#Up
                    color = "red"
                elif mazeGrid[level][x][y] == 'd':#Down
                    color = "blue"
                elif mazeGrid[level][x][y] == 'b':#Both
                    color = "purple"
                else:
                    continue #Space

                block = self.lookup_cell(x, y)

                #If the coordinates of the block match exactly with those of the player
                #rect, we have just used it and it should be stippled.
                if block[:4] == tuple(self.w.coords(self.r)):
                    stipple="gray75"
                else:
                    stipple=""
                
                self.w.create_rectangle(block.x1, block.y1, block.x2, block.y2, fill=color, stipple=stipple)


    def event_loop(self):
        if self.isLooping: #Flag to allow pausing
            for key in self.keysPressed.keys():
                if self.keysPressed[key]:
                    self.move_rect(key)

        self.after(1000 // self.FRAMES_PER_SECOND, self.event_loop)

    def on_key_press(self, event):
        self.keysPressed[event.keysym] = True

    def on_key_release(self, event):
        self.keysPressed[event.keysym] = False

    def move_rect(self, key):
        #Move a half-block width every frame.
        #This is the reason BLOCK_SIZE must be a multiple of 2.
        dist = self.BLOCK_SIZE / 2
        
        if key == "Left":
            self.move(self.r, dist * -1, 0, 0)
        elif key == "Right":
            self.move(self.r, dist, 0, 0)
        elif key == "Up":
            self.move(self.r, 0, dist * -1, 0)
        elif key == "Down":
            self.move(self.r, 0, dist, 0)
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


    def move(self, itemId, xmov, ymov, zmov):
        current = self.w.coords(itemId)

        xsign = xmov // abs(xmov) if xmov != 0 else 0
        ysign = ymov // abs(ymov) if ymov != 0 else 0

        # 'P' for player.
        current = self.Block(current[0] + xmov,
            current[1] + ymov,
            current[2] + xmov,
            current[3] + ymov,
            'p')

        #Find what cells occupied by the current position are also
        #occupied by a wall
        nearWalls = self.intersected_blocks(current)
        
        for block in nearWalls:
            #For each wall, step back the movement until there is no collision
            if block.type == 'w':
                while self.is_collision(current, block):
                    current = self.Block(current.x1 - xsign,
                        current.y1 - ysign,
                        current.x2 - xsign,
                        current.y2 - ysign,
                        'p')

            
            #For each movement block (up, down, or both), check if
            #movement in that direction was requested. If it was,
            #load the correct level and set the new position to be exactly
            #equal to the movement block.
            elif block.type in 'udb' and zmov != 0:
                if zmov == 1 and block.type == 'u':
                    continue
                elif zmov == -1 and block.type == 'd':
                    continue
                
                current = block

                self.w.delete("all")
                self.r = self.w.create_rectangle(block.x1,
                   block.y1,
                   block.x2,
                   block.y2,
                   fill="green")

                self.load_level(self.level + zmov)

            #If there is an intersection with a flag block, that means we've won!
            #Gray screen, pause event_loop, and display win message
            elif block.type == 'f':
                self.w.create_rectangle(0, 0, 
                    current.x2 + self.BLOCK_SIZE * 3, 
                    current.y2 + self.BLOCK_SIZE * 3, 
                    stipple="gray25", 
                    fill="gray")

                current = block
                self.isLooping = False
                self.display_text("Winner!")

        self.w.coords(itemId, (current.x1, current.y1, current.x2, current.y2))


if __name__ == "__main__":
    root = tk.Tk()
    app = MainWindow(root)
    app.mainloop()