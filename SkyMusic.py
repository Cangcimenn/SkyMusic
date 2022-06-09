import os
import glob
import json
import logging
import asyncio
import youtube_dl
from pytgcalls import StreamType
from pytube import YouTube
from youtube_search import YoutubeSearch
from pytgcalls import PyTgCalls, idle
from pytgcalls.types import Update
from pyrogram.raw.base import Update
from pytgcalls.types import AudioPiped, AudioVideoPiped
from pytgcalls.types import (
    HighQualityAudio,
    HighQualityVideo,
    LowQualityVideo,
    MediumQualityVideo
)
from pytgcalls.types.stream import StreamAudioEnded, StreamVideoEnded
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.errors import UserAlreadyParticipant, UserNotParticipant
from helpers.queues import QUEUE, add_to_queue, get_queue, clear_queue, pop_an_item
from helpers.admin_check import *

bot = Client(
    "Anonymous",
    bot_token = os.environ["BOT_TOKEN"],
    api_id = int(os.environ["API_ID"]),
    api_hash = os.environ["API_HASH"]
)

client = Client(os.environ["SESSION_NAME"], int(os.environ["API_ID"]), os.environ["API_HASH"])

app = PyTgCalls(client)

OWNER_ID = int(os.environ["OWNER_ID"])
SUPPORT = os.environ["SUPPORT"]

LIVE_CHATS = []

START_TEXT = """<b>ʜᴇʏ {},</b> 🖤
✨ <b>ꜱᴀʏᴀ ᴀᴅᴀʟᴀʜ ꜱᴋʏ ᴍᴜꜱɪᴄ ʙᴏᴛ.</b>
<b>ʏᴀɴɢ ᴅɪʙᴜᴀᴛ ᴜɴᴛᴜᴋ ᴍᴇɴᴇᴍᴀɴɪ ᴋᴇɢᴀʙᴜᴛᴀɴ ᴋᴀʟɪᴀɴ ᴅɪ ᴛᴇʟᴇɢʀᴀᴍ.</b>
<b>ꜱᴇᴍᴜᴀ ᴘᴇʀɪɴᴛᴀʜ ꜱᴀʏᴀ ᴛᴇʀᴄᴀɴᴛᴜᴍ ᴅɪ ᴛᴏᴍʙᴏʟ ʙᴀɴᴛᴜᴀɴ.</b>
"""

HELP_TEXT = """<b>» ᴍᴀɪɴ ᴄᴏᴍᴍᴀɴᴅꜱ «</b>
» /play (sᴏɴɢ/ʏᴛ ʟɪɴᴋ) : ᴩʟᴀʏ's ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ sᴏɴɢ ᴀs ᴀᴜᴅɪᴏ.
» /vplay (sᴏɴɢ/ʏᴛ ʟɪɴᴋ) : ᴩʟᴀʏ's ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ sᴏɴɢ ᴀs ᴠɪᴅᴇᴏ.
» /pause : ᴩᴀᴜsᴇ ᴛʜᴇ ᴏɴɢᴏɪɴɢ sᴛʀᴇᴀᴍ.
» /resume : ʀᴇsᴜᴍᴇ ᴛʜᴇ ᴩᴀᴜsᴇᴅ sᴛʀᴇᴀᴍ.
» /skip : sᴋɪᴩ ᴛᴏ ᴛʜᴇ ɴᴇxᴛ ᴛʀᴀᴄᴋ ɪɴ ǫᴜᴇᴜᴇ.
» /end : ᴄʟᴇᴀʀs ᴛʜᴇ ǫᴜᴇᴜᴇ ᴀɴᴅ ʟᴇᴀᴠᴇ ᴠɪᴅᴇᴏᴄʜᴀᴛ.
» /playlist : sʜᴏᴡs ᴛʜᴇ ʟɪsᴛ ᴏғ ǫᴜᴇᴜᴇᴅ ᴛʀᴀᴄᴋs.
» /join or /userbotjoin : ʀᴇǫᴜᴇsᴛs ᴛʜᴇ ᴀssɪsᴛᴀɴᴛ ᴛᴏ ᴊᴏɪɴ ʏᴏᴜʀ ᴄʜᴀᴛ.
» /restart : ʀᴇsᴛᴀʀᴛs ᴛʜᴇ ʙᴏᴛ.
💻<b><u>ᴍᴀᴅᴇ ʙʏ ♥ SKY ♥</u></b>"""

