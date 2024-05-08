import os
import sys
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import aiocurl
import asyncio
import functools
import typing
#import bot_aux

# Load environment variables from .env file
load_dotenv()

# Intents definition
intents = discord.Intents.default()
intents.messages = True
intents.reactions = True

# Define the bot's command prefix
bot = commands.Bot(command_prefix=commands.when_mentioned_or(''), intents=intents)

# Event: Bot is ready
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

# Emoji names
custom_emoji_names = ['custom_emoji']

# Threshold for the number of reactions
reaction_threshold = 3

# Event: Reaction is added
@bot.event
async def on_reaction_add(reaction, user):
    # Check if the reaction is a thumbs up emoji and the message is not from the bot itself
    if str(reaction.emoji) == '👍' and user != bot.user:
        # Fetch the message that received the reaction
        message = await reaction.message.channel.fetch_message(reaction.message.id)
        # Check if the message has exactly one reaction
        if len(message.reactions) == 1:
            # Get the "pins" channel
            pins_channel = discord.utils.get(message.guild.channels, name="pins")
            if pins_channel:
                # Get the permalink of the message
                message_link = message.jump_url
                # Send the message link to the "pins" channel
                await pins_channel.send(f"Hey {message.author.mention}, why don't you take a screenshot of your three+ star message {message_link} and post it here?")
                print(message.author.display_name, message.content)
    
# Event: Reaction is added
@bot.event
async def on_reaction_add(reaction, user):
    # Check if the reaction is a thumbs up emoji and the message is not from the bot itself
    if str(reaction.emoji) in custom_emoji_names and user != bot.user:
        # Fetch the message that received the reaction
        message = await reaction.message.channel.fetch_message(reaction.message.id)
        # Check if the message has exactly one reaction
        if len(message.reactions) >= reaction_threshold:
            # Get the "server-pins" channel
            pins_channel = discord.utils.get(message.guild.channels, name="server-pins")
            if pins_channel:
                # Get the permalink of the message
                message_link = message.jump_url
                # Send the message link to the "pins" channel
                await pins_channel.send(f"Hey {message.author.mention}, why don't you take a screenshot of your message {message_link} and post it here?")
                print(message.author.display_name, message.content)         
               
# Command: Get message content from link
@bot.command(name='get_mess_cont')
async def get_message_content(ctx, message_link: str):
    try:
        # Parse the message ID from the link
        message_id = int(message_link.split('/')[-1])
        # Fetch the message using its ID
        message = await ctx.channel.fetch_message(message_id)
        # Send the message content
        await ctx.send(f"Content of the message: {message.content}")
    except Exception as e:
        await ctx.send(f"Failed to retrieve message content: {e}")    
            
# Command to start the background task
@bot.command(name='start')
async def start_send_message(ctx):
    await ctx.send("Chat mode started!")
    while True:
        try:
            # Get the channel ID and message from the terminal
            channel_id = int(input("Enter the channel ID where you want to send the message: "))
            message = input("Enter the message to send to Discord (or type 'quit' to exit): ")
            
            if channel_id == 0 or message.lower() == 'quit':
                await ctx.send("Chat mode stopped!")
                break

            # Get the channel object
            channel = bot.get_channel(channel_id)

            if channel:
                await channel.send(message)
            else:
                print("Invalid channel ID. Please enter a valid channel ID.")
        except ValueError:
            print("Invalid channel ID. Please enter a valid channel ID.")

@bot.command(name='logout')
@commands.is_owner()
async def logout_bot(ctx):
    await ctx.send("Goodbye, minna-san~!")
    await bot.close()
    
# Command: Hello
@bot.command(name='hello')
async def hello(ctx):
    # Send a greeting message
    if ctx.author.name == "user_name":
        # Send a custom response
        await ctx.send("User specific message.")
    else:
        # Send a generic greeting message
        await ctx.send(f'Hello {ctx.author.mention}!')

# Get the bot token from the environment variable
BOT_TOKEN = os.environ.get('BOT_TOKEN')

# Use the bot token to run your bot
#bot.run(BOT_TOKEN)

@bot.listen()
async def on_message(message):
    print("Done!")

# Your bot's main function for running it a specific time
async def main():
    await client.start(BOT_TOKEN)
    # Run the bot for 10 seconds
    await asyncio.sleep(10)
    await client.close()
