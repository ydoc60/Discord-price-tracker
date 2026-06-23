 Discord Price Tracker Bot

A Discord bot that monitors Amazon product prices and sends automatic alerts when the price drops.

 Commands
- `!track <url>` — start tracking a product
- `!tracked` — list all tracked products and their prices
- `!untrack <url>` — stop tracking a product

 How it works
- Fetches live prices using ScraperAPI
- Checks prices every hour automatically
- Saves tracked products to a JSON file so they persist through restarts
- Sends a Discord alert when a price drop is detected

 Built with
- Python
- discord.py
- BeautifulSoup
- ScraperAPI
- python-dotenv

 Setup
1. Clone the repo
2. Install dependencies: `pip install -r requirements.txt`
3. Add your keys to a `.env` file:
   - DISCORD_TOKEN=your_token
   - SCRAPERAPI_KEY=your_key
4. Run: `python bot.py`