START_IMG = "https://telegra.ph/file/95f64da5d816bcd511c65.jpg"

START_BUTTONS = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                        "ᴀᴅᴅ ꜱᴋʏ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ", url="https://t.me/skymusicbot?startgroup=true")
        ],
        [   
            InlineKeyboardButton("ᴅᴇᴠᴇʟᴏᴘᴇʀ", user_id=1356469075),
            InlineKeyboardButton("sᴜᴩᴩᴏʀᴛ", url=f"https://t.me/{SUPPORT}")
        ],
        [
            InlineKeyboardButton("sᴏᴜʀᴄᴇ ᴋᴏᴅᴇ", url="https://github.com/Cangcimenn/SkyMusic")
        ]
    ]
)

HELP_BUTTON = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("​ᴄʟᴏsᴇ​", callback_data="close")
        ]
    ]
)

BUTTONS = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("▷", callback_data="resume"),
            InlineKeyboardButton("II", callback_data="pause"),
            InlineKeyboardButton("‣‣I", callback_data="skip"),
            InlineKeyboardButton("▢", callback_data="end"),
        ],
        [
            InlineKeyboardButton("​ᴄʟᴏsᴇ​", callback_data="close")
        ]
    ]
)

async def skip_current_song(chat_id):
    if chat_id in QUEUE:
        chat_queue = get_queue(chat_id)
        if len(chat_queue) == 1:
            await app.leave_group_call(chat_id)
            clear_queue(chat_id)
            return 1
        else:
            title = chat_queue[1][0]
            duration = chat_queue[1][1]
            link = chat_queue[1][2]
            playlink = chat_queue[1][3]
            type = chat_queue[1][4]
            Q = chat_queue[1][5]
            thumb = chat_queue[1][6]
            if type == "Audio":
                await app.change_stream(
                    chat_id,
                    AudioPiped(
                        playlink,
                    ),
                )
            elif type == "Video":
                if Q == "high":
                    hm = HighQualityVideo()
                elif Q == "mid":
                    hm = MediumQualityVideo()
                elif Q == "low":
                    hm = LowQualityVideo()
                else:
                    hm = MediumQualityVideo()
                await app.change_stream(
                    chat_id, AudioVideoPiped(playlink, HighQualityAudio(), hm)
                )
            pop_an_item(chat_id)
            await bot.send_photo(chat_id, photo = thumb,
                                 caption = f"🕕 <b>ᴅᴜʀᴀᴛɪᴏɴ:</b> {duration}",
                                 reply_markup = BUTTONS)
            return [title, link, type, duration, thumb]
    else:
        return 0


async def skip_item(chat_id, lol):
    if chat_id in QUEUE:
        chat_queue = get_queue(chat_id)
        try:
            x = int(lol)
            title = chat_queue[x][0]
            chat_queue.pop(x)
            return title
        except Exception as e:
            print(e)
            return 0
    else:
        return 0


@app.on_stream_end()
async def on_end_handler(_, update: Update):
    if isinstance(update, StreamAudioEnded):
        chat_id = update.chat_id
        await skip_current_song(chat_id)


@app.on_closed_voice_chat()
async def close_handler(client: PyTgCalls, chat_id: int):
    if chat_id in QUEUE:
        clear_queue(chat_id)
        

