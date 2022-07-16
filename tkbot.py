import os
import discord
from datetime import datetime
from table2ascii import table2ascii as t2a, PresetStyle
from operator import itemgetter
import json
from collections import Counter
import time
from random import choice

# read bot token
try:
  pass_file = open('bot_pass.txt')
except:
  print("ERROR: issue with bot_pass.txt")
  exit()
bot_pass = pass_file.readline()
bot_pass = bot_pass.strip()

client = discord.Client()

@client.event
async def on_ready():
  print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
  # ignore bot text
  if message.author == client.user:
    return

  # tk command issued from discord
  if message.content.startswith('!tk'):
    command = parse_command(message.content)
    total_ats = count_ats(command)
    
    # do action from command
    if 'reset' in command:
      if total_ats == 1:
        user = command.split(' ')[1]
        if '>' in user:
          user_id, user_id_str = get_user_id(command)
          user_obj = await client.fetch_user(user_id)
          user_name = user_obj.display_name

        error, user = reset_user_db(command, user_name)
        if error:
          await message.channel.send(error)
        else:
          await message.channel.send(f'{user} stats cleared')
      else:
        if 'ALL' in command:
          reset_all_db()
          await message.channel.send('db cleared')
    elif 'getdb' in command:
      str_db = get_db()
      await message.channel.send(str_db)
    elif 'help' in command:
      user_obj = await client.fetch_user(int(message.author.id))
      help = display_help()
      await user_obj.send(help)

    # command: !tk cound @user
    # get tk count of a given user
    elif 'count' in command:
      user = command.split(' ')[1]
      if '>' in user:
        user_id, user_id_str = get_user_id(command)
        user_obj = await client.fetch_user(user_id)
        user_name = user_obj.display_name

      total_tks = get_tk_count(user_name)
      bot_text = f"{user_id_str} - {total_tks} TKs Good Job"
      channel = client.get_channel(992114909850648607)
      await channel.send(bot_text)


    # command: !tk leaderboard
    elif 'leaderboard' in command:
      user_data = cal_leaderboard()
      leaderboard = display_leaderboard(user_data)
      channel = client.get_channel(992114909850648607)
      await channel.send(f"```\n{leaderboard}\n```")
    

    # command: !tk stats @user
    elif 'stats' in command:
      parts = command.split(' ')
      user = parts[1].strip()

      if '>' in user:
        user_id, user_id_str = get_user_id(command)
        user_obj = await client.fetch_user(user_id)
        user_name = user_obj.display_name
      else:
        user_name = user

      leaderboard_data = cal_leaderboard()
      victim_data = cal_top_victims()
      user_stats = display_user_stats(user_name, leaderboard_data, victim_data)
      comms = display_comments(user_name)
      channel = client.get_channel(992114909850648607)
      await channel.send(f"```\n{user_stats}\n```")
      await channel.send(f"```\n{comms}\n```")

    # command: !tk input @killer @victim date comment
    elif 'input' in command:
      parts = command.split(' ', 4)
      killer = parts[1]
      victim = parts[2]
      date = parts[3]
      #v_comment = parts[4]

      # get user ids
      killer_id, victim_id = get_user_ids(f"{killer} {victim}")  
        
      # look up user name from user id
      killer_obj = await client.fetch_user(killer_id[0])
      killer_user_name = killer_obj.display_name

      # look up user name from user id
      victim_obj = await client.fetch_user(victim_id[0])
      victim_user_name = victim_obj.display_name

      # replace user id with user name in command
      command = command.replace(killer_id[1], killer_user_name)
      command = command.replace(victim_id[1], victim_user_name)
        
      tk_data = add_tk_to_another_user_data(command)
      send_data_to_db(tk_data)
      bot_text = display_tk(f"{date};{tk_data['victim_comment']}", killer_id[1], victim_id[1])
      channel = client.get_channel(992114909850648607) # tk-tracking channel
      await channel.send(bot_text)

    # add user to tk database
    elif total_ats == 0:
      pass
      
    elif total_ats == 1:
      
      # command: !tk @user start writing comment
      if '<' in command:
        # get user ids
        user_id, user_id_str = get_user_id(command)

        # look up user name from user id
        killer_obj = await client.fetch_user(user_id)
        killer_user_name = killer_obj.display_name

        # replace user id with user name in command
        command = command.replace(user_id_str, killer_user_name)
      
      tk_data = add_tk_to_user_data(command, message.author.name)
      send_data_to_db(tk_data)
      victim_id = f"<@{message.author.id}>"
      bot_text = display_tk(tk_data['victim_comment'], user_id_str, victim_id)

      bot_string = congradulate(user_id_str)

      channel = client.get_channel(992114909850648607)
      await channel.send(bot_text)

      # congradulate the TK'er
      time.sleep(8)
      await channel.send(bot_string)

    # command: !tk @killerUser @victimUser comment
    elif total_ats == 2:
      if '<' in command:
        # get user ids
        killer_id, victim_id = get_user_ids(command)  
        
        # look up user name from user id
        killer_obj = await client.fetch_user(killer_id[0])
        killer_user_name = killer_obj.display_name

        # look up user name from user id
        victim_obj = await client.fetch_user(victim_id[0])
        victim_user_name = victim_obj.display_name

        # replace user id with user name in command
        command = command.replace(killer_id[1], killer_user_name)
        command = command.replace(victim_id[1], victim_user_name)
        
      tk_data = add_tk_to_another_user_data(command)
      send_data_to_db(tk_data)
      bot_text = display_tk(tk_data['victim_comment'], killer_id[1], victim_id[1])
      channel = client.get_channel(992114909850648607) # tk-tracking channel
      await channel.send(bot_text)

