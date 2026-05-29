import discord
from discord.ext import commands, tasks
import random
import os
import json 
import asyncio
from keep_alive import keep_alive 
from datetime import datetime, timezone
from typing import Optional, Dict, Union
from discord.ui import View, Select, Button, Modal, TextInput
from draw_figure import generate_figure
import re

# =============================================================
# 1. AYARLAR VE SABİT DEĞİŞKENLER
# =============================================================
SUNUCU_ADI = "VORTEX LEAGUE"
OWNER_ID = 1243258148232368286
DEGER_YETKILISI_ROL_ID = 1501880582966349847
ANTRENMAN_KANAL_ID = 1501880732279242763
ANTRENMAN_BILDIRI_KANAL_ID = 1505230124222513204
INSTAGRAM_KANAL_ID = 1501880764659404830
KAYIT_KANAL_ID = 1501880695989997752
KAYIT_YETKILI_ROL_ID = 1501880581909250129
KAYITSIZ_ROL_ID = 1501880613270061167
LOG_KANAL_ID = 1501880695989997752
SOHBET_KANAL_ID = 1501880721516793866
TICKET_KANAL_ID = 1501880700591411270
DESTEK_KATEGORI_ID = 1505992163362607234
YETKILI_1_ID = 1501880582966349847
YETKILI_2_ID = 1501880584048480289
BASKAN_ROL_ID = 1501880590696452198
KAPTAN_ROL_ID = 1503137544777502841
TEKNIK_DIREKTOR_ROL_ID = 1501880592277442603
FUTBOLCU_ROL_ID = 1501880611168583802
ILAN_VER_KANAL_ID = 1505691627774152834
TRANSFER_LISTESI_ID = 1505691755205623969
DEGER_LOG = 1503819843672084601

ROLLER = {
    "futbolcu": FUTBOLCU_ROL_ID, 
    "teknik direktör": TEKNIK_DIREKTOR_ROL_ID,
    "kayitli": FUTBOLCU_ROL_ID,
    "kayitsiz": KAYITSIZ_ROL_ID
}

TAKIM_LOGOLARI = {
    "Paris": "https://i.imgur.com/y4N2yJp.png",
    "Barcelona": "https://i.imgur.com/w6TqTzL.png",
    "Real Madrid": "https://i.imgur.com/gJ6hL6x.png",
    "Manchester City": "https://i.imgur.com/qL3t3S4.png",
    "Dortmund": "https://i.imgur.com/Y32wW9M.png",
    "Galatasaray": "https://i.imgur.com/jMzNz3a.png",
    "Fenerbahçe": "https://i.imgur.com/z4f1YfN.png",
    "Arsenal": "https://i.imgur.com/P4aGzS6.png",
}

PARA_DOSYA = "para.json"
ANTRENMAN_DOSYA = "antrenman.json"
STAT_DOSYA = "stats.json"

STAT_ISIMLER = {
    "antrenman":      "🏋️ Antrenman",
    "penalti_atilan": "🥅 Penaltı Atılan",
    "penalti_gol":    "⚽ Penaltı Golü",
    "post":           "📸 Post",
    "kayit_yapildi":  "📋 Kayıt Yapıldı",
}

# =============================================================
# 2. BOT VE INTENTS TANIMLAMA
# =============================================================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='.', intents=intents, help_command=None)

# =============================================================
# 3. YARDIMCI FONKSİYONLAR (JSON, KULLANICI VERİSİ vb.)
# =============================================================
def veri_yukle(dosya_adi, varsayilan_deger={}):
    if not os.path.exists(dosya_adi):
        veri_kaydet(dosya_adi, varsayilan_deger)
        return varsayilan_deger
    try:
        with open(dosya_adi, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, TypeError, FileNotFoundError):
        veri_kaydet(dosya_adi, varsayilan_deger)
        return varsayilan_deger

def veri_kaydet(dosya_adi, data):
    try:
        with open(dosya_adi, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"HATA - {dosya_adi} kaydedilemedi: {e}")

def get_user_para_data(user_id):
    data = veri_yukle(PARA_DOSYA)
    user_id = str(user_id)
    if user_id not in data:
        data[user_id] = {"cash": 0, "bank": 0}
    return data, data[user_id]

def stat_oku():
    return veri_yukle(STAT_DOSYA, {})

def stat_yaz(data):
    veri_kaydet(STAT_DOSYA, data)

def stat_ekle(uid: str, key: str, miktar: int = 1):
    data = stat_oku()
    uid = str(uid)
    if uid not in data:
        data[uid] = {}
    data[uid][key] = data[uid].get(key, 0) + miktar
    stat_yaz(data)

# Verileri başlangıçta yükle
antrenman_sayaci = veri_yukle(ANTRENMAN_DOSYA, {})

# =============================================================
# 4. EVENTLER (on_ready, on_member_join vb.)
# =============================================================
@bot.event
async def on_ready():
    if not self_ping.is_running():
        self_ping.start()
    print(f"✅ {bot.user} AKTİF! {SUNUCU_ADI} Sistemi Hazır.")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        kullanilan = ctx.message.content.split()[0][1:]
        embed = discord.Embed(
            description=f"❌ **`.{kullanilan}`** diye bir komut yok.\n`.yardım` yazarak mevcut komut listesine bakabilirsin.",
            color=0xe74c3c
        )
        await ctx.send(embed=embed, delete_after=8)
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Bu komutu kullanmak için yetkin yok!", delete_after=8)
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Eksik argüman! Lütfen komutu doğru kullan: `.{ctx.command.name} {ctx.command.signature}`", delete_after=8)
    else:
        print(f"Bir hata oluştu: {error}")

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(KAYIT_KANAL_ID)
    if not channel or not isinstance(channel, discord.TextChannel):
        return

    simdi = datetime.now(timezone.utc)
    hesap_yasi = (simdi - member.created_at).days

    if hesap_yasi >= 30: guvenlik = "🟢 Güvenilir"
    elif hesap_yasi >= 7: guvenlik = "🟡 Şüpheli"
    else: guvenlik = "🔴 Yeni Hesap"

    embed = discord.Embed(
        title=f"⚡ {SUNUCU_ADI}'E YENİ BİR OYUNCU KATILDI",
        description=f"🎉 Aramıza hoş geldin {member.mention}",
        color=0x7c3aed
    )
    embed.add_field(name="👤 Kullanıcı", value=f"{member.name}", inline=True)
    embed.add_field(name="🆔 ID", value=f"`{member.id}`", inline=True)
    embed.add_field(name="👥 Sunucu", value=f"{member.guild.member_count}. üye", inline=True)
    embed.add_field(name="📅 Hesap Oluşturma", value=member.created_at.strftime("%d.%m.%Y %H:%M"), inline=False)
    embed.add_field(name="⏳ Hesap Yaşı", value=f"{hesap_yasi} gün", inline=True)
    embed.add_field(name="🛡️ Güvenlik", value=guvenlik, inline=True)
    embed.add_field(name="📋 Durum", value="`Kayıt Bekliyor...`", inline=False)

    if member.avatar:
        embed.set_thumbnail(url=member.avatar.url)
    if member.guild.icon:
        embed.set_author(name=member.guild.name, icon_url=member.guild.icon.url)
    embed.set_footer(text=f"{SUNUCU_ADI} • Kayıt Sistemi")

    await channel.send(content=f"🚨 <@&{KAYIT_YETKILI_ROL_ID}> yeni kayıt geldi!", embed=embed)

# =============================================================
# 5. DEĞER SİSTEMİ (GELİŞMİŞ TASARIM)
# =============================================================
def parse_deger(deger_str):
    return float(deger_str.upper().replace('M', '').replace('€', '').replace(',', '.').strip())

def deger_bar(deger: float) -> str:
    """0–200M aralığında görsel bir ilerleme çubuğu oluşturur."""
    filled = min(int(deger / 10), 20)
    empty = 20 - filled
    return "█" * filled + "░" * empty

def deger_tier(deger: float) -> tuple[str, int]:
    """Değere göre seviye etiketi ve renk döndürür."""
    if deger >= 150:
        return ("👑 Efsane", 0xffd700)
    elif deger >= 100:
        return ("💎 Dünya Yıldızı", 0x00cfff)
    elif deger >= 70:
        return ("🔥 Elit", 0xff6b35)
    elif deger >= 40:
        return ("⚡ Yükselen", 0x7c3aed)
    elif deger >= 20:
        return ("🌱 Umut Vadeden", 0x2ecc71)
    else:
        return ("📋 Sıradan", 0x95a5a6)

