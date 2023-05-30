# Jake Watson
# EG SWE Home Assessment

# used for part 1
import pandas as p, numpy as np, pyarrow.parquet as pq
# used for part 2c
import matplotlib.pyplot as plot
import matplotlib.cm as cm
from scipy.spatial import cKDTree
# open the image after generation
import os

# pandas options used in testing
p.options.display.min_rows = 221330
p.options.display.max_columns = 20
p.options.display.max_colwidth = 250
p.options.display.width = 120

# selected columns
desiredColumns = ['round_num', 'tick', 'side', 'team', 'x', 'y', 'z', 'inventory', 'clock_time', 'player']

# Things to note:
"""
128 tick servers, tick rate in given data is entry every 16 ticks -> 8 entries/second
Entries listed by player, not by round
For all relevant entries, is_alive is true, so it can be ignored
"""


"""
    Equations for bounds:
    13-14: y = -0.512x - 638.32     G
    14-15: y = -0.44x - 492.56      G
    15-16: y = 1.47x + 4866.82      L
    16-17: y = -0.72x - 546.84      L
    17-13: y = 1.941x + 3617.665    G
    Z GE 285
    Z LE 421
"""

# Note: depending on shape of area, some equations may have to be 'or's instead of 'and's (if other areas are going to be used in the future)
def BoundsCheckArea(x, y, z) -> bool:
    if (
        z >= 285 and z <= 421 and 
        y > -0.512*x - 638.32 and 
        y > -0.44*x - 492.56 and 
        y < 1.47*x + 4866.82 and 
        y < -0.72*x - 546.84 and 
        y > 1.941*x + 3617.665
    ):
        return True
    else:
        return False



class ProcessGameState:
    # read in from provided file
    # used https://arrow.apache.org/docs/python/parquet.html to understand arrows, as I had not used them before
    filename = 'data\game_state_frame_data.parquet'
    print("Reading in", filename)
    data = pq.read_table(filename, columns = desiredColumns).to_pandas()
    print("Finished reading", filename)

    # the last entry is the last tick of the last round for the last player, which is a reliable method of getting the total round #  efficiently
    # unknown behaviour if last player disconnects early, do not have data to test it on
    maxrounds = data.iloc[-1]['round_num']
    # other variables
    areaName = 'BombsiteB'
    time2pEnteredBombsiteB = []
    current_round = 1
    coordsOfPlayerInBombsiteB = list()

    #structure to store the names of players who enter the area, and in what round
    playersInBombsiteB = dict()
    for i in range(1, maxrounds+1):
        playersInBombsiteB[i] = list()

    print("Parsing through the data to search for desired data")
    # ****IMPORTANT NOTE: DATA IS ORDER BY PLAYER, NOT ROUND
    for ind in data.index:  # search all rows
        if data['team'][ind] == 'Team2' and data['side'][ind] == 'T':   # search only rows for Team2 T side 
            if BoundsCheckArea(data['x'][ind], data['y'][ind], data['z'][ind]) and data['player'][ind] not in playersInBombsiteB[data['round_num'][ind]]:   # Note: do not need to check is_alive, it is always true
                
                hasDesiredWeapon = False
                for d in data['inventory'][ind]:
                    if d['weapon_class'] == 'Rifle' or d['weapon_class'] == 'SMG':
                        print(data['player'][ind], 'has desired weapon class: ', d['weapon_class'], '\r, and has entered', areaName, 'at', data['clock_time'][ind])
                        hasDesiredWeapon = True
                
                if hasDesiredWeapon:
                    count = 0
                    for p in playersInBombsiteB[data['round_num'][ind]]:
                        if '*' in p:
                            count += 1
                    if count == 1:  # only want to run this for exactly 1 player with this condition, because if mroe entered we do not want to count the same round multiple times
                        time2pEnteredBombsiteB.append(data['clock_time'][ind])
                    playersInBombsiteB[data['round_num'][ind]].append(data['player'][ind] + '*')    # '*' is used to denote that they entered BombsiteB area with a Rifle or SMG
                else:
                    playersInBombsiteB[data['round_num'][ind]].append(data['player'][ind])

                # print(data['player'][ind], 'has entered B at', data['clock_time'][ind])
            
        elif data['team'][ind] == 'Team2' and data['side'][ind] == 'CT':    # search only Team2 CT side
            if BoundsCheckArea(data['x'][ind], data['y'][ind], data['z'][ind]):   # Note: do not need to check is_alive, it is always true

                # ignoring z coordinate here since the BombsiteB area is flat, and we are interested in where they are within 2D space, 
                # and changes in height due to jumping or other reasons are trivial
                # using 2 coordinates also considerably speeds up the 'nearest neighbor' algorithm used to find hot spots
                coordsOfPlayerInBombsiteB.append([data['x'][ind], data['y'][ind]])

    

        

    # determine which rounds team2 played T side
    team1FirstSide = None
    minRound = 1
    maxRound = 15
    if data['team'][0] == 'Team1':
        team1FirstSide = data['side'][0]
    else:
        # first team listed is Team2, shouldn't happen but just in case
        if data['side'][0] == 'T':
            team1FirstSide = 'CT'
        else:
            team1FirstSide = 'T'
    
    # Team2 is T first
    if team1FirstSide == 'CT':
        minRound = 1
        maxRound = 15
    else:
        minRound = 16
        maxRound = maxrounds

    # free up memory as the data is no longer directly needed
    del data

    print('Team2 entered the', areaName, 'specified area on the following:\nR#    Player(s)')
    numRoundsInBombsiteB = 0
    for k, v, in playersInBombsiteB.items():
        if k >= minRound and k <= maxRound:
            if v != list():
                numRoundsInBombsiteB += 1
                print(str(k).ljust(4, ' '), v)

    # 2a
    print('Liklihood of Team2 T side entering', areaName, '(light blue area): ')
    # threshold for likely is 20% (made up since none were listed)
    percentRoundinBombsiteB = numRoundsInBombsiteB/(maxRound + 1 - minRound)
    threshold = 0.2
    print(f'{percentRoundinBombsiteB:2.3f}', '\b%, or ', numRoundsInBombsiteB, '/' , (maxRound + 1 - minRound))
    if percentRoundinBombsiteB > threshold:
        print("This is a significant number of times to use", areaName)


    # 2b calculate average time that the second Team2 T side player enters bombsite B
    if len(time2pEnteredBombsiteB) > 0:
        avgTime = 0
        for t in time2pEnteredBombsiteB:
            min_and_sec = t.split(':')  # calculating it based on split allows for flexibility if the match timer is not single digit minutes
            avgTime += int(min_and_sec[0]) * 60 + int(min_and_sec[1])
        
        avgTime /= len(time2pEnteredBombsiteB)

        print("Average time for 2 players from Team2 T side to enter", areaName, "area with an SMG or Rifle:", avgTime)
    else:
        print("No rounds meet the 2 players from Team2 T side to enter", areaName, "area with an SMG or Rifle condition")


    