def parse_command(command):
  """removes string !tk and leaves only the command

  Parameters:
  -----------
  command : str
    command from discord
  
  Returns:
  --------
  command : str
    user supplied command
  """

  command = command.replace('!tk', '')
  command = command.strip()
  
  return command

def count_ats(command):
  total_ats = 0
  for letter in command:
    if letter == '@':
      total_ats = total_ats + 1

  return total_ats

def add_tk_to_user_data(command, victim):
  """create tk dict from discord text

  Parameters:
  -----------
  command : str
    tk command from discord
  victim : str
    discord author

  Returns:
  --------
  tk_data : dict
    tk data from discord
  """
  parts = command.split(' ', 1)
  killer = parts[0]
  killer = killer.replace('@','')
  victim_comment = parts[1]
  today_date = datetime.now().strftime('%m/%d/%y')

  # build tk dict
  tk_data = {}
  tk_data['killer'] = killer
  tk_data['victim'] = victim
  tk_data['victim_comment'] = victim_comment
  tk_data['date'] = today_date

  return tk_data

def add_tk_to_another_user_data(command):
  """create tk dict from discord text

  Parameters:
  -----------
  command : str
    tk command from discord
  victim : str
    discord author

  Returns:
  --------
  tk_data : dict
    tk data from discord
  
  """

  # build tk dict
  
  if 'input' in command:
    parts = command.split(' ', 4)
    killer = parts[1]
    killer = killer.replace('@','')
    victim = parts[2]
    today_date = parts[3]
    victim_comment = parts[4]

  
  else:
    parts = command.split(' ', 2)
    killer = parts[0]
    killer = killer.replace('@','')
    victim = parts[1]
    victim_comment = parts[2]
    today_date = datetime.now().strftime('%m/%d/%y')

  tk_data = {}
  tk_data['date'] = today_date
  tk_data['killer'] = killer
  tk_data['victim'] = victim
  tk_data['victim_comment'] = victim_comment
    
  return tk_data

def new_tk_user_data(tk_data):
  """create new user in db

  Parameters:
  -----------
  tk_data : dict
    tk data from discord
  """
  
  user = tk_data['killer']
  # build new user db
  data = {'total_tks' : 0, 't_kills' : [], 'v_comments' : []}

  # read current db
  db_file = open('db.txt', 'r')
  db = db_file.read()
  try:
    db = eval(db)
  except:
    # new file no data yet
    db = {}
  db_file.close()

  db[user] = data

  # write new data in db
  db_file = open('db.txt', 'w')
  json.dump(db, db_file)
  db_file.close()
  #db[user] = data

def store_tk_data(tk_data):
  """add tk data to the db

  Parameters:
  -----------
  tk_data : dict
    tk data from discord
  """
  user =  tk_data['killer']
  victim = tk_data['victim']
  v_comment = tk_data['victim_comment']
  date = tk_data['date'] # user reported date
  
  # read current user data
  db = read_db()
  user_data = db[user]

  # update total kills
  total_tks = user_data['total_tks']
  total_tks = total_tks + 1
  
  # update victim killed
  tks = user_data['t_kills']
  tks.append(victim)

  # update victim comment
  comments = user_data['v_comments']
  comments.append(f"{date};{v_comment}")

  # update user data in db
  db_file = open('db.txt', 'w')
  data = {'total_tks' : total_tks, 't_kills' : tks, 'v_comments' : comments} 
  db[user] = data
  json.dump(db, db_file) # write
  db_file.close()
  #db[user] = data