async def deger_guncelle(ctx, m, miktar, sebep, islem):
    if not isinstance(ctx.author, discord.Member) or not ctx.author.get_role(DEGER_YETKILISI_ROL_ID):
        return await ctx.send("❌ Yetkin yok!")
    try:
        val = parse_deger(miktar)
        parcalar = m.display_name.split(" | ")
        if len(parcalar) < 4:
            return await ctx.send(
                embed=discord.Embed(
                    title="❌ Format Hatası",
                    description="Oyuncunun nick formatı hatalı!\n\n**Doğru format:**\n`İsim | Mevki | Takım | 0M€`",
                    color=0xe74c3c
                )
            )
        isim, mevki, takim, deger = parcalar[0].strip(), parcalar[1].strip(), parcalar[2].strip(), parcalar[3].strip()
        eski = parse_deger(deger)

        if islem == "artir":
            yeni = eski + val
            renk = 0x00d084
            yön_emoji = "📈"
            yön_text = f"+{val:g}M€"
            baslik = "📈 PİYASA DEĞERİ ARTIRILDI"
            banner_renk = "🟢"
        else:
            yeni = max(0, eski - val)
            renk = 0xff4444
            yön_emoji = "📉"
            yön_text = f"-{val:g}M€"
            baslik = "📉 PİYASA DEĞERİ DÜŞÜRÜLDÜ"
            banner_renk = "🔴"

        await m.edit(nick=f"{isim} | {mevki} | {takim} | {yeni:g}M€")

        tier_label, tier_color = deger_tier(yeni)
        bar = deger_bar(yeni)
        zaman = datetime.now(timezone.utc).strftime('%d/%m/%Y • %H:%M')

        embed = discord.Embed(color=renk)
        embed.set_author(
            name=f"{SUNUCU_ADI} | Piyasa Değeri",
            icon_url=ctx.guild.icon.url if ctx.guild.icon else None
        )

        embed.description = (
            f"## {baslik}\n"
            f"{'─' * 32}\n"
            f"**{m.mention}** adlı oyuncunun piyasa değeri güncellendi. {banner_renk}"
        )

        embed.add_field(
            name="👤 Oyuncu Bilgileri",
            value=(
                f"```\n"
                f"Ad     : {isim}\n"
                f"Mevki  : {mevki}\n"
                f"Takım  : {takim}\n"
                f"```"
            ),
            inline=False
        )

        embed.add_field(
            name="💰 Değer Değişimi",
            value=(
                f"**Eski:** `{eski:g}M€`\n"
                f"**Yeni:** `{yeni:g}M€`\n"
                f"**Fark:** `{yön_text}`"
            ),
            inline=True
        )

        embed.add_field(
            name=f"🏅 Seviye",
            value=f"{tier_label}\n`{yeni:g}M€`",
            inline=True
        )

        embed.add_field(
            name=f"📊 Değer Göstergesi (0–200M€)",
            value=f"`{bar}` **{yeni:g}M€**",
            inline=False
        )

        embed.add_field(
            name="📝 Güncelleme Sebebi",
            value=f"*{sebep}*",
            inline=False
        )

        embed.set_thumbnail(url=m.display_avatar.url)
        embed.set_footer(
            text=f"Yetkili: {ctx.author.display_name}  •  {zaman}",
            icon_url=ctx.author.display_avatar.url
        )

        await ctx.send(embed=embed)
        log = bot.get_channel(DEGER_LOG)
        if log:
            await log.send(embed=embed)

    except Exception as ex:
        print(ex)
        await ctx.send(
            embed=discord.Embed(
                title="❌ Komut Hatası",
                description="**Doğru kullanım:**\n`.değerver @üye 2M sebep`\n`.değersil @üye 2M sebep`",
                color=0xe74c3c
            )
        )

@bot.command(name='değerver')
@commands.has_permissions(manage_nicknames=True)
async def deger_ver(ctx, m: discord.Member, miktar: str, *, sebep: str = "Belirtilmedi"):
    await deger_guncelle(ctx, m, miktar, sebep, "artir")

@bot.command(name='değersil')
@commands.has_permissions(manage_nicknames=True)
async def deger_sil(ctx, m: discord.Member, miktar: str, *, sebep: str = "Belirtilmedi"):
    await deger_guncelle(ctx, m, miktar, sebep, "azalt")

@bot.command(name="endeğerli", aliases=["topoyuncu"])
async def en_degerli_listesi(ctx):
    oyuncular = []
    for uye in ctx.guild.members:
        if uye.bot or len(parcalar := uye.display_name.split(" | ")) < 4:
            continue
        try:
            deger = float(parcalar[3].upper().replace("M", "").replace("€", "").replace(",", ".").strip())
            oyuncular.append({
                "uye": uye,
                "isim": parcalar[0].strip(),
                "mevki": parcalar[1].strip(),
                "takim": parcalar[2].strip(),
                "deger": deger
            })
        except:
            continue

    if not oyuncular:
        return await ctx.send(
            embed=discord.Embed(
                title="❌ Oyuncu Bulunamadı",
                description="Değer bilgisi bulunan oyuncu yok.",
                color=0xe74c3c
            )
        )

    oyuncular.sort(key=lambda x: x["deger"], reverse=True)
    toplam_deger = sum(o["deger"] for o in oyuncular)
    ortalama = round(toplam_deger / len(oyuncular), 1)
    en_yuksek = oyuncular[0]["deger"]

    embed = discord.Embed(
        title="🏆 EN DEĞERLİ OYUNCULAR",
        color=0xffd700
    )
    if ctx.guild.icon:
        embed.set_author(name=f"{SUNUCU_ADI} | Piyasa Sıralaması", icon_url=ctx.guild.icon.url)

    siralama_emojiler = {1: "🥇", 2: "🥈", 3: "🥉"}
    yazi = ""
    for i, oyuncu in enumerate(oyuncular[:10], start=1):
        sira = siralama_emojiler.get(i, f"`{i:02d}`")
        tier_label, _ = deger_tier(oyuncu["deger"])
        yazi += (
            f"{sira} **{oyuncu['isim']}** — {oyuncu['uye'].mention}\n"
            f"┣ ⚽ `{oyuncu['mevki']}` • 🏟️ `{oyuncu['takim']}`\n"
            f"┗ 💰 **{oyuncu['deger']:g}M€**  {tier_label}\n\n"
        )

    embed.description = yazi

    embed.add_field(name="👥 Toplam Oyuncu", value=f"**{len(oyuncular)}**", inline=True)
    embed.add_field(name="📊 Lig Ortalaması", value=f"**{ortalama}M€**", inline=True)
    embed.add_field(name="💸 Toplam Piyasa", value=f"**{toplam_deger:g}M€**", inline=True)
    embed.add_field(
        name="📈 Piyasa Durumu",
        value=f"`{deger_bar(min(en_yuksek, 200))}` {en_yuksek:g}M€",
        inline=False
    )

    embed.set_footer(text=f"Sorgulayan: {ctx.author.display_name}  •  {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    await ctx.send(embed=embed)

# =============================================================
# 6. GERİ YÜKLENEN TÜM ESKİ KOMUTLAR
# =============================================================

# --- GENEL KOMUTLAR ---
@bot.command(name="şart")
async def sart_mesaji(ctx):
    rol_al_kanali_id = 1505490401690124288
    embed = discord.Embed(
        title="📢 Katılım Şartları",
        description=f"Lige katılabilmek veya devam edebilmek için lütfen <#{rol_al_kanali_id}> kanalından en az **1 adet rol** alınız.",
        color=discord.Color.blue(),
        timestamp=datetime.now(timezone.utc)
    )
    embed.add_field(name="📌 Önemli Not", value="İşlemleri tamamladıktan sonra yetkililere bilgi veriniz, size yardımcı olacaklardır.", inline=False)
    embed.set_footer(text=f"{SUNUCU_ADI} Kayıt Sistemi")
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="Rol Al Kanalına Git", url=f"https://discord.com/channels/{ctx.guild.id}/{rol_al_kanali_id}", style=discord.ButtonStyle.link))
    await ctx.send(embed=embed, view=view)

@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000) 
    await ctx.send(f"🏓 **Pong!** Buradayım kral, tıkır tıkır çalışıyorum. \n⚡ **Gecikme Süresi:** {latency}ms")    

