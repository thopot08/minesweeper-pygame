import random, pygame, sys, threading, time

pygame.init()

class Tile:
    def __init__ (self, hidden=True, bomb=False, flagged=False, bombsAround=0, colourChange=False): # colourChange is for the win/lose animation which lights up the bombs one by one
        self.hidden = hidden
        self.bomb = bomb
        self.flagged = flagged
        self.bombsAround = bombsAround
        self.colourChange = colourChange
                
# constants
TILESIZE = 30
GRIDSIZEX = 25
GRIDSIZEY = 25
TOPBARSIZE = TILESIZE*3
BOMBPERCENTAGE = 0.16
BOMBCOUNT = round(GRIDSIZEX*GRIDSIZEY*BOMBPERCENTAGE)
WIDTH = TILESIZE*GRIDSIZEX
HEIGHT = (TILESIZE*GRIDSIZEY)+TOPBARSIZE
clock = pygame.time.Clock()
font = pygame.font.Font(None,round(TILESIZE*1.8)) # this font used for numbers on the tiles
font2 = pygame.font.Font(None,round(TOPBARSIZE*0.6)) # this one used for other text like timer and win message
winmessages = ["you swept hard enough!",
                "good job",
                "mines = sweeped",
                "that was pretty fast",
                "so talented",
                "holy moly.",
                "wow, incredible!",
                "skill is unfathomable",
                "you're pretty good at this"
                ]

lossmessages = ["you didnt sweep hard enough",
               "it's all your fault",
               "you exploded",
               "why would you do this?",
               "you had a blast",
               "you touched a bomb",
               "you stepped on a mine",
               "no win for you :(",
               "so close yet so far"
               ]

# variables
lost = False
won = False
seconds = 0
flagsPlaced = 0
winMessage = random.choice(winmessages) # these 2 will re randomise in the restart function
lossMessage = random.choice(lossmessages)
rowY = 0 # this are for the colour change animation, see the pygame part before drawgame()
tellplayertostopit = False
freeStart = True
fps = 30

# colours
BLACK = (0,0,0)
WHITE = (255,255,255)
GREY = (100,100,100)
YELLOW = (255,255,180)
LIGHTGREEN = (125,255,125)
SLIGHTLYLESSLIGHTGREEN = (100,230,100)
BLUE = (0,0,230)
DARKBLUE = (0,0,100)
GREEN = (0,230,0)
RED = (255,0,0)
BROWN = (66,29,0)
CYAN = (0,255,255)
ORANGE = (255,170,43)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("minesweepa")

gameArray = [] # make array of tiles
for _ in range(GRIDSIZEY):
    row = []
    for _ in range(GRIDSIZEX):
        row.append(Tile())
    gameArray.append(row)
 
# --- Functions ---

def checkSurrounding(y,x): # function to check how many bombs surround a tile
    global gameArray
    bombcount = 0
    tilesAround = [
        [y-1,x-1],
        [y-1,x],
        [y-1,x+1],
        [y,x-1],
        [y,x+1],
        [y+1,x-1],
        [y+1,x],
        [y+1,x+1]
    ]

    for coords in tilesAround:
        if coords[0] >= 0 and coords[0] <= GRIDSIZEY-1 and coords[1] >= 0 and coords[1] <= GRIDSIZEX-1:
            if gameArray[coords[0]][coords[1]].bomb == True:
                bombcount += 1
    
    return bombcount

