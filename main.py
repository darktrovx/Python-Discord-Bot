import os
import random

import discord
from dotenv import load_dotenv
from discord.ext import commands
from discord.ext.commands import CommandNotFound

# For our HTML calls.
from selenium import webdriver

# Import GeckoDriverManager module.
from webdriver_manager.firefox import GeckoDriverManager

# Used for wait handling.
import time

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

activity = discord.Activity(type=discord.ActivityType.listening, name="!help")
bot = commands.Bot(command_prefix='!', activity=activity, status=discord.Status.do_not_disturb)

wallpapers = []


# Get wallpapers from imgur.
async def get_wallpaper():
    # Install the GeckoDriverManager to run FireFox web browser.
    browser = webdriver.Firefox(executable_path=GeckoDriverManager().install())
    browser.get("https://imgur.com/t/wallpaper")
    # Imgur only loads images dynamically as you scroll down.
    # Using a script execute we force the page to scroll down 5 times.
    scrolling = 0
    while scrolling < 5:
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        scrolling += 1
        # Waiting so the bot can load the wallpapers.
        time.sleep(2)

    # Get all html img elements.
    tags = browser.find_elements_by_tag_name("img")

    for tag in tags:
        src = tag.get_attribute("src")
        # imgur has image properties in the url
        # example ( https://i.imgur.com/hAua146_d.webp?maxwidth=520&shape=thumb&fidelity=high )
        # I check if the src has the _ character and then slice the url to remove it so it can display
        # as an image in discord and not a link.
        if "_" in src:
            wallpapers.append(src[0:src.index("_")])

    browser.close()


# Event: On bot ready display connected string.
@bot.event
async def on_ready():
    print(f'{bot.user.name} connected to discord.')

    await get_wallpaper()

    print(f"Loaded {len(wallpapers)} wallpapers.")


# Command: About this bot - Displays github link.
@bot.command(name='about', help='About this bot.')
async def command_about(ctx):
    response = "I am a bot created for https://github.com/devin-monro"
    await ctx.send(response)


# Command: Gets a random wallpaper image from imgur
@bot.command(name='wallpaper', help='Get yourself a new wallpaper')
async def command_wallpaper(ctx):

    # If the wallpaper count gets lower than 5 refresh the list of wallpapers.
    if len(wallpapers) < 5:
        get_wallpaper()
        time.sleep(2)
    # Get a random wallpaper from the list.
    response = wallpapers[random.randint(0, len(wallpapers)-1)]
    # Remove the wallpaper that was just used to avoid duplicate posts.
    wallpapers.remove(response)

    await ctx.send(response)


# Handles when a user enters an invalid command.
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        await ctx.send("That is not a valid command!")
        return
    raise error

bot.run(TOKEN)
