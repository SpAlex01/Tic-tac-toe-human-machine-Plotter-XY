import numpy as np
import argparse
import cv2
import regions
import tictactoe
import time
import pygame
import serial

# define video port here, usually 0


SERIALPORT = "/dev/ttyACM0"
tabla ="D:\Licenta\TABLAXSIObuna.gcode"
# define video port here, usually 0
VIDEPORT = 1
port = 'COM12'

def desentabla(port, tabla):
    # Open the serial connection
    ser = serial.Serial(port, 115200)  # Replace the baud rate if necessary

    # Open the G-code file
    with open(tabla, 'r') as file:
        # Iterate through the file line by line
        for line in file:
            # Strip any leading/trailing whitespace and newline characters
            line = line.strip()
            print(line)

            # Skip empty lines or comments
            if not line or line.startswith(';'):
                continue

            # Send the G-code line to the device
            ser.write((line + '\n').encode())


            # Wait for the device to process the command (optional)
            ser.readline()

    # Close the serial connection
    ser.close()

def send_gcode_file(port,computerMove):

    filename_mappings = {
        0: 'X1.gcode',
        1: 'X2.gcode',
        2: 'X3.gcode',
        3: 'X4.gcode',
        4: 'X5.gcode',
        5: 'X6.gcode',
        6: 'X7.gcode',
        7: 'X8.gcode',
        8: 'X9.gcode',
    }

    # Check if the computerMove is valid
    if computerMove not in filename_mappings:
        print("Invalid computerMove")
        return
    # Open the serial connection
    ser = serial.Serial(port, 115200)  # Replace the baud rate if necessary
    if computerMove == 0:
        filename = 'X9.gcode'
    elif computerMove == 1:
        filename = 'X8.gcode'
    elif computerMove == 2:
        filename = 'X7.gcode'
    elif computerMove == 3:
        filename = 'X6.gcode'
    elif computerMove == 4:
        filename = 'X5.gcode'
    elif computerMove == 5:
        filename = 'X4.gcode'
    elif computerMove == 6:
        filename = 'X3.gcode'
    elif computerMove == 7:
        filename = 'X2.gcode'
    elif computerMove == 8:
        filename = 'X1.gcode'
    # Open the G-code file
    with open(filename, 'r') as file:
        # Iterate through the file line by line
        for line in file:
            # Strip any leading/trailing whitespace and newline characters
            line = line.strip()

            # Skip empty lines or comments
            if not line or line.startswith(';'):
                continue

            # Send the G-code line to the device
            ser.write((line + '\n').encode())

            # Wait for the device to process the command (optional)
            ser.readline()

    # Close the serial connection
    ser.close()


def findCircles(image):
    # Returns the position and the size of the circle found.
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.blur(gray,(5,5))
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1.4, 30)
    return circles

def drawCircles(image, x , y, r):
    # Draws a circle on the frame.
    cv2.circle(image, (x, y), r, (0, 255, 0), 4)
    cv2.rectangle(image, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)

def findMove(image, circles):
    # Returns the move of the opponent.

    # convert coordinates to integer
    circles = np.round(circles[0, :]).astype("int")
    opponentMove = 0

    # iterate all circles found
    for (x, y, r) in circles:

        isMoved = True
        # check which region the found circle belongs to
        if((x >= regions.minX) and (x <= regions.maxX)) and ((y >= regions.minY) and (y <= regions.maxY)):
            region = regions.checkRegion(x,y)
        else:
            break

        # iterate all available moves
        for move in board.availableMoves():
            # if the region has'nt been occupied, take it as the opponent's move
            if move + 1  == region:
                isMoved = False
                break
            # do nothing if the region has been occupied before
            else:
                pass

        if not isMoved:
            opponentMove = region - 1
            isMoved = True
            return opponentMove