async def yt_video(link):
    proc = await asyncio.create_subprocess_exec(
        "yt-dlp",
        "-g",
        "-f",
        "best[height<=?720][width<=?1280]",
        f"{link}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if stdout:
        return 1, stdout.decode().split("\n")[0]
    else:
        return 0, stderr.decode()
    

async def yt_audio(link):
    proc = await asyncio.create_subprocess_exec(
        "yt-dlp",
        "-g",
        "-f",
        "bestaudio",
        f"{link}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if stdout:
        return 1, stdout.decode().split("\n")[0]
    else:
        return 0, stderr.decode()


@bot.on_callback_query()
async def callbacks(_, cq: CallbackQuery):
    user_id = cq.from_user.id
    try:
        user = await cq.message.chat.get_member(user_id)
        admin_strings = ("creator", "administrator")
        if user.status not in admin_strings:
            is_admin = False
        else:
            is_admin = True
    except ValueError:
        is_admin = True        
    if not is_admin:
        return await cq.answer("» ᴀɴᴅᴀ ᴛɪᴅᴀᴋ ᴅɪᴘᴇʀʙᴏʟᴇʜᴋᴀɴ ᴍᴇɴɢɢᴜɴᴀᴋᴀɴ ᴘᴇʀɪɴᴛᴀʜ ɪɴɪ.")   
    chat_id = cq.message.chat.id
    data = cq.data
    if data == "close":
        return await cq.message.delete()
    if not chat_id in QUEUE:
        return await cq.answer("» ᴛɪᴅᴀᴋ ᴀᴅᴀ ʏᴀɴɢ ᴅɪᴍᴀɪɴᴋᴀɴ.")

    if data == "pause":
        try:
            await app.pause_stream(chat_id)
            await cq.answer("» ʟᴀɢᴜ ʙᴇʀʜᴀꜱɪʟ ᴅɪᴊᴇᴅᴀ.")
        except:
            await cq.answer("» ᴛɪᴅᴀᴋ ᴀᴅᴀ ʏᴀɴɢ ᴅɪᴍᴀɪɴᴋᴀɴ..")
      
    elif data == "resume":
        try:
            await app.resume_stream(chat_id)
            await cq.answer("» ʟᴀɢᴜ ʙᴇʀʜᴀꜱɪʟ ᴅɪʟᴀɴᴊᴜᴛᴋᴀɴ.")
        except:
            await cq.answer("» ᴛɪᴅᴀᴋ ᴀᴅᴀ ʏᴀɴɢ ᴅɪᴍᴀɪɴᴋᴀɴ.")   

    elif data == "end":
        await app.leave_group_call(chat_id)
        clear_queue(chat_id)
        await cq.answer("» ʟᴀɢᴜ ʙᴇʀʜᴀꜱɪʟ ᴅɪᴀᴋʜɪʀɪ.")  

    elif data == "skip":
        op = await skip_current_song(chat_id)
        if op == 0:
            await cq.answer("» ᴀɴᴛʀɪᴀɴ ᴋᴏꜱᴏɴɢ..")
        elif op == 1:
            await cq.answer("» ᴀɴᴛʀɪᴀɴ ᴋᴏꜱᴏɴɢ, ꜱᴛʀᴇᴀᴍɪɴɢ ᴛᴇʀᴛᴜᴛᴜᴘ.")
        else:
            await cq.answer("» ʟᴀɢᴜ ʙᴇʀʜᴀꜱɪʟ ᴅɪʟᴇᴡᴀᴛɪ.")


@bot.on_message(filters.command("start") & filters.private)
async def start_private(_, message):
    msg = START_TEXT.format(message.from_user.mention)
    await message.reply_photo(photo = START_IMG,
                              caption = msg,
                             reply_markup = START_BUTTONS)
    
@bot.on_message(filters.command(["help", "cmd", "cmds", "commands"]) & filters.private)
async def help_cmd(_, message):
    await message.reply_photo(photo = START_IMG,
                              caption = HELP_TEXT,
                             reply_markup = HELP_BUTTON)

@bot.on_message(filters.command(["ping", "alive"]) & filters.group)
async def start_group(_, message):
    await message.delete()
    fuk = "<b>ᴩᴏɴɢ ᴍᴜꜱɪᴄ !</b>"
    await message.reply_photo(photo="https://telegra.ph/file/95f64da5d816bcd511c65.jpg", caption=fuk)


@bot.on_message(filters.command(["join", "userbotjoin", "assistant", "ass"]) & filters.group)
@is_admin
async def join_chat(c: Client, m: Message):
    chat_id = m.chat.id
    try:
        invitelink = await c.export_chat_invite_link(chat_id)
        if invitelink.startswith("https://t.me/+"):
            invitelink = invitelink.replace(
                "https://t.me/+", "https://t.me/joinchat/"
            )
            await client.join_chat(invitelink)
            return await client.send_message(chat_id, "**» ᴀssɪsᴛᴀɴᴛ ʙᴇʀʜᴀꜱɪʟ ʙᴇʀɢᴀʙᴜɴɢ ᴅᴇɴɢᴀɴ ᴏʙʀᴏʟᴀɴ.**")
    except UserAlreadyParticipant:
        return await client.send_message(chat_id, "**» ᴀssɪsᴛᴀɴᴛ ꜱᴜᴅᴀʜ ʙᴇʀɢᴀʙᴜɴɢ ᴅᴇɴɢᴀɴ ᴏʙʀᴏʟᴀɴ.**")

    
@bot.on_message(filters.command(["play", "vplay"]) & filters.group)
async def video_play(_, message):
    await message.delete()
    user_id = message.from_user.id
    state = message.command[0].lower()
    try:
        query = message.text.split(None, 1)[1]
    except:
        return await message.reply_text(f"<b>Usage:</b> <code>/{state} [query]</code>")
    chat_id = message.chat.id
    if chat_id in LIVE_CHATS:
        return await message.reply_text("» ꜱɪʟᴀʜᴋᴀɴ ᴋɪʀɪᴍ <code>/end</code> ᴜɴᴛᴜᴋ ᴍᴇɴɢᴀᴋʜɪʀɪ ꜱᴛʀᴇᴀᴍɪɴɢ ʟᴀɴɢꜱᴜɴɢ ʏᴀɴɢ ꜱᴇᴅᴀɴɢ ʙᴇʀʟᴀɴɢꜱᴜɴɢ ᴅᴀɴ ᴍᴜʟᴀɪ ᴍᴇᴍᴜᴛᴀʀ ʟᴀɢᴜ ʟᴀɢɪ.")
    
    m = await message.reply_text("**» ꜱᴇᴅᴀɴɢ ᴍᴇᴍᴘʀᴏꜱᴇꜱ ʟᴀɢᴜ...**")
    if state == "play":
        damn = AudioPiped
        ded = yt_audio
        doom = "ᴀᴜᴅɪᴏ"
    elif state == "vplay":
        damn = AudioVideoPiped
        ded = yt_video
        doom = "ᴠɪᴅᴇᴏ"
    if "low" in query:
        Q = "low"
    elif "mid" in query:
        Q = "mid"
    elif "high" in query:
        Q = "high"
    else:
        Q = "0"
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        link = f"https://youtube.com{results[0]['url_suffix']}"
        thumb = results[0]["thumbnails"][0]
        duration = results[0]["duration"]
        yt = YouTube(link)
        cap = f"» <b>ᴛɪᴛʟᴇ :</b> [{yt.title}]({link})\n🧐 <b>sᴛʀᴇᴀᴍ ᴛʏᴩᴇ :</b> `{doom}` \n🕕 <b>ᴅᴜʀᴀᴛɪᴏɴ:</b> {duration}"
        try:
            ydl_opts = {"format": "bestvideo[height<=720]+bestaudio/best[height<=720]"}
            ydl = youtube_dl.YoutubeDL(ydl_opts)
            info_dict = ydl.extract_info(link, download=False)
            p = json.dumps(info_dict)
            a = json.loads(p)
            playlink = a['formats'][1]['manifest_url']
        except:
            ice, playlink = await ded(link)
            if ice == "0":
                return await m.edit("❗️YTDL ERROR !!!")               
    except Exception as e:
        return await m.edit(str(e))
    
    try:
        if chat_id in QUEUE:
            position = add_to_queue(chat_id, yt.title, duration, link, playlink, doom, Q, thumb)
            caps = f"» [{yt.title}]({link}) <b>ǫᴜᴇᴜᴇᴅ ᴀᴛ {position}</b> ʙᴀʙʏ \n\n🕕 <b>ᴅᴜʀᴀᴛɪᴏɴ:</b> {duration}"
            await message.reply_photo(thumb, caption=caps)
            await m.delete()
        else:            
            await app.join_group_call(
                chat_id,
                damn(playlink),
                stream_type=StreamType().pulse_stream
            )
            add_to_queue(chat_id, yt.title, duration, link, playlink, doom, Q, thumb)
            await message.reply_photo(thumb, caption=cap, reply_markup=BUTTONS)
            await m.delete()
    except Exception as e:
        return await m.edit(str(e))
    
    
@bot.on_message(filters.command(["stream", "vstream"]) & filters.group)
@is_admin
async def stream_func(_, message):
    await message.delete()
    state = message.command[0].lower()
    try:
        link = message.text.split(None, 1)[1]
    except:
        return await message.reply_text(f"<b>Usage:</b> <code>/{state} [link]</code>")
    chat_id = message.chat.id
    
    if state == "stream":
        damn = AudioPiped
        emj = "🎵"
    elif state == "vstream":
        damn = AudioVideoPiped
        emj = "🎬"
    m = await message.reply_text("» ꜱᴇᴅᴀɴɢ ᴍᴇᴍᴘʀᴏꜱᴇꜱ ʟᴀɢᴜ...")
    try:
        if chat_id in QUEUE:
            return await m.edit("❗️ꜱɪʟᴀʜᴋᴀɴ ᴋɪʀɪᴍ <code>/end</code> ᴜɴᴛᴜᴋ ᴍᴇɴɢᴀᴋʜɪʀɪ ᴏʙʀᴏʟᴀɴ ꜱᴜᴀʀᴀ ꜱᴇʙᴇʟᴜᴍ ꜱᴛʀᴇᴀᴍɪɴɢ ʟᴀɴɢꜱᴜɴɢ.")
        elif chat_id in LIVE_CHATS:
            await app.change_stream(
                chat_id,
                damn(link)
            )
            await m.edit(f"{emj} Started streaming: [Link]({link})", disable_web_page_preview=True)
        else:    
            await app.join_group_call(
                chat_id,
                damn(link),
                stream_type=StreamType().pulse_stream)
            await m.edit(f"{emj} Started streaming: [Link]({link})", disable_web_page_preview=True)
            LIVE_CHATS.append(chat_id)
    except Exception as e:
        return await m.edit(str(e))


@bot.on_message(filters.command("skip") & filters.group)
@is_admin
async def skip(_, message):
    await message.delete()
    chat_id = message.chat.id
    if len(message.command) < 2:
        op = await skip_current_song(chat_id)
        if op == 0:
            await message.reply_text("» ᴀɴᴛʀɪᴀɴ ᴋᴏꜱᴏɴɢ..")
        elif op == 1:
            await message.reply_text("» ᴀɴᴛʀɪᴀɴ ᴋᴏꜱᴏɴɢ, ꜱᴛʀᴇᴀᴍɪɴɢ ᴛᴇʀᴛᴜᴛᴜᴘ.")
    else:
        skip = message.text.split(None, 1)[1]
        out = "🗑 <b>ᴍᴇɴɢʜᴀᴘᴜꜱ ʟᴀɢᴜ ʙᴇʀɪᴋᴜᴛ ᴅᴀʀɪ ᴀɴᴛʀɪᴀɴ:</b> \n"
        if chat_id in QUEUE:
            items = [int(x) for x in skip.split(" ") if x.isdigit()]
            items.sort(reverse=True)
            for x in items:
                if x == 0:
                    pass
                else:
                    hm = await skip_item(chat_id, x)
                    if hm == 0:
                        pass
                    else:
                        out = out + "\n" + f"<b>» {x}</b> - {hm}"
            await message.reply_text(out)
            
            
@bot.on_message(filters.command(["playlist", "queue"]) & filters.group)
@is_admin
async def playlist(_, message):
    chat_id = message.chat.id
    if chat_id in QUEUE:
        chat_queue = get_queue(chat_id)
        if len(chat_queue) == 1:
            await message.delete()
            await message.reply_text(
                f"🍒 <b>ᴄᴜʀʀᴇɴᴛʟʏ ᴩʟᴀʏɪɴɢ :</b> [{chat_queue[0][0]}]({chat_queue[0][2]}) | `{chat_queue[0][4]}`",
                disable_web_page_preview=True,
            )
        else:
            out = f"<b>📃 ǫᴜᴇᴜᴇ :</b> \n\n🎧 <b>ᴩʟᴀʏɪɴɢ :</b> [{chat_queue[0][0]}]({chat_queue[0][2]}) | `{chat_queue[0][4]}` \n"
            l = len(chat_queue)
            for x in range(1, l):
                title = chat_queue[x][0]
                link = chat_queue[x][2]
                type = chat_queue[x][4]
                out = out + "\n" + f"<b>» {x}</b> - [{title}]({link}) | `{type}` \n"
            await message.reply_text(out, disable_web_page_preview=True)
    else:
        await message.reply_text("» ɴᴏᴛʜɪɴɢ ɪs ᴩʟᴀʏɪɴɢ.")
    

@bot.on_message(filters.command(["end", "stop"]) & filters.group)
@is_admin
async def end(_, message):
    await message.delete()
    chat_id = message.chat.id
    if chat_id in LIVE_CHATS:
        await app.leave_group_call(chat_id)
        LIVE_CHATS.remove(chat_id)
        return await message.reply_text("» ʟᴀɢᴜ ʙᴇʀʜᴀꜱɪʟ ᴅɪᴀᴋʜɪʀɪ.")
        
    if chat_id in QUEUE:
        await app.leave_group_call(chat_id)
        clear_queue(chat_id)
        await message.reply_text("» ʟᴀɢᴜ ʙᴇʀʜᴀꜱɪʟ ᴅɪᴀᴋʜɪʀɪ.")
    else:
        await message.reply_text("» ᴛɪᴅᴀᴋ ᴀᴅᴀ ʏᴀɴɢ ᴅɪᴍᴀɪɴᴋᴀɴ.")
        

@bot.on_message(filters.command("pause") & filters.group)
@is_admin
async def pause(_, message):
    await message.delete()
    chat_id = message.chat.id
    if chat_id in QUEUE:
        try:
            await app.pause_stream(chat_id)
            await message.reply_text("» ʟᴀɢᴜ ʙᴇʀʜᴀꜱɪʟ ᴅɪᴊᴇᴅᴀ.")
        except:
            await message.reply_text("» ᴛɪᴅᴀᴋ ᴀᴅᴀ ʏᴀɴɢ ᴅɪᴍᴀɪɴᴋᴀɴ.")
    else:
        await message.reply_text("» ᴛɪᴅᴀᴋ ᴀᴅᴀ ʏᴀɴɢ ᴅɪᴍᴀɪɴᴋᴀɴ.")
        
        
@bot.on_message(filters.command("resume") & filters.group)
@is_admin
async def resume(_, message):
    await message.delete()
    chat_id = message.chat.id
    if chat_id in QUEUE:
        try:
            await app.resume_stream(chat_id)
            await message.reply_text("» ʟᴀɢᴜ ʙᴇʀʜᴀꜱɪʟ ᴅɪʟᴀɴᴊᴜᴛᴋᴀɴ.")
        except:
            await message.reply_text("» ᴛɪᴅᴀᴋ ᴀᴅᴀ ʏᴀɴɢ ᴅɪᴍᴀɪɴᴋᴀɴ.")
    else:
        await message.reply_text("» ᴛɪᴅᴀᴋ ᴀᴅᴀ ʏᴀɴɢ ᴅɪᴍᴀɪɴᴋᴀɴ.")


@bot.on_message(filters.command("restart"))
async def restart(_, message):
    user_id = message.from_user.id
    if user_id != OWNER_ID:
        return
    await message.reply_text("» <i>ꜱᴇᴅᴀɴɢ ᴍᴇʀᴇꜱᴛᴀʀᴛ...</i>")
    os.system(f"kill -9 {os.getpid()} && python3 app.py")
            

app.start()
bot.run()
idle()
