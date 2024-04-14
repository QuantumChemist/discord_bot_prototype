import os
import discord
from discord.ext import commands

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
bot.run(BOT_TOKEN)
