import requests

username = "PhirstBlood"
headers = {"User-Agent": "chess-analytics-dashboard/1.0"}

# Get player info
response = requests.get(f"https://api.chess.com/pub/player/{username}", headers=headers)
data = response.json()
#print(response.status_code)

print(f"Username: {data['username']}")
print(f"Status: {data['status']}")
print(f"Followers: {data['followers']}")

# Get recent games
games_response = requests.get(f"https://api.chess.com/pub/player/{username}/games/archives", headers=headers)
games_data = games_response.json()

print(f"\nGame archives available: {len(games_data['archives'])}")
print("Most recent archive:", games_data['archives'][-1])

# Get most recent month of games
recent_games_response = requests.get(games_data['archives'][-1], headers=headers)
recent_games = recent_games_response.json()

print(f"\nGames played this month: {len(recent_games['games'])}")

# Total games played
all_games = [] #empty list to store all games played 

for games in games_data['archives']:
    recent_games_response = requests.get(games, headers=headers ) #gets data from the games url
    recent_games = recent_games_response.json()

    all_games.extend(recent_games['games']) #adds list of games onto list

print(f"\nAll the games played since joining: {len(all_games)}")


# Look at the first game
first_game = recent_games['games'][0]
print(f"\nFirst game details:")
print(f"White: {first_game['white']['username']}")
print(f"Black: {first_game['black']['username']}")
print(f"Result: {first_game['white']['result']}")
print(f"Time class: {first_game['time_class']}")

#Look at the last game
first_game = recent_games['games'][-1]
print(f"\nLast game details:")
print(f"White: {first_game['white']['username']}")
print(f"Black: {first_game['black']['username']}")
print(f"Result: {first_game['white']['result']}")
print(f"Time class: {first_game['time_class']}")


#Check for wins losses and draws
win = 0
loss = 0
draw = 0

b_win = 0
w_win = 0

w_games=0
b_games=0

for games in all_games:
    if games['white']['username'] == username: #checks if username matches and gives the color played
        w_games +=1
        if games['white']['result'] == "win":
            win +=1
            w_win +=1
        elif games['white']['result'] =="agreed" or games['white']['result'] =="stalemate" or games['white']['result'] =="repetition":
            draw +=1
        else:
            loss +=1
    else:
            b_games +=1
            if games['black']['result'] == "win":
                win +=1
                b_win +=1
            elif games['black']['result'] =="agreed" or games['black']['result'] =="stalemate" or games['black']['result'] =="repetition":
                draw +=1
            else:
                loss +=1

print(f"\nWins: {win}")
print(f"Losses: {loss}")
print(f"Draws: {draw}")

print(f"Total White games: {w_games} Wins as White: {w_win}")
print(f"Win rate as White: {w_win/w_games*100:.2f}%")

print(f"Total black games {b_games} Wins as Black: {b_win}")
print(f"Win rate as Black: {b_win/b_games*100:.2f}%")

