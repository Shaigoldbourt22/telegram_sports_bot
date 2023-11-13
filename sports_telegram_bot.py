
import telebot
import requests

# a ListNode class for the cache
class ListNode:

    def __init__(self, value = -1, prev=None, next=None):
        self.next = next
        self.prev = prev
        self.value = value


# LRU Cache class to keep users who recently sent a massage
class Cache:

    def __init__(self):
        self.capacity = 10
        self.linked_list_head = ListNode()  # head_dummy
        self.linked_list_tail = self.linked_list_head
        self.linked_list_tail = self.linked_list_tail
        self.key_to_value = {}
        self.key_to_node = {}
        self.size = 0

    def get_value(self, key: int) -> dict:
        if key not in self.key_to_value:  # key is not in the dict
            return -1

        else:  # key is in the dict, move the node to the end of the linked list
            self.remove_from_linked_list_and_update_value(key, self.key_to_value[key])
            self.add_to_linked_list_and_update_node(key, self.key_to_value[key])


            return self.key_to_value[key]

    def put_or_update(self, key: int, value: dict) -> None:

        # remove the node from the list if the key is in the dict
        if key in self.key_to_value:
            self.remove_from_linked_list_and_update_value(key, value)

        # add the key if not in the dict
        else:
            self.size += 1
            self.key_to_value[key] = value

        # create the new node and add to the end of the list
        self.add_to_linked_list_and_update_node(key, value)

        # remove the first node from the linked list if the size is bigger than the capacity
        if self.size > self.capacity:
            node_to_remove = self.linked_list_head.next
            self.key_to_value.pop(node_to_remove.value)
            self.key_to_node.pop(node_to_remove.value)

            self.linked_list_head.next = node_to_remove.next

            if node_to_remove.next:
                node_to_remove.next.prev = self.linked_list_head

            else:  # node_to_remove wat the tail
                self.linked_list_tail = self.linked_list_head

    def remove_from_linked_list_and_update_value(self, key: str, value: dict) -> None:
        self.key_to_value[key] = value
        node = self.key_to_node[key]
        node.prev.next = node.next

        if node.next:
            node.next.prev = node.prev

        else:  # node is the tail
            self.linked_list_tail = node.prev

    def add_to_linked_list_and_update_node(self, key: str, value: dict) -> None:
        new_node = ListNode(key)
        self.linked_list_tail.next = new_node
        new_node.prev = self.linked_list_tail
        self.key_to_node[key] = new_node
        self.linked_list_tail = new_node


# telegram api info
telegram_token = "6840332720:AAH3TnoPdotUZEanvXK4Simz9hYwDSrBV5s"
bot = telebot.TeleBot(telegram_token)

# football api info, using "https://www.thesportsdb.com/api.php"
football_api_key = "3"  

# basketball api info, using "https://www.balldontlie.io/home.html#get-all-players"
basketball_url = "https://www.balldontlie.io/api/v1/players"

# basketball functions
def get_nba_player_team(player_name: str) -> str:  # # gets a player's name, and return his team
    params = {"page": 0, "per_page": 1, "search": player_name}
    response = requests.get(basketball_url, params)
    player_data = response.json()

    if player_data and player_data["data"]:
        player_team = player_data["data"][0]["team"]["full_name"]
        return player_team

    return "could not find the player"

# football functions:
def get_footballer_team(player_name: str) -> str:  # gets a player's name, and return his team

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
user_to_state = Cache()

# handle a massage to the telegram bot:
@bot.message_handler(func=lambda message: True) 
def handle_message(message):
   
    user_id = message.from_user.id
    if user_to_state.get_value(user_id) == -1:  # user is not in the cache
        user_to_state.put_or_update(user_id, {"is_sent_welcome": False, "is_chosen_football": False, "is_chosen_basketball": False})
    
    answer = message.text

    if not user_to_state.get_value(user_id)["is_sent_welcome"]:  # need to send a weolcome message
        bot.reply_to(message, "hello! please choose the sport you're intrested in: football or basketball")
        user_to_state.put_or_update(user_id, {"is_sent_welcome": True, "is_chosen_football": False, "is_chosen_basketball": False})

    elif answer == "football":  # the user chose football
        bot.reply_to(message, "please provide a footballer's name, and i will provide his team")
        user_to_state.put_or_update(user_id, {"is_sent_welcome": True, "is_chosen_football": True, "is_chosen_basketball": False})
    
    elif answer == "basketball":  # the user chose basketball
        bot.reply_to(message, "please provide a nba player's name, and i will provide his team")
        user_to_state.put_or_update(user_id, {"is_sent_welcome": True, "is_chosen_football": False, "is_chosen_basketball": True})
        
    elif user_to_state.get_value(user_id)["is_chosen_football"]:   # the user is sending a footballer's name 
        reply = get_footballer_team(answer)
        bot.reply_to(message, reply)
    
    elif user_to_state.get_value(user_id)["is_chosen_basketball"]:   # the user is sending a nba player's name 
        reply = get_nba_player_team(answer)
        bot.reply_to(message, reply)


def get_footballer_team_test(input: str, expceted_output: str):
    # arrange:
    # nothing to do here

    # act:
    res = get_footballer_team(input).lower()
    
    # assert:
    assert res == expceted_output, "problem with input " + input + ", got " + res + ", expected " + expceted_output

get_footballer_team_test("messi", "inter miami")


def get_nba_player_team_test(input: str, expceted_output: str):
    # arrange:
    # nothing to do here

    # act:
    res = get_nba_player_team(input).lower()
    
    # assert:
    assert res == expceted_output, "problem with input " + input + ", got " + res + ", expected " + expceted_output

get_nba_player_team_test("lebron", "los angeles lakers")

# keep the bot running
if __name__ == '__main__':
    bot.polling(none_stop=True)
