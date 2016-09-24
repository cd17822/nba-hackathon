#################
#DEPRECATED - SEE flask-server/app.py
#################

SECONDS_IN_PERIOD = 12 * 60

GAME_IS_OVER = False
IN_GAME = False
GAME_ID = '41500405'
PLAYER = 'Curry'
MADE_SHOT = 'Made Shot'
MISSED_SHOT = 'Missed Shot'
DATA = []
DATA_INDEX = 0
CURR_FGM = 0
CURR_FGA = 0

def main():
    global GAME_IS_OVER, IN_GAME
    line_no = 0 #for debugging only
    with open('Hackathon_play_by_play.txt', 'r') as f:
        for line in f:
            if GAME_IS_OVER:
                break
            elif not IN_GAME:
                if GAME_ID in line:
                    IN_GAME = True
            else:
                parseGameLine(line)

            #for debugging only
            line_no += 1
            if line_no % 1000000 == 0:
                pass
                #print line_no

    f.close()

    updateDataToIndex(2880)

    print '{"andrew_bogut":', DATA, "},"
    #print len(DATA)

def parseGameLine(line):
    global CURR_FGA, CURR_FGM

    if not GAME_ID in line:
        IN_GAME = False
        GAME_IS_OVER = True
    elif PLAYER in line and not "Assist: "+PLAYER in line and not "Block: "+PLAYER in line:
        period = int(line.split()[4]) - 1
        seconds_elapsed_in_period = SECONDS_IN_PERIOD - int(line.split()[9]) / 10

        total_second = period * SECONDS_IN_PERIOD + seconds_elapsed_in_period

        if MADE_SHOT in line:
            CURR_FGM += 1
            CURR_FGA += 1
        elif MISSED_SHOT in line:
            CURR_FGA += 1

        updateDataToIndex(total_second)

def updateDataToIndex(index):
    global DATA_INDEX

    for i in xrange(index - DATA_INDEX):
        if CURR_FGA == 0:
            DATA.append(0)
        else:
            DATA.append(CURR_FGM * 1.0 / CURR_FGA)
    DATA_INDEX = index

if __name__ == '__main__':
    main()
