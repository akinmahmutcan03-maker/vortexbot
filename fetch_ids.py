import asyncio
import os
import discord

TOKEN = os.environ.get("DISCORD_TOKEN")

async def main():
    guild_id = int(input("Sunucu ID: "))
    intents = discord.Intents.default()
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        guild = client.get_guild(guild_id)
        if not guild:
            try:
                guild = await client.fetch_guild(guild_id)
            except Exception as e:
                print(f"Sunucu bulunamadı: {e}")
                await client.close()
                return

        print(f"\n{'='*50}")
        print(f"SUNUCU: {guild.name} (ID: {guild.id})")
        print(f"{'='*50}")

        print("\n📋 KANALLAR:")
        channels = await guild.fetch_channels()
        for ch in sorted(channels, key=lambda c: (str(type(c).__name__), c.position if hasattr(c, 'position') else 0)):
            if isinstance(ch, discord.TextChannel):
                print(f"  #{ch.name:<35} {ch.id}  [METİN]")
            elif isinstance(ch, discord.VoiceChannel):
                print(f"  🔊{ch.name:<34} {ch.id}  [SES]")
            elif isinstance(ch, discord.CategoryChannel):
                print(f"  📁 {ch.name:<34} {ch.id}  [KATEGORİ]")

        print("\n🎭 ROLLER:")
        roles = guild.roles if guild.roles else await guild.fetch_roles()
        for r in sorted(roles, key=lambda r: -r.position):
            if r.name != "@everyone":
                print(f"  @{r.name:<35} {r.id}")

        print(f"\n{'='*50}")
        await client.close()

    await client.start(TOKEN)

asyncio.run(main())
