from flask import Flask
app = Flask(__name__)

#misc
SECONDS_IN_PERIOD = 12 * 60
GAME_IS_OVER = False
IN_GAME = False
GAME_ID = '41500405'
PLAYER = 'Curry'
DATA = []
LAST_DATAPOINT = 0
DATA_INDEX = 0

#fgpct
MADE_SHOT = 'Made Shot'
MISSED_SHOT = 'Missed Shot'
CURR_FGM = 0
CURR_FGA = 0

#pts
FREE_THROW = 'Free Throw'
MISSED = 'missed'
PTS = 0

@app.route('/pts/<last_name>')
def pts(last_name):
    global PLAYER
    PLAYER = last_name

    initPtsGlobals()

    return getPtsData()

def initPtsGlobals():
    global DATA_INDEX, GAME_IS_OVER, IN_GAME, DATA, LAST_DATAPOINT, PTS
    GAME_IS_OVER = False
    IN_GAME = False
    DATA = []
    DATA_INDEX = 0
    LAST_DATAPOINT = 0

    PTS = 0

def getPtsData():
    global GAME_IS_OVER, IN_GAME

    with open('Hackathon_play_by_play.txt', 'r') as f:
        for line in f:
            if GAME_IS_OVER:
                break
            elif not IN_GAME:
                if GAME_ID in line:
                    IN_GAME = True
            else:
                parseGameLineForPts(line)

    f.close()

    updateDataToIndex(2880, LAST_DATAPOINT)

    data_string  = ', '.join(str(d) for d in DATA)
    return '{"pts": [' + data_string + ']}'

def parseGameLineForPts(line):
    global PTS

    if not GAME_ID in line:
        IN_GAME = False
        GAME_IS_OVER = True
    elif PLAYER in line and not "Assist: "+PLAYER in line and not "Block: "+PLAYER in line:
        period = int(line.split()[4]) - 1
        seconds_elapsed_in_period = SECONDS_IN_PERIOD - int(line.split()[9]) / 10

        total_second = period * SECONDS_IN_PERIOD + seconds_elapsed_in_period

        if MADE_SHOT in line or (FREE_THROW in line and not MISSED in line):
            before_pts_string = line.split('PTS')[0]
            print before_pts_string
            PTS = int(before_pts_string.split('(')[len(before_pts_string.split('('))-1])
            print PTS

        updateDataToIndex(total_second, PTS)


@app.route('/fgpct/<last_name>')
def fgpct(last_name):
    global PLAYER
    PLAYER = last_name

    initFgpctGlobals()

    return getFgpctData()

def initFgpctGlobals():
    global DATA_INDEX, CURR_FGA, CURR_FGM, GAME_IS_OVER, IN_GAME, DATA, LAST_DATAPOINT
    GAME_IS_OVER = False
    IN_GAME = False
    DATA = []
    LAST_DATAPOINT = 0
    DATA_INDEX = 0

    CURR_FGM = 0
    CURR_FGA = 0

def getFgpctData():
    global GAME_IS_OVER, IN_GAME

    with open('Hackathon_play_by_play.txt', 'r') as f:
        for line in f:
            if GAME_IS_OVER:
                break
            elif not IN_GAME:
                if GAME_ID in line:
                    IN_GAME = True
            else:
                parseGameLineForFgpct(line)

    f.close()

    updateDataToIndex(2880, LAST_DATAPOINT)

    data_string  = ', '.join(str(d) for d in DATA)
    return '{"fgpct": [' + data_string + ']}'

def parseGameLineForFgpct(line):
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

        if CURR_FGA != 0:
            updateDataToIndex(total_second, CURR_FGM * 1.0 / CURR_FGA)
        else:
            updateDataToIndex(total_second, 0)

def updateDataToIndex(index, data):
    global DATA_INDEX, LAST_DATAPOINT

    for i in xrange(index - DATA_INDEX):
        DATA.append(LAST_DATAPOINT)

    LAST_DATAPOINT = data
    DATA_INDEX = index

if __name__ == '__main__':
    main()