def drawGame(): # draws the game with pygame stuffs
    # i add topbarsize to every y coordinate here its messy but i added the topbar late so it has to be done
    global tellplayertostopit
    screen.fill(YELLOW)

    # Draw the top bar thingy
    pygame.draw.rect(screen, (90,210,90), (0,0, WIDTH,TOPBARSIZE)) # this is the background of top 
    showMessage(f"time: {seconds}", WHITE, round(WIDTH*0.05), round(TOPBARSIZE*0.3),font2)
    showMessage(f"bombs: {BOMBCOUNT}",WHITE, round(WIDTH*0.6),round(TOPBARSIZE*0.1),font2)
    showMessage(f"flags: {flagsPlaced}",WHITE,round(WIDTH*0.6),round(TOPBARSIZE*0.5),font2)

    # DRAW MR SMILEY
    squarelength = TOPBARSIZE*0.8
    pygame.draw.rect(screen, (80,180,80), (round(WIDTH*0.5)-(round(squarelength*0.5)), round(TOPBARSIZE*0.1), round(squarelength),round(squarelength))) # smiley background square
    pygame.draw.circle(screen, (255,255,80), (round(WIDTH*0.5),round(TOPBARSIZE*0.5)), round(squarelength*0.4)) # yellow circle
    pygame.draw.circle(screen, BLACK, (round(WIDTH*0.5),round(TOPBARSIZE*0.5)), round(squarelength*0.4), round(WIDTH*0.004)) # black circle outline

    # all of the percentages i found for these coordinates are trial and error this took a long time
    if lost: # if they die the face has to die too
        # left eye
        pygame.draw.line(screen,BLACK, (round(WIDTH*0.477),round(TOPBARSIZE*0.412)), (round(WIDTH*0.487), round(TOPBARSIZE*0.312)), round(WIDTH*0.004))
        pygame.draw.line(screen,BLACK, (round(WIDTH*0.487),round(TOPBARSIZE*0.412)), (round(WIDTH*0.477), round(TOPBARSIZE*0.312)), round(WIDTH*0.004))
        # right eye
        pygame.draw.line(screen,BLACK, (round(WIDTH*0.507),round(TOPBARSIZE*0.412)), (round(WIDTH*0.517), round(TOPBARSIZE*0.312)), round(WIDTH*0.004))
        pygame.draw.line(screen,BLACK, (round(WIDTH*0.517),round(TOPBARSIZE*0.412)), (round(WIDTH*0.507), round(TOPBARSIZE*0.312)), round(WIDTH*0.004))
        # sad mouth
        pygame.draw.circle(screen, BLACK, (round(WIDTH*0.5), round(TOPBARSIZE*0.67)), round(HEIGHT*0.02),round(WIDTH*0.003),True,True,False,False)
    else:
        # left eye
        pygame.draw.circle(screen,BLACK,(round(WIDTH*0.485),round(TOPBARSIZE*0.362)), round(TOPBARSIZE*0.05))
        # right eye
        pygame.draw.circle(screen,BLACK,(round(WIDTH*0.515),round(TOPBARSIZE*0.362)), round(TOPBARSIZE*0.05))
        # happy mouth
        pygame.draw.circle(screen, BLACK, (round(WIDTH*0.5), round(TOPBARSIZE*0.5)), round(HEIGHT*0.02),round(WIDTH*0.003),False,False,True,True)

    # draw grid lines
    for i in range(GRIDSIZEY): # horizontal
        pygame.draw.line(screen, BLACK, (0, i*TILESIZE+TOPBARSIZE), (WIDTH, i*TILESIZE+TOPBARSIZE))
    for i in range(GRIDSIZEX): # vertical
        pygame.draw.line(screen, BLACK, (i*TILESIZE, 0+TOPBARSIZE), (i*TILESIZE, HEIGHT))

    # loop through tiles
    for i in range(len(gameArray)):
        for j in range(len(gameArray[i])):
            if gameArray[i][j].hidden:

                # Draw hidden tiles
                if (i+j)%2 == 0: # checkered pattern i like this part
                    pygame.draw.rect(screen, LIGHTGREEN, (j*TILESIZE, i*TILESIZE+TOPBARSIZE, TILESIZE, TILESIZE))
                else:
                    pygame.draw.rect(screen, SLIGHTLYLESSLIGHTGREEN, (j*TILESIZE, i*TILESIZE+TOPBARSIZE, TILESIZE, TILESIZE))
                # Draw bombs (if dead or won)
                if lost: # show all bombs if dead
                    if gameArray[i][j].bomb and gameArray[i][j].colourChange:
                        pygame.draw.rect(screen,BLACK,(j*TILESIZE,i*TILESIZE+TOPBARSIZE, TILESIZE,TILESIZE))
                    # circle false flags in orange
                    elif gameArray[i][j].flagged and not gameArray[i][j].bomb:
                        pygame.draw.circle(screen,ORANGE, (round(j*TILESIZE+0.5*TILESIZE), round(i*TILESIZE+0.5*TILESIZE)+TOPBARSIZE), TILESIZE*0.5, round(TILESIZE*0.08))
                    # death message
                    centeredMessage(lossMessage,BLACK,(WIDTH/2)+WIDTH*0.001, (HEIGHT/2)+HEIGHT*0.003, font2) # this give a funny little 3d effect to the red text
                    centeredMessage(lossMessage,RED,WIDTH/2,HEIGHT/2, font2)
                    centeredMessage("R to restart",BLACK,WIDTH/2+WIDTH*0.001, HEIGHT/2+HEIGHT*0.08+HEIGHT*0.003, font2) # 3d effect again bc text was too hard to see
                    centeredMessage("R to restart",WHITE,WIDTH/2, HEIGHT/2 + HEIGHT*0.08, font2)
                if won: # do the same if they won but make it very bright neon green because green is a happy nice friendly colour.
                    if gameArray[i][j].bomb and gameArray[i][j].colourChange:
                        pygame.draw.rect(screen,(0,255,0),(j*TILESIZE,i*TILESIZE+TOPBARSIZE, TILESIZE,TILESIZE))
                    centeredMessage(f"{winMessage} ({seconds}s)",BLACK,(WIDTH/2)+WIDTH*0.001, (HEIGHT/2)+HEIGHT*0.003, font2)
                    centeredMessage(f"{winMessage} ({seconds}s)",(90,255,90),WIDTH/2,HEIGHT/2, font2)
                    centeredMessage("R to restart",BLACK,WIDTH/2+WIDTH*0.001, HEIGHT/2+HEIGHT*0.08+HEIGHT*0.003, font2)
                    centeredMessage("R to restart",WHITE,WIDTH/2, HEIGHT/2 + HEIGHT*0.08, font2)

                # Draw flags
                if gameArray[i][j].flagged: # the greatest flag art of all time:
                    flagx = int(j*TILESIZE+(TILESIZE*0.2)) # flagx and flagy serve no purpose except for making the code SLIGHTLY more bearable
                    flagy = int(i*TILESIZE+(TILESIZE*0.2)+TOPBARSIZE)
                    pygame.draw.rect(screen, RED, (flagx,flagy, int(TILESIZE*0.57), int(TILESIZE*0.4)))
                    pygame.draw.line(screen,GREY, (flagx,flagy), (flagx,flagy+int(TILESIZE*0.7)),3)
                    
            
            else: # Draw the numbers !!!!!!!!
                if gameArray[i][j].bomb == True:
                    showMessage("X",BLACK, j*TILESIZE+int(TILESIZE*0.1), i*TILESIZE-int(TILESIZE*0.05)+TOPBARSIZE, font)
                elif gameArray[i][j].bombsAround == 1:
                    showMessage("1",BLUE, j*TILESIZE+int(TILESIZE*0.2), i*TILESIZE-int(TILESIZE*0.05)+TOPBARSIZE, font)
                elif gameArray[i][j].bombsAround == 2:
                    showMessage("2",GREEN, j*TILESIZE+int(TILESIZE*0.2), i*TILESIZE-int(TILESIZE*0.05)+TOPBARSIZE, font)
                elif gameArray[i][j].bombsAround == 3:
                    showMessage("3",RED, j*TILESIZE+int(TILESIZE*0.2), i*TILESIZE-int(TILESIZE*0.05)+TOPBARSIZE, font)
                elif gameArray[i][j].bombsAround == 4:
                    showMessage("4",DARKBLUE, j*TILESIZE+int(TILESIZE*0.2), i*TILESIZE-int(TILESIZE*0.05)+TOPBARSIZE, font)
                elif gameArray[i][j].bombsAround == 5:
                    showMessage("5", BROWN, j*TILESIZE+int(TILESIZE*0.2), i*TILESIZE-int(TILESIZE*0.05)+TOPBARSIZE, font)
                elif gameArray[i][j].bombsAround == 6:
                    showMessage("6",CYAN, j*TILESIZE+int(TILESIZE*0.2), i*TILESIZE-int(TILESIZE*0.05)+TOPBARSIZE, font)
                elif gameArray[i][j].bombsAround == 7:
                    showMessage("7",BLACK, j*TILESIZE+int(TILESIZE*0.2), i*TILESIZE-int(TILESIZE*0.05)+TOPBARSIZE, font)
                elif gameArray[i][j].bombsAround == 8: # this will probably nver happen but just in case
                    showMessage("8",GREY, j*TILESIZE+int(TILESIZE*0.2), i*TILESIZE-int(TILESIZE*0.05)+TOPBARSIZE, font)        