# --- EĞLENCE KOMUTLARI ---
@bot.command(name='duello')
async def penalti_duellosu(ctx, rakip: discord.Member = None):
    koseler = ["sol", "orta", "sağ"]
    if rakip is None: # AI MOD
        await ctx.send(f"🏟️ {ctx.author.mention} vs 🧤 **KALECİ (AI)**\nİlk **5 gol** atan kazanır!")
        skor = {ctx.author: 0, "kaleci": 0}
        while skor[ctx.author] < 5 and skor["kaleci"] < 5:
            await ctx.send("🎯 Köşe seç: `sol / orta / sağ`")
            try:
                msg = await bot.wait_for('message', timeout=10, check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
                secim = msg.content.lower()
                if secim not in koseler: secim = random.choice(koseler)
            except asyncio.TimeoutError:
                secim = random.choice(koseler)
            kaleci = random.choice(koseler)
            await asyncio.sleep(1)
            if secim == kaleci:
                sonuc = "🧤 KALECİ KURTARDI!"; skor["kaleci"] += 1
            else:
                sonuc = "⚽ GOOOOOL!"; skor[ctx.author] += 1
            e = discord.Embed(description=f"{sonuc}\n\n👉 Sen: **{secim}** | Kaleci: **{kaleci}**\n📊 Skor: **{skor[ctx.author]} - {skor['kaleci']}**", color=0x3498db)
            await ctx.send(embed=e)
        kazanan_text = ctx.author.mention if skor[ctx.author] >= 5 else "🧤 KALECİ"
        await ctx.send(embed=discord.Embed(title="🏆 DÜELLO BİTTİ", description=f"🥇 Kazanan: {kazanan_text}", color=0x2ecc71))
        return
    if rakip == ctx.author: return await ctx.send("❓ Kendinle oynayamazsın!")
    await ctx.send(f"🏟️ {ctx.author.mention} vs {rakip.mention}\nİlk **5 gol** atan kazanır!")
    skor = {ctx.author: 0, rakip: 0}; siradaki = ctx.author
    while skor[ctx.author] < 5 and skor[rakip] < 5:
        await ctx.send(f"🎯 {siradaki.mention} şut atıyor! `sol / orta / sağ`")
        try:
            msg = await bot.wait_for('message', timeout=10, check=lambda m: m.author == siradaki and m.channel == ctx.channel)
            secim = msg.content.lower()
            if secim not in koseler: secim = random.choice(koseler)
        except asyncio.TimeoutError:
            secim = random.choice(koseler)
        kaleci = random.choice(koseler)
        await asyncio.sleep(1)
        if secim == kaleci: sonuc = "🧤 KALECİ KURTARDI!"
        else: sonuc = "⚽ GOOOOOL!"; skor[siradaki] += 1
        e = discord.Embed(description=f"{sonuc}\n\n👉 Şut: **{secim}** | Kaleci: **{kaleci}**\n📊 Skor: **{skor[ctx.author]} - {skor[rakip]}**", color=0x5865F2)
        await ctx.send(embed=e)
        siradaki = rakip if siradaki == ctx.author else ctx.author
    kazanan = ctx.author if skor[ctx.author] >= 5 else rakip
    await ctx.send(embed=discord.Embed(title="🏆 PENALTI DÜELLOSU BİTTİ", description=f"📊 Skor: **{skor[ctx.author]} - {skor[rakip]}**\n🥇 Kazanan: {kazanan.mention}", color=0x2ecc71))

@bot.command(name='yazıtura')
async def yazi_tura(ctx):
    mesaj = await ctx.send("🪙 Para havaya atılıyor...")
    animasyon = ["🪙", "💫", "🪙", "💫"]
    for a in animasyon:
        await asyncio.sleep(0.4)
        await mesaj.edit(content=a)
    sonuc = random.choice(["Yazı", "Tura"])
    e = discord.Embed(title="🪙 YAZI TURA", description=f"## {sonuc}", color=0xf1c40f)
    await mesaj.edit(content=None, embed=e)

@bot.command(name='roll')
async def roll(ctx, *, secenekler: Optional[str] = None):
    if secenekler is None:
        sonuc = str(random.randint(1, 10))
    else:
        if "," in secenekler: liste = [s.strip() for s in secenekler.split(",")]
        else: liste = secenekler.split()
        if len(liste) == 2 and liste[0].isdigit() and liste[1].isdigit():
            sonuc = str(random.randint(int(liste[0]), int(liste[1])))
        else:
            sonuc = random.choice(liste)
    e = discord.Embed(title="🎲 Roll Sonucu", color=0x5865F2, description=f"## 🎯 {sonuc}")
    e.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    e.set_footer(text=f"{datetime.now().strftime('%d.%m.%Y %H:%M')}")
    await ctx.send(embed=e)

@bot.command(name='ship')
async def ship_olcer(ctx, kisi1: Optional[discord.Member] = None, kisi2: Optional[discord.Member] = None):
    if kisi1 is None or kisi2 is None: return await ctx.send("❓ **Kullanım:** `.ship @kişi1 @kişi2`")
    oran = random.randint(0, 100)
    bar = "❤️" * int(oran / 10) + "🖤" * (10 - int(oran / 10))
    if oran < 20: yorum = "💔 Arkadaş kalmanız daha hayırlı gibi..."
    elif oran < 50: yorum = "👀 Biraz zorlansa olur gibi ama emin değilim."
    elif oran < 80: yorum = "💖 Vay canına! Aranızda ciddi bir çekim var."
    else: yorum = "💍 Nikah memurunu çağırın! Bu iş bitmiş. 🔥"
    embed = discord.Embed(title=f"💘 {SUNUCU_ADI} | Aşk Ölçer", description=f"{kisi1.mention} ❤️ {kisi2.mention}", color=0xff4757)
    embed.add_field(name=f"Aşk Oranı: %{oran}", value=bar, inline=False)
    embed.add_field(name="Sinyal:", value=yorum, inline=False)
    if kisi1.avatar: embed.set_thumbnail(url=kisi1.avatar.url)
    embed.set_footer(text=f"{ctx.author.display_name} tarafından eşleştirildi.")
    await ctx.send(embed=embed)

@bot.command(name='kaçcm')
async def kaccm(ctx, üye: discord.Member = None):
    üye = üye or ctx.author
    boy = random.randint(1,31)
    notlar = ""
    if boy == 31: notlar = "\n\n😏 *Sayı manidar...*"
    elif boy <= 5: notlar = "\n\n🤏 *Üzülme, karakteri yeter...*"
    elif boy >= 15: notlar = "\n\n🚀 *Maşallah, bu ne hal!*"
    e = discord.Embed(title="📏 Boy Ölçümü Yapıldı!", description=f"{üye.mention} kişisinin ölçümleri tamamlandı.\n\n**Sonuç:** `{boy}cm`{notlar}", color=0xff00ff)
    e.set_footer(text="Bu sonuçlar bilimsel bir değer taşımamaktadır.")
    await ctx.send(embed=e)

@bot.command(name='halısaha')
async def halisaha(ctx, rakip: discord.Member = None):
    if not rakip or rakip == ctx.author: return await ctx.send("⚽ Rakip etiketle! (`.halısaha @kişi`)")
    oyuncular = ["Ronaldo", "Messi", "Neymar", "Mbappe", "Haaland", "Salah", "De Bruyne", "Vinicius", "Benzema", "Kane"]
    gol_olaylari = []
    skor1, skor2 = 0, 0
    mesaj = await ctx.send("🏟️ Maç başlıyor...")
    for dakika in range(1, 91, 10):
        await asyncio.sleep(1)
        if random.random() < 0.4:
            atan = random.choice([ctx.author, rakip])
            oyuncu = random.choice(oyuncular)
            if atan == ctx.author: skor1 += 1; gol_olaylari.append(f"{dakika}' ⚽ {oyuncu} ({ctx.author.display_name})")
            else: skor2 += 1; gol_olaylari.append(f"{dakika}' ⚽ {oyuncu} ({rakip.display_name})")
        if dakika == 45: await mesaj.edit(content=f"⏸️ İlk yarı bitti!\n📊 {ctx.author.display_name} {skor1} - {skor2} {rakip.display_name}")
    embed = discord.Embed(title="🏟️ HALISAHA MAÇ SONUCU", description=f"📊 **{ctx.author.display_name} {skor1} - {skor2} {rakip.display_name}**", color=0x2ecc71)
    embed.add_field(name="⚽ Goller", value="\n".join(gol_olaylari) if gol_olaylari else "Gol olmadı 😐", inline=False)
    if skor1 > skor2: kazanan = ctx.author.mention
    elif skor2 > skor1: kazanan = rakip.mention
    else: kazanan = "🤝 Berabere"
    embed.add_field(name="🏆 Sonuç", value=kazanan, inline=False)
    embed.set_footer(text=f"{SUNUCU_ADI} Halısaha Sistemi")
    embed.set_image(url="https://media.giphy.com/media/3o7TKunL66O36RPh60/giphy.gif")
    if ctx.author.avatar: embed.set_thumbnail(url=ctx.author.avatar.url)
    await mesaj.edit(content="✅ Maç bitti!")
    await ctx.send(embed=embed)

class PenaltiV(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=20)
        self.ctx = ctx
        self.used = False
    async def sonuc(self, interaction, yon):
        if interaction.user.id != self.ctx.author.id or self.used: return
        self.used = True; self.clear_items()
        ihtimal = random.choices(["Gol", "Kaleci", "Aut", "Direk"], weights=[40, 30, 20, 10], k=1)[0]
        stat_ekle(str(self.ctx.author.id), 'penalti_atilan')
        if ihtimal == "Gol":
            stat_ekle(str(self.ctx.author.id), 'penalti_gol')
            baslik, renk, mesaj, gif = "⚽ GOOOOOL!", 0x2ecc71, f"**{yon} köşeye** mükemmel vuruş! Gol!", "https://media.tenor.com/3m8QvQ6qZQ0AAAAC/soccer-goal.gif"
        elif ihtimal == "Kaleci":
            baslik, renk, mesaj, gif = "🧤 KALECİ KURTARDI!", 0xe74c3c, f"Kaleci topu **{yon}** köşeden çıkardı!", "https://media.tenor.com/8J7f9K1gk9AAAAAC/goalkeeper-save.gif"
        elif ihtimal == "Aut":
            baslik, renk, mesaj, gif = "🏟️ AUT!", 0x95a5a6, f"Top çok farklı gitti! **{yon}** isabetsiz!", "https://media.tenor.com/6hQq9p2f9XAAAAAC/miss-shot.gif"
        else:
            baslik, renk, mesaj, gif = "💥 DİREK!", 0xf39c12, "İnanılmaz! Top direkten döndü!", "https://media.tenor.com/9pKx1d2fQ3MAAAAC/football-hit-post.gif"
        e = discord.Embed(title=baslik, description=f"## {mesaj}", color=renk)
        e.add_field(name="🎯 Vuruş", value=yon, inline=True).add_field(name="🥅 Sonuç", value=ihtimal, inline=True)
        e.set_image(url=gif).set_footer(text=f"{self.ctx.author.display_name} • Penaltı Sistemi")
        await interaction.response.edit_message(embed=e, view=self)
    @discord.ui.button(label="Sol", style=discord.ButtonStyle.primary, emoji="⬅️")
    async def sol(self, interaction, button): await self.sonuc(interaction, "Sol")
    @discord.ui.button(label="Orta", style=discord.ButtonStyle.primary, emoji="↕️")
    async def orta(self, interaction, button): await self.sonuc(interaction, "Orta")
    @discord.ui.button(label="Sağ", style=discord.ButtonStyle.primary, emoji="➡️")
    async def sag(self, interaction, button): await self.sonuc(interaction, "Sağ")

@bot.command(name='penaltı')
async def penalti(ctx):
    e = discord.Embed(title="🥅 Penaltı Noktası", description="Kaleci hazır... Köşeni seç ve şutunu çek!", color=0x3498db)
    if ctx.author.avatar: e.set_thumbnail(url=ctx.author.avatar.url)
    e.set_footer(text="⏱️ 20 saniye içinde karar ver!")
    await ctx.send(embed=e, view=PenaltiV(ctx))

@bot.command(name='çiz')
async def ciz(ctx):
    async with ctx.typing():
        buf = generate_figure()
        file = discord.File(buf, filename="figure.png")
        embed = discord.Embed(title="🎨 Çizim Hazır!", color=0xe74c3c)
        embed.set_image(url="attachment://figure.png")
        embed.set_footer(text=f"{SUNUCU_ADI} • {ctx.author.display_name}")
        await ctx.send(embed=embed, file=file)

# --- KAYIT VE KULLANICI İŞLEMLERİ ---
class KayitButonlari(discord.ui.View):
    def __init__(self, hedef_uye: discord.Member):
        super().__init__(timeout=60)
        self.hedef_uye = hedef_uye
    async def on_timeout(self):
        for item in self.children: item.disabled = True
    async def rol_ata(self, interaction: discord.Interaction, rol_id: int, rol_adi: str):
        if not self.hedef_uye or not isinstance(interaction.user, discord.Member): return
        if not (interaction.user.get_role(KAYIT_YETKILI_ROL_ID) or interaction.user.guild_permissions.administrator):
            return await interaction.response.send_message("❌ Yetkin yok!", ephemeral=True)
        guild = interaction.guild
        meslek_rolu = guild.get_role(rol_id)
        kayitli_rolu = guild.get_role(ROLLER["kayitli"])
        kayitsiz_rolu = guild.get_role(ROLLER["kayitsiz"])
        try:
            await self.hedef_uye.remove_roles(kayitsiz_rolu)
            await self.hedef_uye.add_roles(meslek_rolu, kayitli_rolu)
        except discord.Forbidden:
            return await interaction.response.send_message("❌ Bot rolü yetkisiz!", ephemeral=True)

        hesap_yasi = (datetime.now(timezone.utc) - self.hedef_uye.created_at).days
        embed = discord.Embed(title="✅ KAYIT TAMAMLANDI", color=0x00ff99, timestamp=datetime.now(timezone.utc))
        embed.add_field(name="👤 Oyuncu", value=self.hedef_uye.mention, inline=True)
        embed.add_field(name="⚽ Rol", value=rol_adi, inline=True)
        embed.add_field(name="🛡️ Durum", value="Kayıtlı", inline=True)
        embed.add_field(name="📛 Nick", value=self.hedef_uye.display_name, inline=False)
        embed.add_field(name="📅 Hesap Yaşı", value=f"{hesap_yasi} gün", inline=True)
        embed.add_field(name="👑 Yetkili", value=interaction.user.mention, inline=True)
        embed.set_thumbnail(url=self.hedef_uye.display_avatar.url)
        embed.set_footer(text=f"{SUNUCU_ADI} Registration System")
        sohbet_kanal = guild.get_channel(SOHBET_KANAL_ID)
        if sohbet_kanal: await sohbet_kanal.send(content=f"🎉 {self.hedef_uye.mention} aramıza katıldı!", embed=embed)
        log_kanal = guild.get_channel(LOG_KANAL_ID)
        if log_kanal and log_kanal != sohbet_kanal: await log_kanal.send(embed=embed)
        await interaction.response.send_message("✅ Kayıt tamamlandı.", ephemeral=True)
        if interaction.message: await interaction.message.delete()

    @discord.ui.button(label="Futbolcu", emoji="⚽", style=discord.ButtonStyle.primary)
    async def futbolcu_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.rol_ata(interaction, ROLLER["futbolcu"], "Futbolcu")
    @discord.ui.button(label="Teknik Direktör", emoji="👑", style=discord.ButtonStyle.danger)
    async def td_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.rol_ata(interaction, ROLLER["teknik direktör"], "Teknik Direktör")

@bot.command(name="kayıt", aliases=["k"])
async def kayit(ctx, uye: discord.Member, *, isim: str):
    if not (ctx.author.guild_permissions.administrator or ctx.author.get_role(KAYIT_YETKILI_ROL_ID)):
        return await ctx.send("❌ Kayıt yetkin yok!")
    await uye.edit(nick=isim)
    panel = discord.Embed(title=f"⚡ {SUNUCU_ADI} KAYIT PANELİ", description=f"{uye.mention} için rol seçiniz.\n\n👤 Kullanıcı: **{uye.name}**\n🆔 ID: `{uye.id}`", color=0x7c3aed)
    panel.set_thumbnail(url=uye.display_avatar.url)
    panel.set_footer(text=f"Kayıt Yetkilisi: {ctx.author.display_name}")
    await ctx.send(embed=panel, view=KayitButonlari(uye))
    stat_ekle(str(ctx.author.id), 'kayit_yapildi')

@bot.command(name='kver')
@commands.has_permissions(manage_roles=True)
async def kayitsiz_ver(ctx, m: discord.Member):
    ks_rol = ctx.guild.get_role(KAYITSIZ_ROL_ID)
    if not ks_rol: return await ctx.send("❌ Kayıtsız rolü ID'si bulunamadı!")
    try:
        await m.edit(roles=[ks_rol])
        e = discord.Embed(title="🚪 Üye Kayıtsıza Atıldı", color=0x34495e, description=f"{m.mention} üzerindeki tüm roller temizlendi ve **Kayıtsız** rolü verildi.")
        e.add_field(name="👑 Yetkili:", value=ctx.author.mention, inline=True)
        if m.avatar: e.set_thumbnail(url=m.avatar.url)
        e.set_footer(text=f"{SUNUCU_ADI} • {datetime.now().strftime('%H:%M')}")
        await ctx.send(embed=e)
    except discord.Forbidden:
        await ctx.send("❌ **Hata:** Botun yetkisi bu üyeyi düzenlemeye yetmiyor!")

# --- EKONOMİ ---
@bot.command(name='para')
async def para_goster(ctx, uye: discord.Member = None):
    uye = uye or ctx.author
    data, kullanici = get_user_para_data(uye.id)
    toplam = kullanici["cash"] + kullanici["bank"]
    embed = discord.Embed(title="💰 Cüzdan Bilgileri", color=0xf1c40f)
    embed.set_author(name=uye.display_name, icon_url=uye.display_avatar.url)
    embed.add_field(name="💵 Nakit", value=f"**{kullanici['cash']:,}₺**", inline=True)
    embed.add_field(name="🏦 Banka", value=f"**{kullanici['bank']:,}₺**", inline=True)
    embed.add_field(name="📊 Toplam", value=f"**{toplam:,}₺**", inline=True)
    embed.set_footer(text=f"{SUNUCU_ADI} • Ekonomi Sistemi")
    await ctx.send(embed=embed)

@bot.command(name='deposit', aliases=["yatır"])
async def deposit(ctx, miktar: int):
    if miktar <= 0:
        return await ctx.send("❌ Geçersiz miktar!", delete_after=5)
    data, kullanici = get_user_para_data(ctx.author.id)
    if kullanici["cash"] < miktar:
        return await ctx.send(f"❌ Yeterli nakit yok! Nakitin: **{kullanici['cash']:,}₺**", delete_after=5)
    kullanici["cash"] -= miktar
    kullanici["bank"] += miktar
    veri_kaydet(PARA_DOSYA, data)
    embed = discord.Embed(title="🏦 Para Yatırıldı", color=0x2ecc71,
        description=f"**{miktar:,}₺** bankana yatırıldı.\n\n💵 Nakit: **{kullanici['cash']:,}₺**\n🏦 Banka: **{kullanici['bank']:,}₺**")
    embed.set_footer(text=f"{SUNUCU_ADI} • Ekonomi Sistemi")
    await ctx.send(embed=embed)

@bot.command(name='withdraw', aliases=["çek"])
async def withdraw(ctx, miktar: int):
    if miktar <= 0:
        return await ctx.send("❌ Geçersiz miktar!", delete_after=5)
    data, kullanici = get_user_para_data(ctx.author.id)
    if kullanici["bank"] < miktar:
        return await ctx.send(f"❌ Bankanda yeterli para yok! Banka: **{kullanici['bank']:,}₺**", delete_after=5)
    kullanici["bank"] -= miktar
    kullanici["cash"] += miktar
    veri_kaydet(PARA_DOSYA, data)
    embed = discord.Embed(title="💵 Para Çekildi", color=0x3498db,
        description=f"**{miktar:,}₺** bankandan çekildi.\n\n💵 Nakit: **{kullanici['cash']:,}₺**\n🏦 Banka: **{kullanici['bank']:,}₺**")
    embed.set_footer(text=f"{SUNUCU_ADI} • Ekonomi Sistemi")
    await ctx.send(embed=embed)

@bot.command(name='pay', aliases=["ver", "gönder"])
async def pay(ctx, alici: discord.Member, miktar: int):
    if miktar <= 0:
        return await ctx.send("❌ Geçersiz miktar!", delete_after=5)
    if alici == ctx.author:
        return await ctx.send("❌ Kendine para gönderemezsin!", delete_after=5)
    data, gonderen = get_user_para_data(ctx.author.id)
    if gonderen["cash"] < miktar:
        return await ctx.send(f"❌ Yeterli nakit yok! Nakitin: **{gonderen['cash']:,}₺**", delete_after=5)
    _, alan = get_user_para_data(alici.id)
    gonderen["cash"] -= miktar
    alan["cash"] += miktar
    veri_kaydet(PARA_DOSYA, data)
    embed = discord.Embed(title="💸 Para Transferi", color=0x9b59b6,
        description=f"{ctx.author.mention} → {alici.mention}\n\n**{miktar:,}₺** başarıyla gönderildi!")
    embed.set_footer(text=f"{SUNUCU_ADI} • Ekonomi Sistemi")
    await ctx.send(embed=embed)

@bot.command(name='para-ver')
@commands.has_permissions(administrator=True)
async def para_ver_admin(ctx, uye: discord.Member, miktar: int):
    data, kullanici = get_user_para_data(uye.id)
    kullanici["cash"] += miktar
    veri_kaydet(PARA_DOSYA, data)
    embed = discord.Embed(title="✅ Para Verildi", color=0x2ecc71,
        description=f"{uye.mention} hesabına **{miktar:,}₺** eklendi.\n\n💵 Yeni nakit: **{kullanici['cash']:,}₺**")
    embed.set_footer(text=f"Yetkili: {ctx.author.display_name}")
    await ctx.send(embed=embed)

# --- GELİŞİM ---
@bot.command(name='ant')
@commands.cooldown(1, 3600, commands.BucketType.user)    
async def ant(ctx):
    if ctx.channel.id != ANTRENMAN_KANAL_ID:
        return await ctx.send(f"❌ Bu komutu sadece <#{ANTRENMAN_KANAL_ID}> kanalında kullanabilirsin!", delete_after=5)
    u = str(ctx.author.id)
    c = antrenman_sayaci.get(u, 0) + 1
    antrenman_sayaci[u] = c
    veri_kaydet(ANTRENMAN_DOSYA, antrenman_sayaci)
    stat_ekle(u, 'antrenman')
    progress = c % 10
    if progress != 0:
        bar = "🟦" * progress + "⬜" * (10 - progress)
        e = discord.Embed(title="🏃 ANTRENMAN DEVAM EDİYOR", description=f"⚽ Sahada yoğun çalışma...\n\n📊 İlerleme: **{progress}/10**\n📈 Genel Sayı: **{c}**\n{bar}\n\n💪 Kondisyon geliştiriliyor...", color=0x3498db)
        if ctx.author.avatar: e.set_thumbnail(url=ctx.author.avatar.url)
        e.set_footer(text=f"{ctx.author.display_name} sahada ter döküyor")
        await ctx.send(embed=e)
    else:
        antrenman_sayaci[u] = 0
        veri_kaydet(ANTRENMAN_DOSYA, antrenman_sayaci)
        e = discord.Embed(title="🔥 ANTRENMAN TAMAMLANDI!", description="⚽ Harika performans!\n\n💪 Fizik gücü arttı\n📈 Form seviyesi yükseldi\n💰 Değerini alabilirsin", color=0x2ecc71)
        if ctx.author.avatar: e.set_thumbnail(url=ctx.author.avatar.url)
        e.set_image(url="https://media1.tenor.com/m/dmH0nGUtvGQAAAAC/futbol-entrenar.gif")
        e.set_footer(text="Oyuncu gelişimi tamamlandı")
        await ctx.send(embed=e)
        bk = bot.get_channel(ANTRENMAN_BILDIRI_KANAL_ID)
        if bk:
            notify = discord.Embed(title="📢 OYUNCU GELİŞİMİ", description=f"⚽ {ctx.author.mention} antrenmanını tamamladı!", color=0xf1c40f)
            notify.add_field(name="🏆 Durum", value="Gelişim tamamlandı", inline=True)
            notify.add_field(name="💰 Ödül", value="Alınabilir", inline=True)
            await bk.send(content=f"<@&{DEGER_YETKILISI_ROL_ID}>", embed=notify)

# --- TRANSFER VE KULÜP İŞLEMLERİ ---
class TeamView(discord.ui.View):
    def __init__(self, takim_rolu: discord.Role):
        super().__init__(timeout=180)
        self.takim_rolu = takim_rolu
        self.message = None
    async def on_timeout(self):
        if self.message:
            try: await self.message.edit(view=None)
            except discord.NotFound: pass

    @discord.ui.button(label="Oyuncuları Göster", style=discord.ButtonStyle.secondary, emoji="👥")
    async def show_players(self, interaction: discord.Interaction, button: discord.ui.Button):
        futbolcu_rol = interaction.guild.get_role(FUTBOLCU_ROL_ID)
        if not futbolcu_rol:
            return await interaction.response.send_message("Sistemde 'Futbolcu' rolü bulunamadı.", ephemeral=True)
        oyuncular = [m for m in self.takim_rolu.members if futbolcu_rol in m.roles]
        if not oyuncular:
            return await interaction.response.send_message("Bu takımda lisanslı futbolcu yok.", ephemeral=True)
        liste = "\n".join(f"**{i}.** {oyuncu.mention} - `{oyuncu.display_name}`" for i, oyuncu in enumerate(oyuncular[:25], 1))
        embed = discord.Embed(title=f"⚽ {self.takim_rolu.name} Kadrosu", description=liste, color=self.takim_rolu.color)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Gizle & Kapat", style=discord.ButtonStyle.danger, emoji="🗑️")
    async def close_view(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.message:
            await self.message.delete()

@bot.command(name="takım")
async def takim_komutu(ctx, takim_rolu: discord.Role):
    td_rol = ctx.guild.get_role(TEKNIK_DIREKTOR_ROL_ID)
    kaptan_rol = ctx.guild.get_role(KAPTAN_ROL_ID)
    futbolcu_rol = ctx.guild.get_role(FUTBOLCU_ROL_ID)
    if not futbolcu_rol:
        return await ctx.send("Sistemde 'Futbolcu' rolü ayarlı değil.")

    oyuncular = [m for m in takim_rolu.members if futbolcu_rol in m.roles]
    teknik_direktor = next((m for m in takim_rolu.members if td_rol and td_rol in m.roles), None)
    kaptan = next((m for m in takim_rolu.members if kaptan_rol and kaptan_rol in m.roles), None)

    toplam_deger = 0
    for m in oyuncular:
        try:
            parcalar = m.display_name.split(" | ")
            if len(parcalar) >= 4:
                deger_str = parcalar[3].upper().replace("M€", "").replace("M", "").strip()
                toplam_deger += float(deger_str)
        except (ValueError, IndexError):
            continue

    embed = discord.Embed(title=f"{takim_rolu.name} Takım Formu", color=takim_rolu.color)
    if logo_url := TAKIM_LOGOLARI.get(takim_rolu.name):
        embed.set_thumbnail(url=logo_url)

    embed.add_field(name="Toplam Takım Değeri", value=f"**{toplam_deger:,.0f}M€**", inline=False)
    embed.add_field(name="Takım Etiketi", value=takim_rolu.mention, inline=False)
    embed.add_field(name="Teknik Direktör", value=teknik_direktor.mention if teknik_direktor else "-", inline=True)
    embed.add_field(name="Takım Kaptanı", value=kaptan.mention if kaptan else "-", inline=True)
    embed.add_field(name="Futbolcu Sayısı", value=f"{len(oyuncular)} Tescilli Oyuncu", inline=False)
    embed.set_footer(text="Kadro ve Pazar değerleri için aşağıdaki butonları kullanın.")

    view = TeamView(takim_rolu)
    message = await ctx.send(embed=embed, view=view)
    view.message = message

class TransferModal(Modal):
    def __init__(self, oyuncu: discord.Member, tip: str, mevki: str):
        self.oyuncu = oyuncu; self.tip = tip; self.mevki = mevki
        super().__init__(title=f"💰 {SUNUCU_ADI} | {tip} Formu")
        self.bedel = TextInput(label=f"Talep Edilen {tip} Bedeli 💵", placeholder="Örn: 228M€", required=True)
        self.rapor = TextInput(label="Teknik Heyet Raporu 📜", style=discord.TextStyle.paragraph, placeholder="Neden listeye eklendi?", required=True)
        self.add_item(self.bedel); self.add_item(self.rapor)
    async def on_submit(self, interaction: discord.Interaction):
        if not interaction.guild: return
        kanal = interaction.guild.get_channel(TRANSFER_LISTESI_ID)
        if not isinstance(kanal, discord.TextChannel): return await interaction.response.send_message("❌ Transfer kanalı bulunamadı!", ephemeral=True)
        tip_emoji = "💰" if self.tip == "Transfer" else "🤝"; tip_renk  = 0x1a1a2e if self.tip == "Transfer" else 0x0f3460
        embed = discord.Embed(color=tip_renk)
        embed.set_author(name=f"{SUNUCU_ADI} | {self.tip.upper()} LİSTESİ", icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        embed.description = f"**{interaction.user.mention}**, {self.oyuncu.mention} adlı oyuncuyu resmi olarak **{self.tip.lower()} listesine** ekledi. {tip_emoji}"
        embed.add_field(name="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", value="​", inline=False)
        embed.add_field(name="👤 Oyuncu", value=self.oyuncu.mention, inline=True).add_field(name="​", value="​", inline=True).add_field(name="👕 Mevki", value=f"`{self.mevki}`", inline=True)
        embed.add_field(name=f"{tip_emoji} {self.tip} Bedeli", value=f"**{self.bedel.value}**", inline=True).add_field(name="​", value="​", inline=True).add_field(name="🧑‍💼 Yetkili", value=interaction.user.mention, inline=True)
        embed.add_field(name="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", value="​", inline=False)
        embed.add_field(name="📝 Rapor", value=f"*{self.rapor.value}*", inline=False)
        if self.oyuncu.avatar: embed.set_thumbnail(url=self.oyuncu.avatar.url)
        embed.set_footer(text=f"{SUNUCU_ADI} • {datetime.now().strftime('%d.%m.%Y %H:%M')}")
        etiketler = f"<@&{BASKAN_ROL_ID}> <@&{TEKNIK_DIREKTOR_ROL_ID}> <@&{KAPTAN_ROL_ID}>"
        await kanal.send(content=etiketler, embed=embed)
        await interaction.response.send_message(embed=discord.Embed(description=f"✅ İlan başarıyla {kanal.mention} kanalına gönderildi.", color=0x2ecc71), ephemeral=True)

class TransferSecimView(View):
    def __init__(self, oyuncu: discord.Member, mevki: str):
        super().__init__(timeout=60); self.oyuncu = oyuncu; self.mevki = mevki
    @discord.ui.button(label="TRANSFER LİSTESİ", style=discord.ButtonStyle.success, emoji="💰")
    async def transfer_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(TransferModal(self.oyuncu, "Transfer", self.mevki))
    @discord.ui.button(label="KİRALIK LİSTESİ", style=discord.ButtonStyle.primary, emoji="🤝")
    async def kiralik_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(TransferModal(self.oyuncu, "Kiralık", self.mevki))

@bot.command(name='ilanver')
async def ilan_ver(ctx, üye: discord.Member, mevki: str):
    yetkililer = [BASKAN_ROL_ID, KAPTAN_ROL_ID, TEKNIK_DIREKTOR_ROL_ID]
    if not any(r.id in yetkililer for r in ctx.author.roles): return await ctx.send("❌ Yetkiniz yetersiz!", delete_after=5)
    if ctx.channel.id != ILAN_VER_KANAL_ID: return await ctx.send(f"❌ Bu komutu sadece <#{ILAN_VER_KANAL_ID}> kanalında kullanabilirsin!", delete_after=5)
    embed = discord.Embed(title=f"⚡ {SUNUCU_ADI} KULÜP YÖNETİMİ", description=f"**{üye.mention}** (**{mevki}**) için işlem türünü seçin: ⬇️", color=0x010101)
    await ctx.send(embed=embed, view=TransferSecimView(üye, mevki))

@bot.command(name='transfer')
@commands.has_permissions(manage_messages=True)
async def transfer(ctx, oyuncu: discord.Member, numara: str, sure: str, *, yeni_takim: str):
    embed = discord.Embed(title="🚨 HERE WE GO! 🚨", description=f"### {oyuncu.mention} artık **{yeni_takim}** başarısı için ter dökecek!", color=0x2ecc71)
    embed.add_field(name="👕 Forma Numarası", value=f"**#{numara}**", inline=True).add_field(name="📜 Sözleşme Süresi", value=f"**{sure}**", inline=True).add_field(name="🏟️ Yeni Kulübü", value=f"**{yeni_takim}**", inline=True)
    if ctx.message.attachments: foto_url = ctx.message.attachments[0].url
    else: foto_url = oyuncu.avatar.url if oyuncu.avatar else oyuncu.default_avatar.url
    embed.set_image(url=foto_url)
    embed.set_footer(text=f"{SUNUCU_ADI} Transfer Haberleri • Yetkili: {ctx.author.display_name}")
    await ctx.send(content=f"🔔 **SON DAKİKA:** {oyuncu.mention} transferi tamamlandı!", embed=embed)
    try: await ctx.message.delete()
    except: pass

@bot.command(name="takımara", aliases=["ara"])
@commands.cooldown(1, 60, commands.BucketType.user)
async def takim_ara(ctx, *, mesaj="Yeni oyuncu takım arıyor! ⚽"):
    td_rol = ctx.guild.get_role(ROLLER["teknik direktör"])
    kaptan_rol = ctx.guild.get_role(KAPTAN_ROL_ID)
    embed = discord.Embed(title="📢 TRANSFER DUYURUSU", description=f"⚽ **Yeni Oyuncu Takım Arıyor!**\n\n👤 Oyuncu: {ctx.author.mention}\n\n📝 Mesaj:\n> {mesaj}\n\n🏟️ Kaptanlar ve Teknik Direktörler ilgilenebilir!", color=0x00bfff)
    embed.set_thumbnail(url=ctx.author.display_avatar.url)
    embed.set_footer(text=f"{SUNUCU_ADI} Transfer Sistemi")
    await ctx.send(content=f"👔 {td_rol.mention if td_rol else ''} {kaptan_rol.mention if kaptan_rol else ''} yeni transfer fırsatı!", embed=embed)

@bot.command(name="kap")
async def kap(ctx, oyuncu: discord.Member, eski_takim: str, yeni_takim: str, ucret: str = "Açıklanmadı", sozlesme: str = "Açıklanmadı"):
    yetkililer = [DEGER_YETKILISI_ROL_ID, BASKAN_ROL_ID, TEKNIK_DIREKTOR_ROL_ID]
    if not any(ctx.author.get_role(r) for r in yetkililer): return await ctx.send("❌ Bu komut için yetkili rolü gerekli!", delete_after=5)
    tarih = datetime.now(timezone.utc).strftime("%d.%m.%Y %H:%M")
    embed = discord.Embed(title="📋 RESMİ TRANSFER BİLDİRİSİ", description=f"**{SUNUCU_ADI}** Kamuoyu Aydınlatma Platformu üzerinden aşağıdaki transfer resmi olarak tescil edilmiştir.", color=0x0d1b2a)
    embed.add_field(name="​", value="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", inline=False)
    embed.add_field(name="👤 Oyuncu", value=oyuncu.mention, inline=True).add_field(name="​", value="​", inline=True).add_field(name="📅 Transfer Tarihi", value=f"`{tarih}`", inline=True)
    embed.add_field(name="​", value="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", inline=False)
    embed.add_field(name="📤 Ayrılan Kulüp", value=f"**{eski_takim}**", inline=True).add_field(name="➡️", value="​", inline=True).add_field(name="📥 Katılan Kulüp", value=f"**{yeni_takim}**", inline=True)
    embed.add_field(name="​", value="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", inline=False)
    embed.add_field(name="💰 Transfer Bedeli", value=f"**{ucret}**", inline=True).add_field(name="​", value="​", inline=True).add_field(name="📋 Sözleşme Süresi", value=f"**{sozlesme}**", inline=True)
    embed.add_field(name="​", value="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", inline=False)
    if oyuncu.avatar: embed.set_thumbnail(url=oyuncu.avatar.url)
    if ctx.guild.icon: embed.set_author(name=f"{SUNUCU_ADI} | KAP Bildiri Sistemi", icon_url=ctx.guild.icon.url)
    embed.set_footer(text=f"Bu bildiri resmi nitelik taşımaktadır. • Yetkili: {ctx.author.display_name}")
    try: await ctx.message.delete()
    except: pass
    await ctx.send(content=oyuncu.mention, embed=embed)

# --- SUNUCU YÖNETİMİ VE ARAÇLAR ---
@bot.command(name='sil', aliases=['temizle', 'clear'])
@commands.has_permissions(manage_messages=True)
async def mesaj_sil(ctx, miktar: int = 10):
    if miktar > 100: miktar = 100
    deleted = await ctx.channel.purge(limit=miktar + 1)
    msg = await ctx.send(f"✅ **{len(deleted)-1}** adet mesaj başarıyla süpürüldü! 🧹")
    await asyncio.sleep(3)
    await msg.delete()

@bot.command(name='macsaati', aliases=['msaat', 'duyuru'])
@commands.has_permissions(manage_messages=True)
async def macsaati(ctx, ev_takim: discord.Role, dep_takim: discord.Role, saat: str):
    e = discord.Embed(title=f"🚨 {SUNUCU_ADI} | HAFTANIN MAÇI", description=f"Büyük randevu için hazırlanın! \n\n⚔️ {ev_takim.mention} **vs** {dep_takim.mention}", color=0xff0000)
    e.add_field(name="🏠 Ev Sahibi", value=ev_takim.mention, inline=True).add_field(name="✈️ Deplasman", value=dep_takim.mention, inline=True).add_field(name="⏰ Başlama Saati", value=f"**{saat}**", inline=False)
    e.set_thumbnail(url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExN3RreXByZzZ4Z3R6Z3R6Z3R6Z3R6Z3R6Z3R6Z3R6Z3R6JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/3o7TKMGpxxZ29D5S4o/giphy.gif")
    e.set_image(url="https://media1.tenor.com/m/dmH0nGUtvGQAAAAC/futbol-entrenar.gif")
    e.set_footer(text=f"Duyuruyu Yapan Hakem: {ctx.author.display_name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    e.timestamp = datetime.now(timezone.utc)
    await ctx.send(content=f"{ev_takim.mention} {dep_takim.mention} | **Maç saatiniz belli oldu!**", embed=e)

@bot.command(name='post')
@commands.cooldown(1, 60, commands.BucketType.user)
async def post_olustur(ctx, *, icerik: str = f"{SUNUCU_ADI} Paylaşımı"):
    if ctx.channel.id != INSTAGRAM_KANAL_ID: return await ctx.send(f"❌ Bu komutu sadece <#{INSTAGRAM_KANAL_ID}> kanalında kullanabilirsin!", delete_after=5)
    default_fotolar = ["https://source.unsplash.com/800x500/?football", "https://source.unsplash.com/800x500/?stadium"]
    if ctx.message.attachments and any(ctx.message.attachments[0].filename.lower().endswith(ext) for ext in ['png', 'jpg', 'jpeg', 'gif']):
        foto_url = ctx.message.attachments[0].url
    else: foto_url = random.choice(default_fotolar)
    embed = discord.Embed(description=f"**{ctx.author.display_name}**\n{icerik}", color=0xe1306c)
    embed.set_author(name=f"{ctx.author.display_name} • {SUNUCU_ADI}", icon_url=ctx.author.display_avatar.url)
    embed.set_image(url=foto_url)
    embed.add_field(name="❤️ Beğeni", value=f"**{random.randint(100, 1500)}**", inline=True).add_field(name="💬 Yorum", value=f"**{random.randint(5, 150)}**", inline=True)
    embed.add_field(name="💭 Öne çıkan yorum", value=random.choice(["🔥 Efsane olmuş!", "⚽ Kral hareket!", "💯 Bu ne kalite!"]), inline=False)
    embed.set_footer(text=f"{ctx.author.display_name} • Paylaşım")
    mesaj = await ctx.send(embed=embed)
    stat_ekle(str(ctx.author.id), 'post')
    await mesaj.add_reaction("❤️"); await mesaj.add_reaction("💬"); await mesaj.add_reaction("🔥")
    try: await ctx.message.delete()
    except: pass

@bot.command(name="toplurolver")
@commands.has_permissions(manage_roles=True)
async def toplurolver(ctx, *args: Union[discord.Member, discord.Role]):
    if len(args) < 2: return await ctx.send("❌ **Eksik Kullanım!**\nDoğrusu: `.toplurolver @kişi @kişi @rol`")
    members = [a for a in args if isinstance(a, discord.Member)]
    roles = [a for a in args if isinstance(a, discord.Role)]
    if not roles: return await ctx.send("❌ **Hata:** En az bir rol etiketlemelisin!")
    target_role = roles[0]
    msg = await ctx.send(f"🔄 **{len(members)}** kullanıcı için **{target_role.name}** rolü dağıtılıyor...")
    basarili, hata = [], []
    for member in members:
        try:
            if target_role not in member.roles:
                await member.add_roles(target_role)
                basarili.append(f"`{member.name}`")
        except: hata.append(f"`{member.name}`")
    sonuc_embed = discord.Embed(title=f"🛡️ {SUNUCU_ADI} | İşlem Raporu", color=0x2ecc71, timestamp=ctx.message.created_at)
    sonuc_embed.add_field(name="📦 Verilen Rol", value=target_role.mention, inline=False)
    if basarili: sonuc_embed.add_field(name="✅ Başarılı", value=", ".join(basarili), inline=False)
    if hata: sonuc_embed.add_field(name="⚠️ Hata/Yetki Yetersiz", value=", ".join(hata), inline=False)
    sonuc_embed.set_footer(text=f"Komutu Kullanan: {ctx.author.name}")
    await msg.edit(content=None, embed=sonuc_embed)

# --- TICKET SİSTEMİ ---
TICKET_KATEGORILER = [
    discord.SelectOption(label="Transfer İşlemi",  description="Oyuncu transferi veya bonservis talebi", emoji="⚽"),
    discord.SelectOption(label="Değer / Bütçe", description="Değer güncelleme veya bütçe işlemleri", emoji="💰"),
    discord.SelectOption(label="Şikayet / Öneri", description="Şikayet bildir veya öneri sun", emoji="📋"),
    discord.SelectOption(label="Satın Alım", description="Sunucu içi satın alım işlemleri", emoji="🛒"),
    discord.SelectOption(label="Diğer", description="Yukarıdaki kategorilere uymayan talepler", emoji="🔧"),
]
class TicketDropdown(discord.ui.Select):
    def __init__(self):
        super().__init__(placeholder="📂 Talep kategorini seç...", options=TICKET_KATEGORILER, min_values=1, max_values=1)
    async def callback(self, interaction: discord.Interaction):
        guild, member = interaction.guild, interaction.user
        if not guild or not isinstance(member, discord.Member): return
        category = guild.get_channel(DESTEK_KATEGORI_ID)
        if not isinstance(category, discord.CategoryChannel):
            return await interaction.response.send_message("❌ Ticket kategorisi bulunamadı.", ephemeral=True)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
            guild.get_role(YETKILI_1_ID): discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True),
            guild.get_role(YETKILI_2_ID): discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True)
        }
        kanal_adi = f"🎫︱{member.display_name[:20].lower().replace(' ', '-')}"
        channel = await guild.create_text_channel(name=kanal_adi, category=category, overwrites=overwrites, topic=f"Talep sahibi: {member} | Kategori: {self.values[0]}")
        await interaction.response.send_message(f"✅ Destek kanalın oluşturuldu → {channel.mention}", ephemeral=True)
        embed = discord.Embed(title=f"🎫 {SUNUCU_ADI} — DESTEK TALEBİ", color=0x7c3aed)
        embed.add_field(name="👤 Talep Sahibi", value=member.mention, inline=True).add_field(name="📂 Kategori", value=f"`{self.values[0]}`", inline=True)
        embed.add_field(name="📌 Bilgi", value="Yetkililerimiz en kısa sürede seninle ilgilenecek.\nLütfen talebini **kısa ve net** şekilde açıkla.", inline=False)
        embed.set_footer(text="İşin bitince 'Kanalı Kapat' butonuna bas.")
        ping_str = f"<@&{YETKILI_1_ID}> <@&{YETKILI_2_ID}>"
        close_view = View(timeout=None)
        close_btn = Button(label="🔒 Kanalı Kapat", style=discord.ButtonStyle.danger)
        async def close_callback(inter: discord.Interaction):
            await inter.response.send_message("⚠️ Kanal **5 saniye** içinde siliniyor...")
            await asyncio.sleep(5)
            if isinstance(inter.channel, discord.TextChannel): await inter.channel.delete()
        close_btn.callback = close_callback
        close_view.add_item(close_btn)
        await channel.send(content=f"||{ping_str}|| → {member.mention}", embed=embed, view=close_view)
class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None); self.add_item(TicketDropdown())
@bot.command(name="ticket-kur")
@commands.has_permissions(administrator=True)
async def ticket_kur(ctx: commands.Context):
    if ctx.channel.id != TICKET_KANAL_ID: return await ctx.send(f"❌ Bu komutu sadece <#{TICKET_KANAL_ID}> kanalında kullanabilirsin!", delete_after=5)
    panel = discord.Embed(title=f"🎫 {SUNUCU_ADI} | DESTEK MERKEZİ", description="Sunucumuzda bir sorunla mı karşılaştın? Transfer, değer veya başka bir konuda yardım mı istiyorsun?\n\n**Aşağıdan kategorini seç** — yetkili ekibimiz sana özel kanal açsın.", color=0x7c3aed)
    if ctx.guild and ctx.guild.icon: panel.set_thumbnail(url=ctx.guild.icon.url)
    panel.set_footer(text=f"{SUNUCU_ADI} • Destek Merkezi")
    await ctx.message.delete()
    await ctx.send(embed=panel, view=TicketView())

# --- STATS & YARDIM ---
@bot.command(name="stat")
async def stat_goster(ctx, uye: discord.Member = None):
    uye = uye or ctx.author
    data = stat_oku()
    uid = str(uye.id)
    stats = data.get(uid, {})
    if not stats: return await ctx.send(f"❌ **{uye.display_name}** için kayıtlı stat bulunamadı!")
    embed = discord.Embed(title=f"📊 {uye.display_name} — İstatistikler", color=0x3498db)
    if uye.avatar: embed.set_thumbnail(url=uye.avatar.url)
    for key, isim in STAT_ISIMLER.items():
        if val := stats.get(key, 0): embed.add_field(name=isim, value=f"**{val}**", inline=True)
    if not embed.fields: embed.description = "Henüz hiç stat yok."
    embed.set_footer(text=f"{SUNUCU_ADI} • Stat Sistemi")
    await ctx.send(embed=embed)

@bot.command(name="stat-sıfırla")
@commands.has_permissions(administrator=True)
async def stat_sifirla(ctx, uye: discord.Member = None):
    data = stat_oku()
    if uye is None:
        count = len(data)
        data.clear()
        desc = f"**{count}** oyuncunun tüm statları temizlendi."
    else:
        uid = str(uye.id)
        if uid in data: data.pop(uid)
        desc = f"{uye.mention} adlı oyuncunun statları temizlendi."
    stat_yaz(data)
    embed = discord.Embed(title="🔄 Statlar Sıfırlandı", description=desc, color=0xe74c3c)
    embed.set_footer(text=f"{SUNUCU_ADI} • Yetkili: {ctx.author.display_name}")
    await ctx.send(embed=embed)

class HelpMenu(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=60); self.ctx = ctx
    async def interaction_check(self, interaction: discord.Interaction): return interaction.user == self.ctx.author
    def get_embed(self, title, fields):
        e = discord.Embed(title=f"📖 {SUNUCU_ADI} — {title}", color=0x7c3aed)
        for name, value in fields.items(): e.add_field(name=name, value=value, inline=False)
        e.set_footer(text="Prefix: .")
        return e
    @discord.ui.button(label="🏠 Ana Menü", style=discord.ButtonStyle.secondary, row=2)
    async def ana_menu(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=self.get_embed("Yardım Menüsü", {"Genel": "Aşağıdaki butonlardan bir kategori seçerek komutları inceleyebilirsin."}))
    @discord.ui.button(label="⚽ Oyunlar", style=discord.ButtonStyle.primary)
    async def oyunlar(self, interaction: discord.Interaction, button: discord.ui.Button):
        fields = {
            ".duello @kişi": "Penaltı düellosu yap.",
            ".halısaha @kişi": "Maç simülasyonu oyna.",
            ".penaltı": "Penaltı at.",
            ".yazıtura": "Yazı-tura oyna.",
            ".roll": "Rastgele sayı veya seçim yap.",
            ".ship @kişi1 @kişi2": "Aşk uyumunu ölç.",
            ".kaçcm": "Boyunu ölç."
        }
        await interaction.response.edit_message(embed=self.get_embed("Oyunlar", fields))
    @discord.ui.button(label="💰 Piyasa & Değer", style=discord.ButtonStyle.success)
    async def piyasa(self, interaction: discord.Interaction, button: discord.ui.Button):
        fields = {
            ".değerver @oyuncu 5M sebep": "Oyuncunun piyasa değerini artırır.",
            ".değersil @oyuncu 5M sebep": "Oyuncunun piyasa değerini düşürür.",
            ".endeğerli": "En değerli 10 oyuncuyu sıralar.",
            ".ant": "Antrenman yapar (saatlik).",
        }
        await interaction.response.edit_message(embed=self.get_embed("Piyasa & Değer", fields))
    @discord.ui.button(label="📋 Sunucu", style=discord.ButtonStyle.danger)
    async def sunucu(self, interaction: discord.Interaction, button: discord.ui.Button):
        fields = {
            ".kayıt @kişi <isim>": "Üye kaydı yap.",
            ".kver @kişi": "Üyeyi kayıtsıza at.",
            ".transfer ...": "Transfer duyurusu yap.",
            ".ilanver ...": "Transfer listesine oyuncu ekle.",
            ".macsaati ...": "Maç duyurusu yap.",
            ".post <içerik>": "Instagram tarzı post at.",
            ".takım @rol": "Takım bilgilerini gösterir.",
            ".ara": "Takım aradığını duyur."
        }
        await interaction.response.edit_message(embed=self.get_embed("Sunucu", fields))
    @discord.ui.button(label="🛠️ Araçlar", style=discord.ButtonStyle.secondary)
    async def araclar(self, interaction: discord.Interaction, button: discord.ui.Button):
        fields = {
            ".sil <miktar>": "Mesajları temizle.",
            ".toplurolver @kişiler @rol": "Toplu rol ver.",
            ".ticket-kur": "(Admin) Ticket panelini kurar.",
            ".stat [@kişi]": "Kullanıcı istatistiklerini gösterir."
        }
        await interaction.response.edit_message(embed=self.get_embed("Araçlar", fields))

@bot.command(name="help", aliases=["yardım"])
async def help_menu(ctx):
    view = HelpMenu(ctx)
    await ctx.send(embed=view.get_embed("Yardım Menüsü", {"Genel": "Aşağıdaki butonlardan bir kategori seçerek komutları inceleyebilirsin."}), view=view)

# --- BOT YÖNETİMİ ---
@bot.command(name="sunucuyakatıl")
async def sunucuya_katil(ctx, sunucu_id: int):
    if ctx.author.id != OWNER_ID:
        return await ctx.send("❌ Bu komutu sadece bot sahibi kullanabilir!", delete_after=5)

    invite_url = (
        f"https://discord.com/oauth2/authorize"
        f"?client_id={bot.user.id}"
        f"&permissions=8"
        f"&scope=bot"
        f"&guild_id={sunucu_id}"
    )

    embed = discord.Embed(
        title="🔗 Sunucuya Katılım Linki",
        description=(
            f"**Sunucu ID:** `{sunucu_id}`\n\n"
            f"Aşağıdaki butona tıklayarak botu o sunucuya ekleyebilirsin.\n"
            f"⚠️ O sunucuda **Yönetici** yetkine sahip olman gerekiyor."
        ),
        color=0x7c3aed
    )
    embed.set_footer(text=f"{SUNUCU_ADI} • Bot Yönetimi")

    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="Sunucuya Ekle", url=invite_url, style=discord.ButtonStyle.link, emoji="🤖"))

    try:
        await ctx.author.send(embed=embed, view=view)
        await ctx.send("✅ Link DM kutuna gönderildi!", delete_after=5)
    except discord.Forbidden:
        await ctx.send(embed=embed, view=view)

