#!/usr/bin/env python
import config, debrid, memes, tv_movies, puzzle, chatbot, wiki, insult
import datetime, random, requests, json, loki, db
import discord
import asyncio, subprocess
from bs4 import BeautifulSoup
from hurry.filesize import size

#define discord client
client = discord.Client()

@client.event
async def on_ready():
    log_channel = client.get_channel(config.log_channel)
    loki.log('info', 'on_ready()', f"Logged in as {client.user.name}")
    await log_channel.send("[BOT ACTIVATED]")

waffle_emoji = '\N{WAFFLE}'
#define commands
wordlist_recs = ["!addrec", "!getrec", "!addalias"]
wordlist_animal = ["!cat", "!catgif", "!neb", '!catfact', '!dog']
wordlist_dogs = ['!dog']
wordlist_debrid = ["!search", "!status", '!lstatus', '!unlock ']
wordlist_waffle = ["!waffle", f"!{waffle_emoji}", f"!{':w:'}", "!chat", "!gpt", "!gptprompt"]
wordlist_search = ["!wiki", "!movie", "!tv"]
wordlist_insult = ["!insult", "!comp"]
wordlist_weather = ["!weather"]
wordlist_help = ['!help']
wordlist_system = ["!restartbot", "!git-update", "!media", "!users"]
wordlist_imgs = ['!meme', '!curse', '!funny', '!cute', '!osha', '!badfood', '!schad', '!gif', '!rassle']
wordlist_puzzle = ['!prompt', '!setprompt']
not_ready_magnets = []

list_roles_system = ['967697785304526879']

string_restartdiscord = "Restarting myself..."
string_updatebot = "Pulling from git and restarting..."
string_no_restart= "Ask an adult for permission."

async def update_debrid_status(): # log this stuff
    await client.wait_until_ready()
    while not client.is_closed():
        if len(not_ready_magnets) > 0:
            for magnet in not_ready_magnets:
                status = debrid.get_status(magnet_id=magnet)
                if status == 'ready':
                    filez = debrid.build_link_info(magnet)
                    em_links = discord.Embed()
                    for info in filez:
                        em_links.add_field(name=info["name"],value=f"{info['link']} | size: {info['size']}",inline=False)
                    dl_channel = client.get_channel(config.dl_channel)
                    not_ready_magnets.remove(magnet)
                    await dl_channel.send(embed=em_links)
                elif status == 404:
                    not_ready_magnets.remove(magnet)
        await asyncio.sleep(10)

@client.event
async def on_message(message):
    log_channel = client.get_channel(config.log_channel)
    if message.author == client.user: #Don't respond to my own messages
        return

    em_footer = f"{message.author} | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}" #default embed footer

# gpt chat
    if message.content.startswith('@waffle') or client.user.mention in message.content:
        loki.log('info', 'bot.on_message', f"{message.author}: {message.content}")
        input = message.content.split(maxsplit=1)[1]
        response = chatbot.get_response(input).strip()
        if response.startswith("Waffle: "):
            response = response.split(maxsplit=1)[1]
        if "Human:" in response:
            index = response.find("Human:")
            await message.channel.send(response[:index])
        else:
            await message.channel.send(response)
    if message.content.startswith("!gpt"):
        input = message.content.split(maxsplit=1)[1]
        response = chatbot.chat_response(input).strip()
        await message.channel.send(response)
    if message.content.startswith('!chatprompt'):
        chatbot.set_prompt(message.content.split(maxsplit=1)[1])
# memes
    if any(message.content.startswith(word) for word in wordlist_imgs):
        await message.channel.send(db.meme_db(message.content[1:]))

# insults/compliments
    if any(message.content.startswith(word) for word in wordlist_insult):
        if message.content.startswith("!insult"):
            loki.log('info', 'bot.insult', f"{message.author} is insulting {message.content[8:]}.")
            await message.channel.send(insult.insult(message.content[8:]))
        if message.content.startswith("!comp"):
            loki.log('info', 'bot.comp', f"{message.author} is complimenting {message.content[8:]}.")
            await message.channel.send(insult.compliment(message.content[6:]))