# generate random mines around the grid
def generateBombs():
    global gameArray, BOMBCOUNT
    count = 0
    while count != BOMBCOUNT:
        x,y = random.randint(0,GRIDSIZEX-1), random.randint(0,GRIDSIZEY-1)
        if gameArray[y][x].bomb == False:
            gameArray[y][x].bomb = True
            count += 1
            print(f"bomb set {x},{y}")
        else:
            print("rerandomising")
generateBombs()

def showMessage(txt,colour,x,y, chosenfont): # does what it says on the tin
    textsurface = chosenfont.render(txt,True,colour)
    screen.blit(textsurface,(x,y))

def centeredMessage(txt,colour,x,y, chosenfont): # showmessage but centered around x and y coordinate, used for end screen
    textsurface = chosenfont.render(txt,True,colour)
    textrect = textsurface.get_rect()
    textrect.center = x,y
    screen.blit(textsurface,textrect)

def checkiftheguywonthegame(): # does what it says on the tin (incredible fuction name i know)
    global won
    won = True # by default is true
    for i in range(len(gameArray)):
        for j in range(len(gameArray[i])):
            if gameArray[i][j].hidden == True and gameArray[i][j].bomb == False: # if there is still any hidden tiles that arent bombs then they didnt win
                won = False
                break
        if not won:
            break # breaks out of the loops so it ends as soon as an uncovered tile is found, so it doesnt check the whole board every time