@bot.command(name="sunucular")
@commands.is_owner()
async def sunucular(ctx):
    liste = ""
    for i, guild in enumerate(bot.guilds, 1):
        liste += f"**{i}. {guild.name}** | Üye: {guild.member_count}\n"
    embed = discord.Embed(title="📊 Botun Sunucuları", description=liste, color=0x2b2d31)
    try:
        await ctx.author.send(embed=embed)
        await ctx.send("✅ Sunucu listesi DM kutuna gönderildi.", delete_after=5)
    except discord.Forbidden:
        await ctx.send("❌ DM kutun kapalı olduğu için listeyi gönderemedim!")

@bot.command(name="ayrıl")
@commands.is_owner()
async def ayril(ctx, sunucu_id: int):
    guild = bot.get_guild(sunucu_id)
    if guild:
        await guild.leave()
        await ctx.send(f"✅ **{guild.name}** sunucusundan ayrıldım.")
    else:
        await ctx.send(f"❌ `{sunucu_id}` ID'li sunucu bulunamadı.")

@bot.command(name="buserverdışıheryerdenayrıl")
@commands.is_owner()
async def buserverdışıheryerdenayrıl(ctx):
    mevcut_sunucu_id = ctx.guild.id
    sayac = 0
    for guild in bot.guilds:
        if guild.id != mevcut_sunucu_id:
            await guild.leave()
            sayac += 1
    await ctx.send(f"✅ Bu sunucu dışındaki **{sayac}** sunucudan ayrıldım.")

# =============================================================
# 7. BOTU BAŞLATMA
# =============================================================
@tasks.loop(minutes=4)
async def self_ping():
    pass 

if __name__ == "__main__":
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        print("❌ HATA: DISCORD_TOKEN ortam değişkeni bulunamadı!")
    else:
        try:
            keep_alive()
            print("✅ Keep-alive sunucusu başlatıldı.")
        except Exception as e:
            print(f"⚠️ Keep-alive başlatılamadı: {e}")

        print("🚀 Bot başlatılıyor...")
        bot.run(token)
