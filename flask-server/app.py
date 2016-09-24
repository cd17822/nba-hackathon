from flask import Flask
from flask import render_template
# import pandas as pd
# import math
# from scipy import stats
# import json

app = Flask(__name__)
# data = pd.read_csv("data/game.csv")
# global OFFENSE
# OFFENSE = data[((data["BX"] <= 47) & (data["Period"].isin([1,2]))) | ((data["BX"] >= 47) & (data["Period"].isin([3,4])))]
# OFFENSE["RevClock"] = OFFENSE.apply(lambda x: 720-math.ceil(x["Game_Clock"]), axis=1)
# OFFENSE["Clock"] = OFFENSE.apply(lambda x: 720*(x["Period"]-1) + x["RevClock"], axis=1)
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

@app.route('/home/')
def home():
    return render_template('index.html')

def smooth_list(l):
    for i in range(1, len(l)-1):
        before = l[i-1]
        now = l[i]
        after = l[i+1]
        if before==after:
            if now!= before:
                now = before
                l[i] = now
    return l

def player_dist(row, playerID=PLAYER, teamID=1610612744):
# def player_dist(row):
    opposing_players = []
    player = []
    closest = None
    for i in range(1,11):
        name = "Player"+str(i)
        pid = name+".1"
        tid = name+"Team"
        x = "P"+str(i)+"X"
        y = "P"+str(i)+"Y"
        if row[tid] != teamID:
            opposing_players.append([row[x], row[y], row[name]])
        try:
            if (playerID in row[name]) and (row[tid] == teamID):
                player = [row[x],row[y]]
        except TypeError:
            pass
    distance = float("inf")
    if len(player) == 2:
        for p in opposing_players:
            d = (p[0]-player[0])*(p[0]-player[0]) + (p[1]-player[1])*(p[1]-player[1])
            d = math.sqrt(d)
            if d < distance:
                closest = p[2]
                distance = d
    return closest

# @app.route('/defense/<last_name>')
# def defense(last_name):
#     print "in here"
#     global PLAYER
#     PLAYER = last_name
#     offense = OFFENSE
#     offense["Closest"] = offense.apply(lambda x: player_dist(x), axis=1)
#     clock = offense.groupby("Clock")
#     valid = clock.filter(lambda x: len(x) <= 30).groupby("Clock")
#     per_sec = valid["Closest"].agg(stats.mode)
#     closest = per_sec.to_frame()
#     closest["Second"] = closest.index
#     closest["Minute"] = closest.apply(lambda x: math.ceil(x["Second"]/60), axis=1)
#     closest["Name"] = closest.apply(lambda x: x["Closest"][0][0], axis=1)
#     closest_by_min = closest.groupby("Minute")
#     per_min = closest_by_min["Name"].agg(stats.mode)
#     closest_min = per_min.to_frame()
#     closest_min["Minute"] = closest_min.index
#     closest_min["Name"] = closest_min.apply(lambda x: x["Name"][0][0], axis=1)
#     l = list(closest_min.sort_values("Minute")["Name"].values)
#     return '{ "defense":' + json.dumps(smooth_list(l)) + '}'
@app.route('/defense/<last_name>')
def defense(last_name):
    return '{ "defense":["JR Smith", "Kyrie Irving", "Kyrie Irving", "Kyrie Irving", "JR Smith", "JR Smith", "Kyrie Irving", "Kyrie Irving", "Kyrie Irving", "Tristan Thompson", "Matthew Dellavedova", 0, 0, "Iman Shumpert", "Iman Shumpert", "Iman Shumpert", "Iman Shumpert", "Iman Shumpert", "Iman Shumpert", "Iman Shumpert", "Iman Shumpert", "Iman Shumpert", "Richard Jefferson", "LeBron James", "Kyrie Irving", "Kyrie Irving", "Tristan Thompson", "JR Smith", "Kyrie Irving", "Kyrie Irving", "Kyrie Irving", 0, 0, 0, "LeBron James", "Iman Shumpert", "Iman Shumpert", "Iman Shumpert", "Iman Shumpert", "Iman Shumpert", "Iman Shumpert", "Iman Shumpert", "Kyrie Irving", "JR Smith", "JR Smith", 0, 0, 0]}'

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
        if PLAYER == 'Thompson' and not '[GSW' in line: return #the thompson glitch
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
        if PLAYER == 'Thompson' and not '[GSW' in line: return #the thompson glitch
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
