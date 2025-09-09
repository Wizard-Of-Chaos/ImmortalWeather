# Gargoyle
> The CIC brass can't stand these guys because they upload staggering quantities of useless information to the database, on the off chance that some of it will eventually be useful. It's like writing down the license number of every car you see on your way to work each morning, just in case one of them will be involved in a hit-and-run accident. Even the CIC database can only hold so much garbage. So, usually, these habitual gargoyles get kicked out of the CIC before too long.

> This guy hasn't been kicked out yet. And to judge from the quality of his equipment - which is very expensive - he's been at it for a while. So he must be pretty good.
## What does it do?
Gargoyle's original purpose was to track idiots in Dota 2 pubs so I could avoid them. At present, the `subman` module is disabled because of Valve's shitty attitude toward Dota 2 replays.

Gargoyle's current purpose is Deadlock stats as well as storing easy dinner recipes. There may be additional cogs added in the future for other stats. A module is currently planned that will provide an update on the lime tree on my deck, as well as an update on my bird feeder.
## Necessary commands for Steam integration
- `/register [steam_id]`: Registers your current Discord ID to your Steam ID. This is the Steam ID3, accessible via `/steam_id3` if you're too stupid to figure it out, and is a prerequisite for any Deadlock or Dota 2 module tracking your personal stats.
- `/unregister`: Unregisters your Steam ID from your Discord ID.
- `/steam_id3 [profile_link]`: Gets your Steam ID3 based off a link to your profile.

## Deadlock commands
### NOTE: this uses the [Deadlock API here](https://api.deadlock-api.com) which is prone to all kinds of issues, since the game's still in Alpha. Be patient with it.
- `/deadlock lm`: Gets your most recent match and spits out a digest of your stats and your inventory. Requires registration with `/register`.
- `/deadlock blame`: Finds out who the idiot was in your most recent lane. Requires registration with `/register`.
- `/deadlock herostats [hero_name]`: Gets a stat digest based on the hero. Requires registration with `/register`.
- `/deadlock courage`: Gets a randomly-generated build + hero. Are *you* a bad enough dude to build it?
- `/deadlock meta-roulette [hero_name]`: Gets a random Eternus match digest including the given hero. Meant to get an idea of current top-tier meta, and also find the occasional schizo.

## General commands
- `/dinner`: Dinner suggestion.
- `/universal_spice`: Many recipes refer to the universal spice, which you can be reminded of here.
- `/contribute`: Link the GitHub of Gargoyle.

## Subman commands
Currently nonexistent, pending a rework of the subman aspect of the bot to track idiots in pubs. Valve's API has changed; the bot has not changed with it to account for the fact that half the god damn matches are now hidden.
