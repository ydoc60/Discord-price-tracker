import discord
from discord.ext import commands, tasks
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import json

load_dotenv()
token = os.getenv("DISCORD_TOKEN")
scraper_key = os.getenv("SCRAPERAPI_KEY")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

tracked_products = {}
if os.path.exists("tracked_products.json"):
    with open("tracked_products.json", "r") as f:
        tracked_products = json.load(f)

@bot.command()
async def track(ctx, url):
    await ctx.send("Fetching price, please wait...")
    
    price = None
    for attempt in range(3):
        scraper_url = f"http://api.scraperapi.com?api_key={scraper_key}&url={url}"
        response = requests.get(scraper_url)
        soup = BeautifulSoup(response.content, "html.parser")
        price = soup.find("span", {"class": "a-price-whole"})
        if price:
            break
    
    if price:
        current_price = float(price.text.replace(",", ""))
        channel_id = str(ctx.channel.id)
        if channel_id not in tracked_products:
            tracked_products[channel_id] = {}
        tracked_products[channel_id][url] = current_price
        with open("tracked_products.json", "w") as f:
            json.dump(tracked_products, f)
        await ctx.send(f"Current price: ${current_price} — I'll alert you if it drops!")
    else:
        await ctx.send("Could not find price.")

@bot.command()
async def tracked(ctx):
    channel_id = str(ctx.channel.id)
    if channel_id not in tracked_products or not tracked_products[channel_id]:
        await ctx.send("No products being tracked in this channel.")
        return
    
    message = "**Tracked products:**\n"
    for url, price in tracked_products[channel_id].items():
        message += f"${price} — {url}\n"
    
    await ctx.send(message)

@bot.command()
async def untrack(ctx, url):
    channel_id = str(ctx.channel.id)
    if channel_id in tracked_products and url in tracked_products[channel_id]:
        del tracked_products[channel_id][url]
        with open("tracked_products.json", "w") as f:
            json.dump(tracked_products, f)
        await ctx.send("Product removed from tracking.")
    else:
        await ctx.send("That product is not being tracked.")

@tasks.loop(hours=1)
async def check_prices():
    for channel_id, products in tracked_products.items():
        channel = bot.get_channel(int(channel_id))
        for url, original_price in products.copy().items():
            scraper_url = f"http://api.scraperapi.com?api_key={scraper_key}&url={url}"
            response = requests.get(scraper_url)
            soup = BeautifulSoup(response.content, "html.parser")
            price = soup.find("span", {"class": "a-price-whole"})
            if price:
                current_price = float(price.text.replace(",", ""))
                if current_price < original_price:
                    await channel.send(f"Price drop! <{url}>\nWas: ${original_price} — Now: ${current_price}")
                    tracked_products[channel_id][url] = current_price
                    with open("tracked_products.json", "w") as f:
                        json.dump(tracked_products, f)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    if not check_prices.is_running():
        check_prices.start()

bot.run(token)