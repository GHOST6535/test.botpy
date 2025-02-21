import discord
from discord.ext import commands
import asyncio
import os
import random
from datetime import datetime, timedelta
import platform
import psutil

TOKEN = os.environ.get("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("DISCORD_TOKEN environment variable not set.")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Image Handling:
IMAGE_DIR = os.path.join(os.path.dirname(__file__), "images")
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

IMAGE_FILES = [
    os.path.join(IMAGE_DIR, f) for f in os.listdir(IMAGE_DIR)
    if os.path.isfile(os.path.join(IMAGE_DIR, f))
    and f.lower().endswith(('image.png', 'image2.png', 'image3.png', 'image4.png','image5.png','image6.jpg'))
]

if not IMAGE_FILES:
    raise ValueError("No images found in the 'images' directory.")

TARGET_CHANNEL_ID = 1332420477959929878

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

DEVELOPER_IDS = [878543757245550602]  # Replace with actual developer IDs

@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")
    print(f"Target channel ID (hardcoded): {TARGET_CHANNEL_ID}")

    await bot.change_presence(status=discord.Status.do_not_disturb, activity=discord.Streaming(name="Hail M2PLO", url="http://youtube.com/m2plo"))

    while True:
        await send_random_image()
        await asyncio.sleep(420)

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

bot.run(TOKEN)