# this reveals every tile adjacent if the one you clicked has 0 bombs around it (i cheated this so hard because i couldnt figure out how to do it recursively)
def revealZeroTiles(): # this might be the most inefficient code i have ever written in my life
    global gameArray, flagsPlaced
    unchecked_zero_tiles = True # basicaly this says i should loop through the gameArray if there are any tiles with 0 bombs around them and have hidden tiles around them
    while unchecked_zero_tiles:
        print("hello")
        unchecked_zero_tiles = False # set this as default value so when it goes through the for loop "for coords in tilesAround" it will end loop if nothing is found
        for i in range(len(gameArray)):
            for j in range(len(gameArray[i])):

                if gameArray[i][j].bombsAround == 0 and not gameArray[i][j].hidden: # if player revealed 0 tile OR 0 tile was revealed as consequence of the while loop
                    tilesAround = [[i-1,j-1],[i-1,j],[i-1,j+1],[i,j-1],[i,j+1],[i+1,j-1],[i+1,j],[i+1,j+1]]

                    for coords in tilesAround: # keep repeating this while loop until all adjacent 0 tiles have been cleared
                        if coords[0] >= 0 and coords[0] <= GRIDSIZEY-1 and coords[1] >= 0 and coords[1] <= GRIDSIZEX-1:
                            if gameArray[coords[0]][coords[1]].flagged: # removes flag from tile before it's revealed to prevent bugs with function revealSurrounding and variable flagsPlaced
                                gameArray[coords[0]][coords[1]].flagged = False
                                flagsPlaced -= 1
                            if gameArray[coords[0]][coords[1]].hidden:
                                gameArray[coords[0]][coords[1]].hidden = False
                                unchecked_zero_tiles = True
                    
    
# reveal all 8 surrounding tiles, used for when player presses right click and left click at the same time and also has the correct amount of flags around a tile
def revealSurrounding(x,y):
    global gameArray
    global lost
    tilesAround = [[y-1,x-1],
                   [y-1,x],
                   [y-1,x+1],
                   [y,x-1],
                   [y,x+1],
                   [y+1,x-1],
                   [y+1,x],
                   [y+1,x+1]
                   ]

    flagsAround = 0 # count total flags around so only if total flags around = total bombs around will it work
    for coords in tilesAround:
        if coords[0] >= 0 and coords[0] <= GRIDSIZEY-1 and coords[1] >= 0 and coords[1] <= GRIDSIZEX-1:
            if gameArray[coords[0]][coords[1]].flagged:
                flagsAround += 1
    print(gameArray[y][x].bombsAround, flagsAround)
    if gameArray[y][x].bombsAround == flagsAround:
        for coords in tilesAround:
            if coords[0] >= 0 and coords[0] <= GRIDSIZEY-1 and coords[1] >= 0 and coords[1] <= GRIDSIZEX-1:
                if not gameArray[coords[0]][coords[1]].flagged:
                    gameArray[coords[0]][coords[1]].hidden = False
                    if gameArray[coords[0]][coords[1]].bombsAround == 0:
                        revealZeroTiles() # do this thing bc it usually does it with normal clicks but not in the reveal surrounding function
                    if gameArray[coords[0]][coords[1]].bomb == True:
                        lost = True

