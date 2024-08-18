import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio

# Load environment variables from .env file
load_dotenv()

# Intents definition
intents = discord.Intents.default()
intents.messages = True
intents.reactions = True

# Define the bot's command prefix
bot = commands.Bot(command_prefix=commands.when_mentioned_or('!'), intents=intents)

# Emoji names
custom_emoji_names = ['custom_emoji']

# Threshold for the number of reactions
reaction_threshold = 1

# Event: Bot is ready
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

# Combined Event: Reaction is added
@bot.event
async def on_reaction_add(reaction, user):
    if user == bot.user:
        return

    message = await reaction.message.channel.fetch_message(reaction.message.id)

    # Handle thumbs up emoji with exactly one reaction
    if str(reaction.emoji) == '👍' and len(message.reactions) == 1:
        pins_channel = discord.utils.get(message.guild.channels, name="general")
        if pins_channel:
            message_link = message.jump_url
            await pins_channel.send(
                f"Hey {message.author.mention}, thumbs up emoji reaction for {message_link}!"
            )
            print(message.author.display_name, message.content)
    
    # Handle custom emojis with reactions greater than or equal to the threshold
    elif str(reaction.emoji) in custom_emoji_names and len(message.reactions) >= reaction_threshold:
        pins_channel = discord.utils.get(message.guild.channels, name="server-pins")
        if pins_channel:
            message_link = message.jump_url
            await pins_channel.send(
                f"Hey {message.author.mention}, thumbs up emoji reaction for {message_link}!"
            )
            print(message.author.display_name, message.content)

# Command: Get message content from link
@bot.command(name='get_mess_cont')
async def get_message_content(ctx, message_link: str):
    try:
        message_id = int(message_link.split('/')[-1])
        message = await ctx.channel.fetch_message(message_id)
        await ctx.send(f"Content of the message: {message.content}")
    except Exception as e:
        await ctx.send(f"Failed to retrieve message content: {e}")    

# Command to start the background task (Refactored)
@bot.command(name='start')
async def start_send_message(ctx):
    await ctx.send("Chat mode started!")
    channel_id = None  # Initialize channel_id variable
    try:
        while True:
            if channel_id is None:
                channel_id = await bot.loop.run_in_executor(None, input, "Enter the channel ID where you want to send the message: ")
            message = await bot.loop.run_in_executor(None, input, "Enter the message to send to Discord (or type 'quit' to exit): ")

            if channel_id == '0' or message.lower() == 'quit':
                await ctx.send("Chat mode stopped!")
                break
            if channel_id == '1':
                channel_id = None

            channel = bot.get_channel(int(channel_id))

            if channel:
                await channel.send(message)
            else:
                print("Invalid channel ID. Please enter a valid channel ID.")
    except ValueError:
        print("Invalid input. Please enter valid channel ID.")

# Command: Logout
@bot.command(name='logout')
@commands.is_owner()
async def logout_bot(ctx):
    await ctx.send("Goodbye, minna-san~!")
    await bot.close()

# Command: Hello
@bot.command(name='hello')
async def hello(ctx):
    if ctx.author.name == "user_name":
        await ctx.send("User specific message.")
    else:
        await ctx.send(f'Hello {ctx.author.mention}!')

# Get the bot token from the environment variable
BOT_TOKEN = os.environ.get('BOT_TOKEN')

# Run the bot
if __name__ == '__main__':
    print(f"Running bot with token: {BOT_TOKEN}")
    bot.run(BOT_TOKEN)

