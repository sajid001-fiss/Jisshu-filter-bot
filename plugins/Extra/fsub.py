from pyrogram import Client, filters, enums
from pyrogram.types import ChatJoinRequest
from database.users_chats_db import db
from info import ADMINS, AUTH_CHANNEL
from utils import is_check_admin
import logging  
logger = logging.getLogger(__name__)


@Client.on_message(filters.command("fsub"))
async def force_subscribe(client, message):
    m = await message.reply_text("Wait im checking...")
    if not message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await m.edit("This command is only for groups!")
    if not await is_check_admin(client, message.chat.id, message.from_user.id):
        return await m.edit("Only group admins can use this command!")
    try: 
        toFsub = message.command[1]
    except IndexError:
        return await m.edit("Usage: /fsub CHAT_ID")
    if not toFsub.startswith("-100"):
        toFsub = '-100'+toFsub
    if not toFsub[1:].isdigit() or len(toFsub) != 14:
        return await m.edit("CHAT_ID isn't valid!")
    try:
        toFsub = int(toFsub) if not toFsub.startswith("@") else toFsub
    except:
        return await m.edit("Only Send Chat ID or Username with @ !")
    if toFsub == message.chat.id:
        return await m.edit("It seems like you're attempting to enable force subscription for this chat ID. Please use a different chat ID !")
    if not await is_check_admin(client, toFsub, client.me.id):
        return await m.edit("I need to be an admin in the given chat to perform this action!\nMake me admin in your Target chat and try again.")
    id = await client.get_chat(toFsub)
    try:
        await db.setFsub(grpID=message.chat.id, fsubID=id.id, name=id.title)
        return await m.edit(f"Successfully added force subscribe to {toFsub} in {message.chat.title}")
    except Exception as e:
        logger.exception(e)
        return await m.edit(f"Something went wrong ! Try again later or report in Support Group @SandVillage1")

@Client.on_message(filters.command("del_fsub"))
async def del_force_subscribe(client, message):
    m = await message.reply_text("Wait im checking...")
    if not message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await m.edit("This command is only for groups!")
    if not await is_check_admin(client, message.chat.id, message.from_user.id):
        return await m.edit("Only group admins can use this command!")
    ifDeleted =await db.delFsub(message.chat.id)
    if ifDeleted:
        return await m.edit(f"Successfully removed force subscribe for - {message.chat.title}\nTo add again use <code>/fsub YOUR_FSUB_CHAT_ID</code>")
    else:
        return await m.edit(f"Force subscribe not found in {message.chat.title}")

@Client.on_message(filters.command("show_fsub"))
async def show_fsub(client, message, m=None):
    if m is None:
        m = await message.reply_text("Wait im checking...")
    if not message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await m.edit("This command is only for groups!")
    # check if commad is given by admin or not
    if not await is_check_admin(client, message.chat.id, message.from_user.id):
        return await m.edit("Only group admins can use this command!")
    fsub = await db.getFsub(message.chat.id)
    if fsub:
        #now gen a invite link
        try:
            invite_link = await client.export_chat_invite_link(fsub.id)
        except:
            async for member in client.get_chat_members(chat_id=message.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
                if not member.user.is_bot:
                    try:
                        await client.send_message(member.user.id, f"#Attention !\nSeems i've been removed from {fsub.name}, removing Fsub!!!", disable_web_page_preview=True)
                    except:
                        pass

            await db.delFsub(message.chat.id)
            await show_fsub(client, message, m=m)
        await m.edit(f"Force subscribe is set to {fsub}\n<a href={invite_link}>Channel Link Link</a>" ,disable_web_page_preview=True)
    else:
        await m.edit(f"Force subscribe is not set in {message.chat.title}")
