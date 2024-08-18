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

# Event: Reaction is added
@bot.event
async def on_reaction_add(reaction, user):
    if user == bot.user:
        return

    message = await reaction.message.channel.fetch_message(reaction.message.id)

    # Handle thumbs up emoji with exactly one reaction
    if str(reaction.emoji) == '👍' and len(message.reactions) == 1:
        pins_channel = discord.utils.get(message.guild.channels, name="thumbsup")
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

        # Check if the message author is the bot
        if message.author == bot.user:
            await ctx.send(f"Content of the message: {message.content}")
        else:
            await ctx.send("Error: The message is not from the bot.")

    except Exception as e:
        await ctx.send(f"Failed to retrieve message content: {e}")

# Flag to check if start command has been triggered
start_triggered = False

@bot.command(name='start')
async def start_send_message(ctx):
    global start_triggered

    if start_triggered:
        await ctx.send("The start command has already been triggered and cannot be run again.")
        return

    start_triggered = True  # Set the flag to indicate the command has been triggered
    await ctx.send("Chat mode started!")
    channel_id = None  # Initialize channel_id variable

    while True:
        try:
            if channel_id is None:
                channel_id = await bot.loop.run_in_executor(None, input,
                                                            "Enter the channel ID where you want to send the message: ")
            message = await bot.loop.run_in_executor(None, input,
                                                     "Enter the message to send to Discord "
                                                     "(or type '_switch' to enter a new channel ID or '_quit' to exit): ")

            if message.lower() == '_quit':
                await ctx.send("Chat mode stopped!")
                start_triggered = False  # Reset the flag so the command can be triggered again if needed
                break

            if message.lower() == '_switch':
                channel_id = None
                continue  # Skip sending the message and reset the channel ID

            # Check if the message is empty
            if not message.strip():
                print("Cannot send an empty message. Please enter a valid message.")
                continue

            channel = bot.get_channel(int(channel_id))
            if channel:
                try:
                    await channel.send(message)
                except discord.HTTPException as e:
                    print(f"Failed to send message: {e}")
            else:
                print("Invalid channel ID. Please enter a valid channel ID.")

        except ValueError:
            print("Invalid input. Please enter a valid channel ID.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            # The loop will automatically continue after handling the exception

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
    elif ctx.author.name == "chichimeetsyoko":
        await ctx.send("Hallihallo, Chris!")
    elif ctx.author.name == os.environ.get('user1'):
        await ctx.send(os.environ.get('message1'))
    else:
        await ctx.send(f'Hello {ctx.author.mention}!')

# Helper function: List all bot commands with custom definitions
async def list_bot_commands(ctx):
    # Define potential command descriptions
    command_definitions = {
        'help': "To call upon mine aid, revealing the knowledge thou dost require.",
        'logout': "To depart from my presence and return to thine own realm.",
        'get_mess_cont': "To summon forth the contents of messages past, "
                         "though it may be fraught with peril (only works with bot messages).",
        'hello': "To greet me, though beware, for I am not fond of idle pleasantries.",
        'start': "To rouse me into action, shouldst thou wish to embark upon a new venture.",
    }

    # Create a list of commands that exist in the bot, along with their descriptions if available
    commands_list = []
    for command in bot.commands:
        name = command.name
        description = command_definitions.get(name, "No description available.")
        commands_list.append(f'`{name}` — {description}')

    # Sort the command list alphabetically
    commands_list = sorted(commands_list)

    # Join the sorted list into a string with each command on a new line
    commands_str = '\n'.join(commands_list)

    # Send the formatted list of commands to the channel
    await ctx.send(f"Who dares to disturb my slumber? \n"
                   f"Mortal {ctx.author.mention}, thou art bold to awaken a beast of such age and grandeur. \n"
                   f"Speak quickly, lest my patience wears thin, "
                   f"for the sands of time are precious even to one as ancient as I. \n"
                   f"Shouldst thou seek guidance within my domain, "
                   f"know that these are the words of command I may deign to bestow upon thee: \n{commands_str}")
    # Wait for 3 seconds before sending the message
    await asyncio.sleep(3)
    await ctx.send(f"\nNow, mortal {ctx.author.mention}, take heed of these commands, "
                   f"for I shall not suffer fools to waste my time. \n"
                   f"Use them wisely, and perhaps thou may yet earn a measure of my respect. \n"
                   f"But beware, for my wrath is as fiery as my breath, and my patience is not infinite.")

# Event: on_message to check if bot was mentioned
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user.mentioned_in(message) and len(message.content.split()) == 1:
        ctx = await bot.get_context(message)
        await list_bot_commands(ctx)

    await bot.process_commands(message)

# Error handling: CommandNotFound
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"Error: The command you entered is not recognized. "
                       f"Please use `@{bot.user.name}` to see a list of available commands.")
    else:
        # Handle other errors here if necessary
        await ctx.send(f"An error occurred: {error}")

# Get the bot token from the environment variable
BOT_TOKEN = os.environ.get('BOT_TOKEN')

# Run the bot
if __name__ == '__main__':
    print(f"Running bot with token: {BOT_TOKEN}")
    bot.run(BOT_TOKEN)
