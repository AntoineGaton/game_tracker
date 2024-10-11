# main.py

import requests
from models import Game, session
from config import STEAM_API_KEY, STEAM_USER_ID
from hltbapi import HtmlScraper

# Function to fetch the games from the Steam API
def get_owned_games():
   print('fetching games from Steam API...')
   # URL to fetch the games from the Steam API
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

# Function to display games by status
def display_games():
   statuses = ['Backlog', 'Playing', 'Done']
   
   for status in statuses:
      print(f"\nGames in {status}:")
      games = session.query(Game).filter_by(status=status).all()
      for game in games:
         print(f"{game.title} ({game.hours_played:.2f} hours played)")

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

# Main menu for the command-line app
def main_menu():
   while True:
      print("\n1. Sync games from Steam")
      print("2. Display games by status")
      print("3. Update game status")
      print("4. Exit")
      
      choice = input("Choose an option: ")
      
      if choice == '1':
         sync_games()
         print("Games synced from Steam!")
      elif choice == '2':
         display_games()
      elif choice == '3':
         update_game_status()
      elif choice == '4':
         break
      else:
         print("Invalid choice, please try again.")

if __name__ == "__main__":
   main_menu()