def is_user(user):
  """returns true if user exists in the db

  Parameters:
  -----------
  user : str
    the user's discord name

  Returns:
  --------
  user_exists : bool
    true if the user exists in the db
  """
  db_file = open('db.txt', 'r')
  db = db_file.read()
  try:
    db = eval(db)
  except:
    # no data in db.txt causes and error
    return False

  user_exists = False
  keys = db.keys()
  if user in keys:
    user_exists = True
  
  db_file.close()
  return user_exists
               
def send_data_to_db(tk_data):
  """handles saving data to the db
  
  Parameters:
  -----------
  tk_data : dict
    tk data from discord
  """
  user_exists = None
  user_exists = is_user(tk_data['killer'])

  if user_exists == False:
    new_tk_user_data(tk_data)
  
  store_tk_data(tk_data)

def get_db():
  """dump db into a string 

  Returns:
  --------
  str_db  : str
    db contents
  """
  db = read_db()

  keys = db.keys()
  str_db = ""
  for key in keys:
    #print(f"{db[key]}")
    str_db = str_db + f"{key} - {db[key]}\n"

  return str_db

def reset_all_db():
  """clears the db
  """
  
  db_file = open('db.txt', 'w')
  db_file.write('')
  db_file.close()

  print("db cleared")
  
def reset_user_db(command, user_name):
  """rest the tk stats for a given user

  Parameters:
  -----------
  command : str
    the discord command

  Returns:
  --------
  error : str
    error message if user does not exist in db
  """
  '''
  parts = command.split(' ')
  user = parts[1]
  user = user.replace('@', '')
  '''
  user_exists = is_user(user_name)
  
  error = None
  if user_exists:
    data = {'total_tks' : 0, 't_kills' : []}
    db = read_db()
    db[user_name] = data

    db_file = open('db.txt', 'w')
    json.dump(db, db_file)
    db_file.close()

  else:
    error = f"ERROR: user {user_name} not found in db"

  return error, user_name
  
def get_user_id(command):
  """parses the user_id from the discord command

  Parameters:
  -----------
  command : str
    command from discord

  Returns:
  --------
  user_name : int
    discord user id
  """
  
  parts = command.split(' ')
  user_id_str = parts[0]
  
  user_id = user_id_str.replace('@','')
  user_id = user_id.replace('<','')
  user_id = user_id.replace('>','')

  try:
    int(user_id)
  except:
    user_id_str = parts[1]
  
    user_id = user_id_str.replace('@','')
    user_id = user_id.replace('<','')
    user_id = user_id.replace('>','')
  
  return int(user_id), user_id_str

def get_user_ids(command):
  """parses two user_ids from the discord command

  Parameters:
  -----------
  command : str
    command from discord

  Returns:
  --------
  killer_list : list
    user id and user id string
  victim_list : list
    user id and user id string
  """
  
  parts = command.split(' ', 2)
  killer_id_str = parts[0]
  victim_id_str = parts[1]

  killer_id = killer_id_str.replace('@','')
  killer_id = killer_id.replace('<','')
  killer_id = killer_id.replace('>','')

  victim_id = victim_id_str.replace('@','')
  victim_id = victim_id.replace('<','')
  victim_id = victim_id.replace('>','')

  killer_list = [int(killer_id), killer_id_str]
  victim_list = [int(victim_id), victim_id_str]
  
  return killer_list, victim_list

def display_tk(comment, killer_id, victim_id):
  """bot text annouce tk kill

  Parameters:
  -----------
  comment : str
    victim comment
  killer_id : str
    full discord user id to mention
  victim_id : str
    full discord user id to mention

  Returns:
  --------
  bot_text : str
    tk annoucement
  """
  
  today_date = datetime.now().strftime('%m/%d')

  count_f_slash = 0
  for letter in comment:
    if letter == '/':
      count_f_slash = count_f_slash + 1
  

  if count_f_slash == 2:
    parts = comment.split(';')
    date = parts[0]
    today_date = date
    year = datetime.now().strftime('%y')
    today_date = today_date.replace(f"/{year}", '')
    comment = comment.replace(today_date, '')
    comment = comment.replace(';', '')

  bot_text = f"{today_date} {killer_id} TK'd {victim_id} {comment}"
  
  return bot_text