# 2c
# ----Generate a heatmap of where Team2 CT players are likely to be within the area
# NOTE:I used https://stackoverflow.com/questions/2369492/generate-a-heatmap-using-a-scatter-data-set/59920744# 59920744 for most of the following section. 
# Everything above these comment is completely original work

# I began to work on an original method for creating a heatmap, but I switched to this when I realized the problems with it
# My solution: Calculate the squared distance (x2-x1)*(y2-y1) between all points (was planning on adding caching to speed things up), 
# I was using squared distance not the regular distance formula because sqrt is a relatively inefficient operation, and the time efficiency is already O(n^2)
# Once all of the distances were found, I would keep the top x, I was planning on ~20, and the lower the summed distance value was, the closer together many points were
# From that, the point with the lowest summed distance value would be the hotspot
# 
# As I thought about part 3 of the task, it made more and more sense to switch to a library implementation of a similar problem, which is how I came across the nearest neighbor problem
# This solution uses a 2-D tree and is able to much more efficiently calculate the nearest neighbor sums with trimming


    print("Generating the heatmap image")

    def data_coord2view_coord(p, resolution, pmin, pmax):
        dp = pmax - pmin
        dv = (p - pmin) / dp * resolution
        return dv


    n = len(coordsOfPlayerInBombsiteB)
    xs, ys = list(), list()
    for e in coordsOfPlayerInBombsiteB:
        xs.append(e[0])
        ys.append(e[1])
    
    resolution = 250

    extent = [np.min(xs), np.max(xs), np.min(ys), np.max(ys)]
    xv = data_coord2view_coord(xs, resolution, extent[0], extent[1])
    yv = data_coord2view_coord(ys, resolution, extent[2], extent[3])


    def kNN2DDens(xv, yv, resolution, neighbours, dim=2):
        """
        """
        #  Create the tree
        tree = cKDTree(np.array([xv, yv]).T)
        #  Find the closest nnmax-1 neighbors (first entry is the point itself)
        grid = np.mgrid[0:resolution, 0:resolution].T.reshape(resolution**2, dim)
        dists = tree.query(grid, neighbours)
        #  Inverse of the sum of distances to each grid point.
        inv_sum_dists = 1. / dists[0].sum(1)

        #  Reshape
        im = inv_sum_dists.reshape(resolution, resolution)
        return im


    fig, axes = plot.subplots(1, 2, figsize=(15, 15))
    for ax, neighbours in zip(axes.flatten(), [0, 16]):

        if neighbours == 0:
            ax.plot(xs, ys, 'k.', markersize=5)
            ax.set_aspect('equal')
            ax.set_title("Scatter Plot")
        else:

            im = kNN2DDens(xv, yv, resolution, neighbours)

            ax.imshow(im, origin='lower', extent=extent, cmap=cm.Blues)
            ax.set_title("Smoothing over %d neighbours" % neighbours)
            ax.set_xlim(extent[0], extent[1])
            ax.set_ylim(extent[2], extent[3])

    plot.savefig('heatmap.png', dpi=150, bbox_inches='tight')
    print("Image generation done\n")

    os.startfile('heatmap.png')

# Test cases for bounds checking:
"""
print('-2200, 800, 300 ', BoundsCheckArea(-2200, 800, 300))
print('-1800, 400, 350 ', BoundsCheckArea(-1800, 400, 350))
print('-2000, 300, 350 ', BoundsCheckArea(-2000, 300, 350))
print('-2700, 750, 350 ', BoundsCheckArea(-2700, 750, 350))

"""