def timer():
    global seconds # make this global so the main program can use it
    seconds = 0
    starttime = time.time()
    while not lost and not won:
        pygame.time.wait(10)
        endtime = time.time()
        seconds = "{:.2f}".format(endtime-starttime,2) # i stole this off stack overflow idk how it works but it rounds and keeps the trailing zeros so the timer on the screen isnt giving you a seizure

def restart(): # this is all just recycled code to reset everything
    global gameArray,lost,won,seconds,timerthread, flagsPlaced, lossMessage, winMessage, rowY, freeStart
    lost = True # do this just do make sure timer stops
    pygame.time.wait(10)
    flagsPlaced = 0
    gameArray = [] # make array of tiles
    for _ in range(GRIDSIZEY):
        row = []
        for _ in range(GRIDSIZEX):
            row.append(Tile())
        gameArray.append(row)
    generateBombs()
    for i in range(GRIDSIZEY):
        for j in range(GRIDSIZEX):
            gameArray[i][j].bombsAround = checkSurrounding(i, j) # assign to the bombsaround attribute
            gameArray[i][j].hidden = True
            gameArray[i][j].flagged = False
    winMessage, lossMessage = random.choice(winmessages), random.choice(lossmessages)
    lost,won = False,False
    seconds = 0
    rowY = 0
    freeStart = True

def mrsmileygotclicked(x,y):
    squarepoint = (WIDTH*0.5) - (TOPBARSIZE*0.4)
    if x > squarepoint and x < squarepoint+TOPBARSIZE*0.8 and y > TOPBARSIZE*0.1 and y < (TOPBARSIZE*0.1)+TOPBARSIZE*0.8:
        print("check2")
        return True
    return False

def removebombsandregeneratesomewhereelseplease(bombAmount,y,x): # function for first click, 
    global gameArray
    tilesAround = [[y-1,x-1],
                   [y-1,x],
                   [y-1,x+1],
                   [y,x-1],
                   [y,x+1],
                   [y+1,x-1],
                   [y+1,x],
                   [y+1,x+1]
                   ]
    
    if gameArray[y][x].bomb:
        gameArray[y][x].bomb = False
        bombAmount += 1

    for coords in tilesAround:
        if coords[0] >= 0 and coords[0] <= GRIDSIZEY-1 and coords[1] >= 0 and coords[1] <= GRIDSIZEX-1:
            gameArray[coords[0]][coords[1]].bomb = False
            
    for _ in range(bombAmount): # rerandomises the boms
        while True:
            randomy,randomx = random.randint(0,GRIDSIZEY-1), random.randint(0,GRIDSIZEX-1)
            if not gameArray[randomy][randomx].bomb:
                gameArray[randomy][randomx].bomb = True
                if checkSurrounding(y,x) == 0 and not gameArray[y][x].bomb: # makes sure that it doesnt generate a bomb around the first selected tile, which would just defeat the whole purpose of the function
                    break
                elif gameArray[y][x].bomb: # if it regenerates bomb on selected tile get rid of it
                    gameArray[y][x].bomb = False
                else:
                    gameArray[randomy][randomx].bomb = False # if it is around the first selected tile, get rid of it and just make new coords

    
# --- No more functions ---

restart() # can use this function to set everything up