def congradulate(user_id_str):
  """reads in congradulate.txt and picks a random phrase

  Parameters:
  -----------
  user_id_str : str
    discord user id
  
  Returns:
  --------
  bot_string : str
    bot's words of congrats
  """
  
  f = open('congradulate.txt', 'r')
  statements = f.readlines()
  rand_line = choice(statements)
  parts = rand_line.split(' ', 1)
  bot_words = parts[1]
  
  bot_string = f"{user_id_str} w/ Another Tk, {bot_words}"

  return bot_string

def display_help():
  """bot commands help page

  Returns:
  --------
  string : str
    bot help
  """
  
  string = """TKbot Commands:
  Add a TK to a user that killed you:
  !tk @user comment

  Add a TK to another user:
  !tk @killer @victim comment

  Show leaderboard:
  !tk leaderboard

  Show user stats:
  !tk stats @user

  Reset a user's stats:
  !tk reset @user

  Reset all user stats
  !tk reset ALL

  Manual database entry:
  !tk input @killer @victim mm/dd/yy comment
  """

  return string

def get_tk_count(user):
  """get total tks from db

  Parameters:
  -----------
  user : str
    user name in db

  Returns:
  ---------
  total_tks : int
    total team kills
  """
  
  db = read_db()

  tk_data = db[user]
  total_tks = tk_data['total_tks']

  return total_tks

def cal_leaderboard():
  """calculate leaderboard for most tks

  Returns:
  --------
  user_data : list
    a list with user and number of tks
  """

  db = read_db()
  
  users_data = []
  keys = db.keys()

  for key in keys:
    num_tks = db[key]['total_tks']
    data = [key, num_tks]
    users_data.append(data)

  # sort greatest to least tks
  users_data = (sorted(users_data, key=itemgetter(1), reverse=True))

  return users_data

def display_leaderboard(stats):
  """builds leaderboard table

  Parameters:
  stats : list
    user and tk stats

  Returns:
  --------
  output : str
    ascii table
  """
  
  data = []
  # format data for table
  for index, user in enumerate(stats, start=1):
    user_name = user[0]
    num_tks = user[1]
    data.append([index, user_name, num_tks])

  # make ascii table
  output = t2a(
    header=["Rank", "Player", "Total TKs"],
    body=data,
    #style=PresetStyle.thin_compact
  )

  return output

def cal_top_victims():
  db = read_db()

  users_data = []
  keys = db.keys()

  for key in keys:
    victims = db[key]['t_kills']
    victim_dict = Counter(victims)
    users_data.append([key, victim_dict])
  
  return users_data

def display_user_stats(user, leaderboard_data, victim_data):
  """Generate user stats information to be displayed in discord

  Parameters:
  -----------
  user : str
    the user to display their stats
  leaderboard_data : list
    leaderboard stats of all users
  victim_data : list
    all players killed by the given user

  Returns:
  --------
  output : str
    ascii table with user stats
  """
  
  for index, data in enumerate(leaderboard_data, start=1):
    user_name = data[0]
    if user_name == user:
      num_tks = data[1]
      rank = index

  for item in victim_data:
    user_name = item[0]

    if user_name == user:
      vicitms_dict = item[1]
      victims = vicitms_dict.keys()
      
      vcitims_string = ""
      for victim in victims:
        total_deaths = vicitms_dict[victim]
        vcitims_string = vcitims_string + f"{victim} - {total_deaths}\n"

  data = [[rank, user, num_tks, vcitims_string]]
  # make ascii table
  output = t2a(
    header=["Rank", "Player", "Total Team Kills", 'Victims'],
    body=data,
    #style=PresetStyle.thin_compact
  )

  return output

def display_comments(user):
  """Format and return all comments for a given user

  Parameters:
  -----------
  user : str
    user to display comments
  
  Returns:
  --------
  com_string : str
    all comments for a given user
  """
  
  db = read_db()

  com_string = ""
  comments = db[user]['v_comments']
  this_year = datetime.now().strftime('%y')
  this_year = f"/{this_year}"
  for comment in comments:
    parts = comment.split(';')
    date = parts[0]
    comm = parts[1]
    if this_year in date:
      date = date.replace(this_year, '')

    com_string = com_string + f"\n{date} - {comm}"
  
  return com_string

def read_db():
  """read in the dict from the database

  Returns:
  --------
  db : dict
    the database

  """
  
  db_file = open('db.txt', 'r')
  db = db_file.read()
  db = eval(db)
  db_file.close()

  return db

client.run(bot_pass)

