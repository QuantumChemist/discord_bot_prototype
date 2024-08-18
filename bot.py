import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from discord_slash import SlashCommand, SlashContext

# Load environment variables from .env file
load_dotenv()

# Intents definition
intents = discord.Intents.default()
intents.messages = True
intents.reactions = True

# Define the bot's command prefix and initialize SlashCommand
bot = commands.Bot(command_prefix=commands.when_mentioned_or('!'), intents=intents)
slash = SlashCommand(bot, sync_commands=True)

# Event: Bot is ready
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

# Slash Command: Hello
@slash.slash(name='hello', description='Sends a greeting message.')
async def hello(ctx: SlashContext):
    if ctx.author.name == "user_name":
        await ctx.send("User specific message.")
    else:
        await ctx.send(f'Hello {ctx.author.mention}!')

# Slash Command: Get Message Content
@slash.slash(name='get_mess_cont', description='Gets the content of a message by link.')
async def get_message_content(ctx: SlashContext, message_link: str):
    try:
        message_id = int(message_link.split('/')[-1])
        message = await ctx.channel.fetch_message(message_id)
        await ctx.send(f"Content of the message: {message.content}")
    except Exception as e:
        await ctx.send(f"Failed to retrieve message content: {e}")

# Slash Command: Start Send Message
@slash.slash(name='start', description='Starts the chat mode.')
async def start_send_message(ctx: SlashContext):
    await ctx.send("Chat mode started!")
    try:
        while True:
            channel_id = await bot.loop.run_in_executor(None, input, "Enter the channel ID where you want to send the message: ")
            message = await bot.loop.run_in_executor(None, input, "Enter the message to send to Discord (or type 'quit' to exit): ")

            if channel_id == '0' or message.lower() == 'quit':
                await ctx.send("Chat mode stopped!")
                break

            channel = bot.get_channel(int(channel_id))

            if channel:
                await channel.send(message)
            else:
                print("Invalid channel ID. Please enter a valid channel ID.")
    except ValueError:
        print("Invalid input. Please enter a valid channel ID.")

# Slash Command: Logout
@slash.slash(name='logout', description='Logs out the bot.')
@commands.is_owner()
async def logout_bot(ctx: SlashContext):
    await ctx.send("Goodbye, minna-san~!")
    await bot.close()

# Event: Reaction is added
@bot.event
async def on_reaction_add(reaction, user):
    print(f'Reaction added: {reaction.emoji} by {user.name}')
    if user == bot.user:
        return

    message = await reaction.message.channel.fetch_message(reaction.message.id)
    print(f'Message fetched: {message.content}')

    # Handle thumbs up emoji with exactly one reaction
    if str(reaction.emoji) == '👍' and len(message.reactions) == 1:
        pins_channel = discord.utils.get(message.guild.channels, name="pins")
        if pins_channel:
            message_link = message.jump_url
            await pins_channel.send(
                f"Hey {message.author.mention}, why don't you take a screenshot of your three+ star message {message_link} and post it here?"
            )
            print(message.author.display_name, message.content)
    
    # Handle custom emojis with reactions greater than or equal to the threshold
    elif str(reaction.emoji) in ['custom_emoji'] and len(message.reactions) >= 3:
        pins_channel = discord.utils.get(message.guild.channels, name="server-pins")
        if pins_channel:
            message_link = message.jump_url
            await pins_channel.send(
                f"Hey {message.author.mention}, why don't you take a screenshot of your message {message_link} and post it here?"
            )
            print(message.author.display_name, message.content)

# Get the bot token from the environment variable
BOT_TOKEN = os.environ.get('BOT_TOKEN')

# Run the bot
if __name__ == '__main__':
    print(f"Running bot with token: {BOT_TOKEN}")
    bot.run(BOT_TOKEN)

