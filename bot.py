import discord
import aiohttp
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
GROUP_ID = '47521425-1a89-452a-b9ac-5708064abdce'  # Eternal Petal Scan

# Dicionário com cargos (ID dos cargos do Discord)
manga_roles = {
    "Impossibility Defense": {
        "main": 1365512350584537181,  # cargo da obra
        "global": 1382432721695019068  # cargo "todas as obras"
    },
    "Mikoto-chan wa Kirawaretakunai!": {
        "main": 1368592168079458384,
        "global": 1382432721695019068
    },
    "Taida na Succubus-chan": {
        "main": 1371100723793625170,
        "global": 1382432721695019068
    },
    "Please Give Me Your Blood, I Will Serve You in Gratitude": {
        "main": 1388271881869852802,
        "global": 1382432721695019068
    },
    "Brutal": {
        "main": 1383783748117598218,
        "global": 1382432721695019068
    },
    "Webtoon Character Na Kang Lim": {
        "main": 1390157471112237057,
        "global": 1382432721695019068
    },
    "Azure Wants to Turn Me into the Ideal BF": {
        "main": 1375487561153384468,
        "global": 1382432721695019068
    },
    "My Eldritch Girlfriend": {
        "main": 1365512189355622511,
        "global": 1382432721695019068
    },
    "Debby the Corsifa wa Makezugirai": {
        "main": 1385309718423277758,
        "global": 1382432721695019068
    },
    "Genkai Dungeon no Hanshoku Jijou": {
        "main": 1383784065962086492,
        "global": 1382432721695019068
    },
    "Crazy for You": {
        "main": 1383784181808631808,
        "global": 1382432721695019068
    },
    "I Thought She Was a Yandere, but Apparently She's Even Worse": {
        "main": 1385995914761736212,
        "global": 1382432721695019068
    },
    "Onigiriya no Neko": {
        "main": 1388925522557272227,
        "global": 1382432721695019068
    },
    "Instant Regret": {
        "main": 1389252374060859563,
        "global": 1382432721695019068
    },
    "Class no Gal ni Kuuki Atsukai Sareteimasu": {
        "main": 1370728666195169320,
        "global": 1382432721695019068
    },
    "Blue Ursus": {
        "main": 1383783638180823081,
        "global": 1382432721695019068
    },
    "A Little Sister with Squishy Cheeks": {
        "main": 1390007833516572744,
        "global": 1382432721695019068
    }
}

last_chapter_id = None

intents = discord.Intents.default()
client = discord.Client(intents=intents)

async def fetch_latest_chapter():
    url = f"https://api.mangadex.org/chapter?limit=1&translatedLanguage[]=en&order[publishAt]=desc&groups[]={GROUP_ID}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            if data["results"]:
                return data["results"][0]["data"]
            return None

async def check_new_chapter():
    global last_chapter_id
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    while not client.is_closed():
        chapter = await fetch_latest_chapter()
        if chapter and chapter["id"] != last_chapter_id:
            chapter_number = chapter["attributes"].get("chapter", "?")
            title = chapter["attributes"].get("title", "")
            manga_id = next((rel["id"] for rel in chapter["relationships"] if rel["type"] == "manga"), None)

            manga_title = "Mangá Desconhecido"
            if manga_id:
                manga_url = f"https://api.mangadex.org/manga/{manga_id}"
                async with aiohttp.ClientSession() as session:
                    async with session.get(manga_url) as resp:
                        manga_data = await resp.json()
                        manga_title = manga_data["data"]["attributes"]["title"]["en"]

            link = f"https://mangadex.org/chapter/{chapter['id']}"
            roles = manga_roles.get(manga_title)

            role_mentions = ""
            if roles:
                main_mention = f"<@&{roles['main']}>"
                global_mention = f"<@&{roles['global']}>"
                role_mentions = f"{main_mention} {global_mention}"

            msg = (
                f"📢 Novo capítulo de **{manga_title}** postado pela **Eternal Petal Scan**!"

                f"📘 Capítulo {chapter_number} - {title or 'Sem título'}"

                f"🔗 {link}"

                f"📌 {role_mentions}"
            )

            await channel.send(msg)
            last_chapter_id = chapter["id"]

        await asyncio.sleep(300)

@client.event
async def on_ready():
    print(f"✅ Bot logado como {client.user}")

client.loop.create_task(check_new_chapter())
client.run(TOKEN)