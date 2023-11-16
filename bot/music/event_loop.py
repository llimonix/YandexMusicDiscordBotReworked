import asyncio
from time import time
from io import BytesIO
from ..core import Bot
from .voice import VoiceManager
from discord import TextChannel, Embed, Colour, FFmpegOpusAudio
from ..music.YM.Track import Track
from discord.errors import ClientException
from pydub import AudioSegment
from ..utils.log import LOGGER
from discord.ui.button import Button, ButtonStyle
from ..ui.views.colorRGB import DominantColor

log = LOGGER("event_loop")


async def event_loop(voiceManager: VoiceManager, MediaPlayer):
    
    lastActivity = None
    voiceManager.counter = 0 # Счётчик интераций цикла

    if not voiceManager.voiceClient or not voiceManager.voiceClient.is_connected():
        try:
            await voiceManager.connect()
        except ClientException:
            Bot.loop.create_task(error_message(voiceManager.textChannel, disconnectError=True))

    if voiceManager.voiceClient:
        while True:
            try:
                voiceManager.counter += 1

                if Bot.user not in voiceManager.voiceChannel.members:
                    voiceManager.voiceClient.stop()
                    await voiceManager.disconnect()
                    await voiceManager.delete_message()
                    Bot.loop.create_task(disconnected_message(voiceManager.textChannel))
                    break
                elif Bot.user in voiceManager.voiceChannel.members and len(voiceManager.voiceChannel.members) == 1:
                    if not lastActivity:
                        lastActivity = time()
                    else:
                        if time() - lastActivity >= 180:
                            await voiceManager.delete_message()
                            voiceManager.voiceClient.stop()
                            await voiceManager.disconnect()
                            Bot.loop.create_task(disconnected_message(voiceManager.textChannel, activity=True))
                            break
                else:
                    lastActivity = None

                if not voiceManager.voiceClient.is_playing() and not voiceManager.voiceClient.is_paused():
                    if not voiceManager.queue:
                        await voiceManager.delete_message()
                        await voiceManager.disconnect()
                        Bot.loop.create_task(disconnected_message(voiceManager.textChannel, notTracks=True))
                        break
                    else:
                        if voiceManager.counter != 1:
                            if MediaPlayer.repeat_enabled:  # Проверяем, включено ли повторение
                                current_track = voiceManager.queue.pop(0)
                                voiceManager.queue.insert(0, current_track)
                            else:
                                await voiceManager.skip()

                        try:
                            track = await voiceManager.first_track()
                        except IndexError:
                            continue

                        if not track.available:
                            continue
                        else:
                            trackSource = await track.download()

                        audio_data = AudioSegment.from_file(BytesIO(trackSource), format='mp3')
                        normalized_audio = audio_data.normalize()

                        voiceManager.voiceClient.play(FFmpegOpusAudio(normalized_audio.export(format='wav'), pipe=True))
                        await now_playing(voiceManager, track, MediaPlayer)
            except Exception as err:
                log.error(err, exc_info=True)
                await error_message(voiceManager.textChannel, unexpected=True)

            await asyncio.sleep(.3)

        await voiceManager.delete_message()
    

async def now_playing(voiceManager: VoiceManager, track: Track, MediaPlayer):
    # Если у нас уже есть сохраненное сообщение, используем его
    if voiceManager.message:
        embed = voiceManager.message.embeds[0]  # Получаем встроенное сообщение
        embed.title = "Сейчас играет"
        embed.description = f"[{track.title} ({track.duration})]({track.track_link})"
        artists = [artist.name for artist in track.artists]
        if artists:
            try:
                artist_cover_uri = ("https://" + track.artists[0].cover.uri).replace("%%", "300x300")
            except:
                artist_cover_uri = "https://yastatic.net/s3/doc-binary/freeze/vwogjhEVmMn1pRZIEL6YBYfOSQs.png"
            artist_uri = f"https://music.yandex.ru/artist/{track.artists[0].id}"

            embed.set_author(name=', '.join(artists), icon_url=artist_cover_uri, url=artist_uri)
        color_embed = await DominantColor.get_dominant_color(track.preview)
        embed.color = (color_embed[0] << 16) + (color_embed[1] << 8) + color_embed[2]
        embed.set_thumbnail(url=track.preview)

        for child in MediaPlayer.children:
            if isinstance(child, Button) and child.custom_id == "repeat_track":
                if MediaPlayer.repeat_enabled == False:
                    child.style = ButtonStyle.grey
            if isinstance(child, Button) and child.custom_id == "play_or_pause":
                child.style = ButtonStyle.green
                child.label = "Пауза"
        try:
            await voiceManager.message.edit(embed=embed, view=MediaPlayer)
        except:
            try:
                await voiceManager.delete_message()
                voiceManager.message = await voiceManager.textChannel.send(embed=embed, view=MediaPlayer)
            except:
                voiceManager.message = await voiceManager.textChannel.send(embed=embed, view=MediaPlayer)
    else:
        embed = Embed(
            title="Сейчас играет",
            description=f"[{track.title} ({track.duration})]({track.track_link})"
        )
        artists = [artist.name for artist in track.artists]
        if artists:
            try:
                artist_cover_uri = ("https://" + track.artists[0].cover.uri).replace("%%", "300x300")
            except:
                artist_cover_uri = "https://yastatic.net/s3/doc-binary/freeze/vwogjhEVmMn1pRZIEL6YBYfOSQs.png"
            artist_uri = f"https://music.yandex.ru/artist/{track.artists[0].id}"

            embed.set_author(name=', '.join(artists), icon_url=artist_cover_uri, url=artist_uri)
        color_embed = await DominantColor.get_dominant_color(track.preview)
        embed.color = (color_embed[0] << 16) + (color_embed[1] << 8) + color_embed[2]
        embed.set_thumbnail(url=track.preview)

        for child in MediaPlayer.children:
            if isinstance(child, Button) and child.custom_id == "repeat_track":
                if MediaPlayer.repeat_enabled == False:
                    child.style = ButtonStyle.grey
            if isinstance(child, Button) and child.custom_id == "play_or_pause":
                child.style = ButtonStyle.green
                child.label = "Пауза"

        voiceManager.message = await voiceManager.textChannel.send(embed=embed, view=MediaPlayer)



async def disconnected_message(channel: TextChannel, activity=False, notTracks=False):
    """Сообщение о отключении от голосового чата!"""

    embed = Embed(
        title="Бот отключен от голосового чата!"    
    )

    if activity:
        embed.description = "Бот отключен из-за отсутствия активности!"
        embed.color=Colour.red()
    elif notTracks:
        embed.description = "Очередь треков окончена!"
        embed.color=Colour.brand_red()
    else:
        embed.color=Colour.red()

    message = await channel.send(embed=embed)
    await asyncio.sleep(10 if activity else 3)
    await message.delete()


async def error_message(channel: TextChannel, disconnectError = False, unexpected=False):
    embed = Embed(
        title="Ошибка!",
        colour=Colour.red()
    )

    if disconnectError:
        embed.description = "Похоже вы отключили бота не самым лучшим способом. Подождите немного..."
    elif unexpected:
        embed.description = "Непредвиденная ошибка!"

    message = await channel.send(embed=embed)
    await asyncio.sleep(10)
    await message.delete()
