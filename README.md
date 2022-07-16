# tkbot

## Description
tkbot is a Discord bot to help keep track of [team kills](https://www.urbandictionary.com/define.php?term=team-kill) (tks) in games. 

## tkbot commands
All commands start with `!tk` 

### 1) Add a tk to a user that killed you
`!tk @user comment`

Use this command to report a team mate that killed you.

**Example:**

`!tk @Adam WATCH YOUR AIM`

![](/pics/add_tk.png)


---

### 2) Add a tk to another user
`!tk @killer @victim comment`

Use this command to report a team kill for another user.

**Example:**

`!tk @Madam @Adam Haha got you back`

![](/pics/add_tk_to_another.png)

---

### 3) Show leaderboard
`!tk leaderboard`

Displays the team kill leaderboard.

![](/pics/leaderboard.png)

---

### 4) Show user stats
`!tk stats @user`

Display team kill stats for a given user.

**Example:**

`!tk stats @Madam`

![](/pics/user_stats.png)

---

### 5) Reset a user's stats
`!tk reset @Adam`

Reset team kill stats for a given user.

![](/pics/stats_cleared.png)

---

### 6) Reset all user stats
`!tk reset ALL`

Deletes the entire file contents of db.txt

---

### 7) Manual database entry
`!tk input @killer @victim mm/dd/yy comment`

Use this command to enter a team kill that occured on a previous day. 

**Example:**

`!tk input @Madam @Adam 07/14/22 Try aiming better!`

![](/pics/manual_entry.png)