# the pygame part
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        elif event.type == pygame.KEYDOWN:
            keys = pygame.key.get_pressed()
            if event.key == pygame.K_r:
                restart()
                
            if keys[pygame.K_w] and keys[pygame.K_i] and keys[pygame.K_n]:
                for i in range(len(gameArray)):
                    for j in range(len(gameArray[i])):
                        if not gameArray[i][j].bomb:
                            gameArray[i][j].hidden = False
                checkiftheguywonthegame()
                
            if keys[pygame.K_f] and keys[pygame.K_l] and keys[pygame.K_a]:
                if flagsPlaced >= BOMBCOUNT:
                    for i in range(len(gameArray)):
                        for j in range(len(gameArray[i])):
                            if gameArray[i][j].flagged:
                                gameArray[i][j].flagged = False
                                flagsPlaced -= 1
                else:
                    for i in range(len(gameArray)):
                        for j in range(len(gameArray[i])):
                            if gameArray[i][j].bomb and not gameArray[i][j].flagged:
                                gameArray[i][j].flagged = True
                                flagsPlaced += 1
                            if gameArray[i][j].flagged and not gameArray[i][j].bomb:
                                gameArray[i][j].flagged = False
                                flagsPlaced -= 1

        # --- mouse shenanigans ---
        elif event.type == pygame.MOUSEBUTTONDOWN:
            button = pygame.mouse.get_pressed() # makes an array of booleans for which button is pressed [left,middle,right]
            if seconds == 0:
                timerthread = threading.Thread(target=timer) # start timer as soon as click happens
                timerthread.start()


        elif event.type == pygame.MOUSEBUTTONUP: # only register press on release
            x,y = pygame.mouse.get_pos() # gets coordinates of the click

            if mrsmileygotclicked(x,y):
                restart()

            # ignore top bar size so the coordinate calculation tingy works
            y -= TOPBARSIZE

            if y >= 0: # when you click the topbar, it reveals tiles at the bottom. this stops it from happening
                x,y = int(x/TILESIZE), int(y/TILESIZE) # divides by tilesize and truncates it to make them into coordinates for array
                try:
                    if not lost and not won: # cant reveal tiles if you are dead or if you win theres no point yk
                        if button[0]:
                            if not gameArray[y][x].flagged: # only reveal tile if its not flagged
                                if freeStart:
                                    freeStart = False
                                    if gameArray[y][x].bomb or gameArray[y][x].bombsAround > 0:
                                        removebombsandregeneratesomewhereelseplease(gameArray[y][x].bombsAround, y,x)
                                        for i in range(GRIDSIZEY):
                                            for j in range(GRIDSIZEX):
                                                gameArray[i][j].bombsAround = checkSurrounding(i, j)
                                        
                                        
                                gameArray[y][x].hidden = False
                                if gameArray[y][x].bomb == True:
                                    lost = True
                                if gameArray[y][x].bombsAround == 0 and not gameArray[y][x].bomb:
                                    revealZeroTiles()
                                checkiftheguywonthegame()

                        elif button[2]:
                            if gameArray[y][x].hidden: # only flag if hidden
                                if not gameArray[y][x].flagged:
                                    gameArray[y][x].flagged = True
                                    flagsPlaced += 1
                                else:
                                    gameArray[y][x].flagged = False
                                    flagsPlaced -= 1

                        if button[0] and button[2]:
                            revealSurrounding(x,y)
                except IndexError: # this stops you from holding down click then dragging your mouse out of the game which would crash it
                    tellplayertostopit = True
            
    # the little animation part
    if won or lost:
        if rowY <= len(gameArray)-1:
            farRightBombX = -1
            for i in range(len(gameArray[rowY])):
                if gameArray[rowY][i].bomb:
                    farRightBombX = i # find the furthest bomb to the right first

            if farRightBombX == -1:
                rowY += 1 # skip row if theres no bombs
            else:
                for i in range(len(gameArray[rowY])):
                    if gameArray[rowY][i].bomb and not gameArray[rowY][i].colourChange: # make the tiles light up one by one
                            gameArray[rowY][i].colourChange = True
                            if i == farRightBombX:
                                print(f"rowY = {rowY}\ni = {i}\nfarRightBombX = {farRightBombX}\nlen = {len(gameArray)}\n\n\n")
                                rowY += 1 # move down row if the last bomb in the row has been highlighted
                            break

    drawGame()
    if tellplayertostopit:
        centeredMessage("stop it", RED, WIDTH/2, (HEIGHT)/2, font2)
        pygame.display.flip()
        time.sleep(1)
        tellplayertostopit = False
        
    pygame.display.flip()
    clock.tick(30)
