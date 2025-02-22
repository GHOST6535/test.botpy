import discord
from discord.ext import commands
import asyncio
import os
import random
from datetime import datetime
import platform
import psutil

TOKEN = os.environ.get("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("DISCORD_TOKEN environment variable not set.")

intents = discord.Intents.default()
intents.message_content = True  # Required for message content

bot = commands.Bot(command_prefix="!", intents=intents)

# Image Handling:
IMAGE_DIR = os.path.join(os.path.dirname(__file__), "images")
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

IMAGE_FILES = [
    os.path.join(IMAGE_DIR, f) for f in os.listdir(IMAGE_DIR)
    if os.path.isfile(os.path.join(IMAGE_DIR, f))
    and f.lower().endswith(('image.png', 'image2.png', 'image3.png', 'image4.png','image5.png','image6.jpg','image7.png'))
]

if not IMAGE_FILES:
    raise ValueError("No images found in the 'images' directory.")

TARGET_CHANNEL_ID = 1332420477959929878  # Replace with your channel ID
TARGET_GUILD_ID = 1332420476877934642  # Replace with the target guild ID
ANNOUNCEMENT_CHANNEL_ID = 1332421696887717959  # Replace with your announcement channel ID

async def send_random_image():
    try:
        channel = bot.get_channel(TARGET_CHANNEL_ID)
        if channel:
            chosen_image = random.choice(IMAGE_FILES)
            await channel.send(file=discord.File(chosen_image, filename=os.path.basename(chosen_image)))
            print(f"Image {chosen_image} sent to {channel.name} at {datetime.now()}")
        else:
            print(f"Error: Could not find channel with ID {TARGET_CHANNEL_ID}")
    except Exception as e:
        print(f"Error sending image: {e}")

bot_start_time = datetime.now()

def get_system_info():
    system = platform.system()
    release = platform.release()
    version = platform.version()
    machine = platform.machine()
    processor = platform.processor()

    ram = psutil.virtual_memory()
    total_ram = ram.total / (1024 ** 3)
    available_ram = ram.available / (1024 ** 3)
    used_ram = ram.used / (1024 ** 3)
    ram_percent = ram.percent

    return f"System: {system} {release} {version}\nMachine: {machine}\nProcessor: {processor}\nTotal RAM: {total_ram:.2f} GB\nAvailable RAM: {available_ram:.2f} GB\nUsed RAM: {used_ram:.2f} GB ({ram_percent:.1f}%)"

def get_bot_uptime():
    uptime = datetime.now() - bot_start_time
    hours, remainder = divmod(int(uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    return f"{days} days, {hours} hours, {minutes} minutes, {seconds} seconds"

DEVELOPER_IDS = [878543757245550602]  # Replace with your developer ID
ANNOUNCER_IDS = [736212585573122048, 1319339948117201077,1061289422924038184]  # Add user IDs here


@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")
    print(f"Target channel ID (hardcoded): {TARGET_CHANNEL_ID}")
    print(f"Target Guild ID (hardcoded): {TARGET_GUILD_ID}")
    print(f"Announcement Channel ID (hardcoded): {ANNOUNCEMENT_CHANNEL_ID}")

    await bot.change_presence(status=discord.Status.do_not_disturb, activity=discord.Streaming(name="Hail M2PLO", url="http://youtube.com/m2plo"))

    while True:
        await send_random_image()
        await asyncio.sleep(1800) #time to send messages 30 minutes

@bot.command(name="status")
async def status(ctx):
    system_info = get_system_info()
    latency_ms = round(bot.latency * 1000, 2)
    ram = psutil.virtual_memory()
    ram_percent = ram.percent
    uptime = get_bot_uptime()

    em = discord.Embed(title=f"{bot.user.name}'s Status", color=discord.Color.red())
    em.add_field(name="System Info", value=system_info, inline=False)
    em.add_field(name="Latency", value=f"{latency_ms} ms", inline=True)
    em.add_field(name="RAM Usage", value=f"{ram_percent:.1f}%", inline=True)
    em.add_field(name="Uptime", value=uptime, inline=False)
    await ctx.send(embed=em)

@bot.command(name="restart")
async def restart(ctx):
    if ctx.author.id not in DEVELOPER_IDS:
        await ctx.send("Only Ghostyy can access this command.")
        return

    await ctx.send("M2PLO WORKER is restarting...")
    os.system("python main.py")  # Replace with your actual run command
    await bot.close()

@bot.command(name="announce")
async def announce(ctx, *, message):
    if ctx.author.id not in DEVELOPER_IDS and ctx.author.id not in ANNOUNCER_IDS:
        await ctx.send("You do not have permission to use this command.")
        return

    if ctx.guild.id != TARGET_GUILD_ID:
        await ctx.send("This command can only be used in the specified server.")
        return

    announcement_channel = bot.get_channel(ANNOUNCEMENT_CHANNEL_ID)

    if not announcement_channel:
        await ctx.send("Announcement channel not found.")
        return

    confirmation_message = await ctx.send(f"Are you sure you want to send this message to the channel '{announcement_channel.name}'?\n```\n{message}\n```\nType 'yes' to confirm or 'no' to cancel.")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        confirmation = await bot.wait_for('message', check=check, timeout=30.0)
        if confirmation.content.lower() == 'yes':
            confirmed = True
        else:
            await ctx.send("Announcement cancelled.")
            await confirmation_message.delete()
            await ctx.message.delete()
            return

    except asyncio.TimeoutError:
        await ctx.send("Confirmation timed out.")
        await confirmation_message.delete()
        await ctx.message.delete()
        return

    if confirmed:
        try:
            await announcement_channel.send(message)
            confirmation_sent = await ctx.send(f"Announcement sent to {announcement_channel.mention}.")
            print(f"Announcement sent to channel: {announcement_channel.name} ({announcement_channel.id})")

            await confirmation_message.delete()
            await ctx.message.delete()
            await confirmation_sent.delete(delay=5)

        except Exception as e:
            await ctx.send(f"Error sending announcement: {e}")
            await confirmation_message.delete()
            await ctx.message.delete()
            print(f"Error sending announcement to channel {announcement_channel.name} ({announcement_channel.id}): {e}")


bot.run(TOKEN)