def nextMove(opponentMove):
    # Returns the next best move for the arm

    player = 'X'
    # save the opponent's move in the list
    board.makeMove(opponentMove, player)
    print("Opponent Move: ", opponentMove + 1)
    board.show()

    # get the next best move based on the opponent's move
    player = tictactoe.getEnemy(player)
    computerMove = tictactoe.determine(board, player)

    # save the computer's move in the list
    board.makeMove(computerMove, player)
    send_gcode_file(port, computerMove)
    print("Computer Move: ", computerMove + 1)
    board.show()

    # play a beep sound the acknowldge the opponent's move
    pygame.init()
    pygame.mixer.music.load("aplauze1.wav")
    pygame.mixer.music.play()
    return computerMove + 1

def drawRegions(image):
    # Draws all the squares on the frame
    '''
    sample data
    [0, 213, 426, 639]
    [0, 160, 320, 480]
    r1 = (0   , 0  ) (213  , 160)
    r2 = (213 , 0  ) (426  , 160)
    r3 = (426 , 0  ) (640  , 160)

    r4 = (0 ,  160 ) (213, 320)
    r5 = (213, 160 ) (426, 320)
    r6 = (426, 160 ) (640, 320)

    r7 = (0, 320 ) (213, 480)
    r8 = (213, 320 ) (426, 480)
    r9 = (426, 320 ) (640, 480)
    '''
    fontIndex = 0
    for i in range(regions.totalYintercepts-1):
        for ii in range(regions.totalXintercepts-1):
            x1 = regions.xIntercepts()[ii]
            x2 = regions.xIntercepts()[ii + 1]
            y1 = regions.yIntercepts()[i]
            y2 = regions.yIntercepts()[i + 1]
            # draw the rectangles
            x1 = int(x1)
            y1 = int(y1)
            x2 = int(x2)
            y2 = int(y2)
            cv2.rectangle(image,(x1,y1),(x2,y2),(0,255,0),2)
            fontIndex = fontIndex + 1
            #dra the labels
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(image,str(fontIndex),(x1 +5,y1+25), font, 0.7,(255,255,255),2)

def drawOpponentMoves(image):
    # Draws all the opponent's moves on the frame
    for move in board.getSquares('X'):
        x = int(regions.center()[move][0])
        y = int(regions.center()[move][1])
        cv2.circle(image, (x, y), 40, (0, 0, 255), 10)

def drawComputerMoves(image):
    # Draws all the computer's moves on the frame
    for move in board.getSquares('O'):
        x = regions.center()[move][0]
        y = regions.center()[move][1]
        x1 = int(x - 40)
        y1 = int(y - 40)
        x2 = int(x + 40)
        y2 = int(y + 40)

        X1 = int(x + 40)
        Y1 = int(y - 40)
        X2 = int(x - 40)
        Y2 = int(y + 40)

        pt1 = (x1, y1)
        pt2 = (x2, y2)
        pt3 = (X1, Y1)
        pt4 = (X2, Y2)

        cv2.line(image, pt1, pt2, (255, 0, 0), 10)
        cv2.line(image, pt3, pt4, (255, 0, 0), 10)

def main():
    # store which turn it is.
    turn = 0
    # continue looping until there's a winner
    while not board.complete():

        # get the frame from the video feed
        ret, image = videoCapture.read()

        # find all the circles on the frame
        circles = findCircles(image)

        if circles is not None:

            # get opponent's move
            opponentMove = findMove(image, circles)
            if not opponentMove in board.availableMoves():
                continue

            # calculate what's the next move
            computerMove = nextMove(opponentMove)

            #end the game if thpyere's any winner
            if board.complete():

                break

        #draw opponent's and computer's move on the screen
        drawComputerMoves(image)
        drawOpponentMoves(image)
        drawRegions(image)
        cv2.imshow('TICTACTOE',image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    if board.winner() == 'O':
        print("winner is X")
    elif board.winner() == 'X':
        print("winner is 0")
    else:
        print("winner is None")
    pygame.mixer.music.load("aplauze2.wav")
    pygame.mixer.music.play()
    time.sleep(1)
    videoCapture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":

    regions = regions.Regions(50,400,400,50,3,3)
    videoCapture = cv2.VideoCapture(VIDEPORT)
    board = tictactoe.Tic()
    image = None
    desentabla(port, tabla)
    main()
