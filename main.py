import requests
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score



username = input("Enter a  Chess.com username (case sensitive): ")
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

print(f"\nAll the games played since joining: {len(all_games)}\n")

#Pandas Implementation
df= pd.DataFrame(all_games)
#print(df.head())
#print(f"DataFrame shape: {df.shape}")
#print(df.columns.tolist())
#print(df['eco'].value_counts().head(10))

df['opening_name'] = df['eco'].str.split('/openings/').str[-1].str.replace('-', ' ')
print(f'The top 10 used chess openings for {username} are: ')
print(df['opening_name'].value_counts().head(10))

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


#Matplotlib Implementation
#Bar Chart of wins, losses and draws
plt.figure()
plt.bar(['Wins', 'Losses', 'Draws'], [win, loss, draw], color=['g','r', 'gray'])
plt.title(f"{username}'s Win-Loss-Draw Record")
plt.xlabel('Result')
plt.ylabel('Number of Games')
plt.savefig('win_loss_draw.png')
plt.show()

#Pie chart of winrate
plt.figure()
plt.pie([w_win, b_win], labels=['White Win Rate', 'Black Win Rate'], colors=['g', 'r'], autopct='%1.1f%%')
plt.title(f"{username}'s White-Black Win Rate")
plt.savefig('white_black_rate.png')
plt.show()


#Game Type Tracker & Analysis
game_type = {
    "rapid": 0,
    "blitz": 0,
    "bullet": 0,
    "daily": 0
}

for games in all_games:
    if games['time_class'] == 'rapid':
        game_type['rapid'] += 1
    elif games['time_class'] == 'blitz':
        game_type['blitz'] += 1
    elif games['time_class'] == 'bullet':
        game_type['bullet'] += 1
    else:
        game_type['daily'] += 1    



print()
print(f"The most played game type is {max(game_type, key=game_type.get)}")
print()

#Winner Predictions
#print(all_games[0]['white'])
white_ratings = []
black_ratings = []
results = []

for games in all_games:
    if games['white']['username'].lower() == username.lower():
        white_ratings.append(games['white']['rating'])
        black_ratings.append(games['black']['rating'])
        if games['white']['result'] == 'win':
            results.append(1)
        else:
            results.append(0)

rating_diff = np. array(white_ratings) - np.array(black_ratings)

x = rating_diff.reshape(-1,1)
y = np.array(results)

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.2, random_state = 42)

model = LogisticRegression()
model.fit(x_train, y_train)

y_pred = model.predict(x_test)
model_accuracy = accuracy_score(y_test, y_pred)
print(f"\nModel Accuracy: {model_accuracy*100:.2f}%")



#Predict outcome given rating difference
#Get player most recent rating
for game in reversed(all_games):
    if game['white']['username'].lower() == username.lower():
        player_rating = game['white']['rating']
        break
    elif game['black']['username'].lower() == username.lower():
        player_rating = game['black']['rating']
        break

print(f"\n{username}'s current rating: {player_rating}")

opp_rating = int(input(f"\nEnter your rating to see if you would beat {username}: "))
diff = np.array([[player_rating - opp_rating]])
prediction = model.predict(diff)

if prediction[0] == 1:
    print(f"Prediction: {username} will win!")
else:
    print(f"Prediction: {username} will lose!")
    