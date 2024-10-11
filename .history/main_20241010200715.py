# main.py
'''
To Do:
- implement getting data from hltbapi to calculate percentage of completion
- make this app have a cli window
- convert this app to django app
- save game data to csv file to be able to load it later
- add a way to export the data to a csv file to view in excel
- 
'''
import requests
import os
from models import Game, session
from config import STEAM_API_KEY, STEAM_USER_ID
from hltbapi import HtmlScraper
import urllib.error

# Function to fetch the games from the Steam API
def get_owned_games():
   print('fetching games from Steam API...')
   
   url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={STEAM_API_KEY}&steamid={STEAM_USER_ID}&format=json&include_appinfo=true"
   response = requests.get(url)
   data = response.json()
   print('data received: ', data)
   return data['response']['games'] if 'games' in data['response'] else []

# Function to sync games with the PostgreSQL database
def sync_games():
   games_data = get_owned_games()
   print('games data received: ', games_data)
   for game_data in games_data:
      steam_id = game_data['appid']
      title = game_data.get('name', 'Unknown')
      hours_played = game_data['playtime_forever'] / 60  # Convert from minutes to hours
      
      # Check if the game already exists in the database
      game = session.query(Game).filter_by(steam_id=steam_id).first()
      if game:
         # Update hours played if the game exists
         game.hours_played = hours_played
      else:
         # Add new game to the database
         new_game = Game(steam_id=steam_id, title=title, hours_played=hours_played)
         session.add(new_game)
   
   # Commit the changes to the database
   session.commit()
   print('Games synced to the database!')
   
def add_new_game():
   print('adding new game to the database...')
   steam_id = input('Enter the Steam ID of the game: ')
   hours_played = float(input('Enter the hours played: '))
   status = input('Enter the status of the game (Backlog, Playing, Done): ').capitalize()
   last_played = input('Enter the last played date (YYYY-MM-DD): ')
   new_game = Game(steam_id=steam_id, title=title, hours_played=hours_played, status=status, last_played=last_played)
   session.add(new_game)
   session.commit()
   print('Game added to the database!')

# Function to display games by status
def display_games():
   while True:
      print("\nDisplay Games Menu:")
      print("1. All Games")
      print("2. Games by Status")
      print("3. Back to Main Menu")
      
      choice = input("Choose an option: ")
      
      if choice == '1':
         display_all_games()
      elif choice == '2':
         display_games_by_status()
      elif choice == '3':
         break
      else:
         print("Invalid choice, please try again.")

def display_all_games():
   games = session.query(Game).order_by(Game.title).all()
   paginate_games(games, "All Games")

def display_games_by_status():
   status = input("Enter status (Backlog, Playing, Done): ").capitalize()
   if status not in ['Backlog', 'Playing', 'Done']:
      print("Invalid status!")
      return
   games = session.query(Game).filter_by(status=status).order_by(Game.title).all()
   paginate_games(games, f"Games in {status}")

def paginate_games(games, title):
   page = 0
   while True:
      start = page * 10
      end = start + 10
      current_games = games[start:end]
      
      if not current_games:
         print("End of list")
         break
      
      print(f"\n{title} (Page {page + 1}):")
      for game in current_games:
         print(f"{game.title} ({game.hours_played:.2f} hours played) - Status: {game.status}")
      
      user_input = input("Press Enter to see more games or 'q' to quit: ")
      if user_input.lower() == 'q':
         break
      page += 1

# Function to update the status of a game
def update_game_status():
   title = input("Enter the title of the game: ")
   game = session.query(Game).filter_by(title=title).first()

   if game:
      print(f"Current status: {game.status}")
      new_status = input("Enter new status (Backlog, Playing, Done): ").capitalize()

      if new_status in ['Backlog', 'Playing', 'Done']:
         game.status = new_status
         session.commit()
         print(f"Status of {game.title} updated to {new_status}")
      else:
         print("Invalid status!")
   else:
      print("Game not found!")

def how_long_to_beat():
   print('How Long To Beat search...')
   game_name = input("Enter the name of the game to search: ")
   
   try:
      res = HtmlScraper().search(name=game_name)
      
      if not res:
         print(f"No results found for '{game_name}'")
         print(f'error: {res}')
         print('--------------------------------')
         return
      
      for entry in res:
         print('===================================')
         print(f"Game: {entry.gameName}")
         print(f"Description: {entry.description}")
         print(f"Playable On: {', '.join(entry.playableOn)}")
         print(f"Main Story: {entry.gameplayMain} hours")
         print(f"Main + Extras: {entry.gameplayMainExtra} hours")
         print(f"Completionist: {entry.gameplayCompletionist} hours")
         print('===================================')
   
   except urllib.error.HTTPError as e:
      if e.code == 404:
         print(f"Error: The game '{game_name}' was not found on HowLongToBeat.")
      else:
         print(f"HTTP Error {e.code}: {e.reason}")
   except Exception as e:
      print(f"An error occurred: {str(e)}")

# Main menu for the command-line app
def main_menu():
   print('--------------------------------')
   print('Welcome to the Game Tracker')
   print('--------------------------------')
   while True:
      print("1. Sync games from Steam")
      print("2. Add a new game")
      print("3. Display games by status")
      print("4. Update game status")
      print("5. How long to beat(TESTING)")
      print("6. Exit")
      print('--------------------------------')
      choice = input("Choose an option: ")
      
      if choice == '1':
         sync_games()
         print("Games synced from Steam!")
      elif choice == '2':
         add_new_game()
      elif choice == '3':
         display_games()
      elif choice == '4':
         update_game_status()
      elif choice == '5':
         how_long_to_beat()
      elif choice == '6':
         os.system('cls')
         break
      else:
         print("Invalid choice, please try again.")

if __name__ == "__main__":
   main_menu()