# system commands
    if any(message.content.startswith(word) for word in wordlist_system):
        loki.log('info', 'bot.on_message', f"{message.author}: {message.content}")
        valid_group = 0
        loki.log('info', 'bot.system', f"{message.author} has invoked a system command.")
        for role in message.author.roles:
                if str(role.id) in list_roles_system: #Needed role to restart shit
                    valid_group = 1
        if valid_group == 1:
            if message.content.startswith('!restartbot'):
                loki.log('info', 'bot.system', f"Restarting bot.")
                await log_channel.send(string_restartdiscord)
                subprocess.run('/waffle/scripts/restart.sh', shell=True)
            elif message.content.startswith('!users'):
                users = db.get_users()
                await message.channel.send(f"```{users}```")
            elif message.content.startswith('!media'):
                media = db.get_media()
                await message.channel.send(f"```{media}```")
            elif message.content.startswith('!git-update'):
                loki.log('info', 'bot.system', f"Pulling from git and then restarting.")
                await log_channel.send(string_updatebot)
                subprocess.run('/waffle/scripts/update.sh', shell=True)
        else:
            loki.log('warning', 'bot.system', f"{message.author} isn't auth'd for system commands.")
            await message.channel.send(string_no_restart)
# debrid
    if any(message.content.startswith(word) for word in wordlist_debrid):
        loki.log('info', 'bot.on_message', f"{message.author}: {message.content}")
        if message.content.startswith('!status'):
            magnet_status = debrid.get_status(all = True)
            if len(magnet_status['magnets']) > 0:
                em_status = discord.Embed()
                em_status.set_footer(text=em_footer)
                for magnet in magnet_status['magnets']:
                    if magnet['downloaded'] <= 0:
                        percent = 0
                    else:
                        percent = f"{'{0:.2f}'.format(100 * magnet['downloaded'] / magnet['size'])}"               
                    em_status.add_field(name=magnet['filename'], value=f"{percent}% | {magnet['status']} | Size: {size(magnet['size'])} | Speed: {size(magnet['downloadSpeed'])} | Seeders: {magnet['seeders']}", inline=False)
                await message.channel.send(embed=em_status)
            else:
                await message.channel.send('No active torrents, bud.')
        if message.content.startswith('!search'):
            results = debrid.search1337(message.content[8:])['items'][:5]
            if len(results) > 0:
                em_result = discord.Embed()
                em_result.set_footer(text=em_footer)
                x=1
                for torrent in results:
                    result_name = torrent["name"]
                    result_value = f"Seeders: {torrent['seeders']} | Leechers: {torrent['leechers']} | Size: {torrent['size']}"
                    em_result.add_field(name=f"{x}. {result_name}", value=result_value, inline=False)
                    x = x + 1
                em_result.add_field(name="----------------",value="You should pick the one with the most seeders and a reasonable filesize. Pay attention to the quality. You dont want a cam or TS.\n*!pick 1-5*",inline=False,)
                await message.channel.send(embed=em_result)

                def check(m):
                    return m.author == message.author and m.content.startswith("!pick")
                try:
                    msg = await client.wait_for("message", check=check, timeout=60)
                    pick = int(msg.content[6:])-1
                    if int(msg.content[6:]) > 5 or pick < 0:
                        await message.channel.send("WRONG")
                    else:
                        magnet_link = debrid.magnet_info(results[pick]["torrentId"])
                        ready_bool, name, magnet_id = debrid.add_magnet(magnet_link)
                        if ready_bool:
                            filez = debrid.build_link_info(magnet_id)
                            em_links = discord.Embed(description=f"{message.author.mention}")
                            em_links.set_footer(text=em_footer)
                            for info in filez:
                                em_links.add_field(name=info["name"],value=f"{info['link']} | size: {info['size']}",inline=False)
                            dl_channel = client.get_channel(config.dl_channel)
                            await dl_channel.send(embed=em_links)
                        else:
                            not_ready_magnets.append(magnet_id)
                            await message.channel.send("It aint ready. Try !status.")
                except asyncio.TimeoutError:
                    await message.channel.send("TOO SLOW")

            else:
                await message.channel.send("zero zero zero sesam street sesam street zero zero zero")
        if message.content.startswith('!unlock'):
            link = debrid.unlock_link(message.content[8:])
            await message.channel.send(link)

client.run(config.discord_bot_token)