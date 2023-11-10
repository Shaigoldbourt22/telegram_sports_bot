
import telebot
import requests

# telegram api info
telegram_token = "6840332720:AAH3TnoPdotUZEanvXK4Simz9hYwDSrBV5s"
bot = telebot.TeleBot(telegram_token)

# football api info, using "https://www.thesportsdb.com/api.php"
football_api_key = "3"  

# basketball api info, using "https://www.balldontlie.io/home.html#get-all-players"
basketball_url = "https://www.balldontlie.io/api/v1/players"

# basketball functions
def get_nba_player_team(player_name):  # # gets a player's name, and return his team
    params = {"page": 0, "per_page": 1, "search": player_name}
    response = requests.get(basketball_url, params)
    player_data = response.json()

    if player_data and player_data["data"]:
        player_team = player_data["data"][0]["team"]["full_name"]
        return player_team

    return "could not find the player"

# football functions:
def get_footballer_team(player_name):  # gets a player's name, and return his team

    # get the player's id first
    football_url = f"https://www.thesportsdb.com/api/v1/json/{football_api_key}/searchplayers.php?p={player_name}"  
    response = requests.get(football_url) 
    player_data = response.json()  
    
    # Check if the player exists
    if player_data and player_data["player"] and player_data["player"][0]["strSport"] == "Soccer":
        player_id = player_data["player"][0]["idPlayer"]

    else: 
        return "could not find the player"
    
    # find the player's team using his id
    player_url = f"https://www.thesportsdb.com/api/v1/json/{football_api_key}/lookupplayer.php?id={player_id}"
    response = requests.get(player_url)
    player_team_data = response.json()
    team_name = player_team_data["players"][0].get("strTeam")
    return team_name

# dict to map user_id to his current state
user_to_state = {}

# handle a massage to the telegram bot:
@bot.message_handler(func=lambda message: True) 
def handle_message(message):
   
    user_id = message.from_user.id
    if user_id not in user_to_state:
        user_to_state[user_id] = {"is_sent_welcome": False, "is_chosen_football": False, "is_chosen_basketball": False}
    
    answer = message.text

    if not user_to_state[user_id]["is_sent_welcome"]:  # need to send a weolcome message
        bot.reply_to(message, "hello! please choose the sport you're intrested in: football or basketball")
        user_to_state[user_id]["is_sent_welcome"] = True

    elif answer == "football":  # the user chose football
        bot.reply_to(message, "please provide a footballer's name, and i will provide his team")
        user_to_state[user_id]["is_chosen_football"] = True
        user_to_state[user_id]["is_chosen_basketball"] = False
    
    elif answer == "basketball":  # the user chose basketball
        bot.reply_to(message, "please provide a nba player's name, and i will provide his team")
        user_to_state[user_id]["is_chosen_basketball"] = True
        user_to_state[user_id]["is_chosen_football"] = False
        
    elif user_to_state[user_id]["is_chosen_football"]:   # the user is sending a footballer's name 
        reply = get_footballer_team(answer)
        bot.reply_to(message, reply)
    
    elif user_to_state[user_id]["is_chosen_basketball"]:   # the user is sending a nba player's name 
        reply = get_nba_player_team(answer)
        bot.reply_to(message, reply)

# keep the bot running
if __name__ == '__main__':
    bot.polling(none_stop=True)
