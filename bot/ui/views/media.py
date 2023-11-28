from discord import ui, ButtonStyle, Interaction, Embed, Colour
from ...music import GM
from ...music.voice import VoiceManager
from ...music.YM.Track import Track
from ...music.YM.Playlist import Playlist


def check_voice(func):
    async def wrapper(*args, **kwargs):
        if args[1].user.voice:
            return await func(*args)
        else:
            await args[1].response.send_message(
                "Для выполнения этого действия вы должны находится в голосовом канале!",
                ephemeral=True
            )
    return wrapper

def check_role(role_id):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            interaction = args[1]
            user = interaction.user
            guild = interaction.guild
            role = None
            role_name = None
            role_colour = Colour.default()

            for r in guild.roles:
                if r.id == role_id:
                    role = r
                    role_name = r.mention  # Получаем упоминание роли
                    role_colour = r.colour
                    break

            if role and role not in user.roles:
                embed = Embed(
                    title="Ошибка",
                    description=f"У вас нет роли {role_name} для выполнения этого действия!",
                    color=role_colour
                )
                await interaction.response.send_message(
                    embed=embed,
                    ephemeral=True
                )
            else:
                return await func(*args)

        return wrapper

    return decorator

class MediaPlayer(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.repeat_enabled = False

    @ui.button(label="Пауза", style=ButtonStyle.green, custom_id="play_or_pause", row=1, emoji="<:Pause:1172248080129732749>")
    @check_voice
    async def play_or_pause(self, interaction: Interaction, button: ui.Button):
        VM: VoiceManager = await GM.get_guild(interaction.user.voice.channel, interaction.channel)
        if not interaction.user.voice.channel or interaction.user.voice.channel.id != VM.voiceChannel.id:
            await interaction.response.send_message(
                "Для этого действия вам нужно находится в текущем голосом канале!",
                ephemeral=True
            )
        else:
            if not VM.voiceClient.is_paused():
                VM.voiceClient.pause()
                button.label = "Продолжить"
                button.style = ButtonStyle.red
                button.emoji = "<:Play:1172248082197528658>"
            else:
                VM.voiceClient.resume()
                button.label = "Пауза"
                button.style = ButtonStyle.green
                button.emoji = "<:Pause:1172248080129732749>"
            await interaction.response.edit_message(view=self)


    @ui.button(label="Пропустить", style=ButtonStyle.blurple, custom_id="skip_track", row=3, emoji="<:Skip:1172248088451235870> ")
    @check_voice
    async def skip_track(self, interaction: Interaction, button: ui.Button):
        VM: VoiceManager = await GM.get_guild(interaction.user.voice.channel, interaction.channel)
        if not interaction.user.voice.channel or interaction.user.voice.channel.id != VM.voiceChannel.id:
            await interaction.response.send_message(
                "Для этого действия вам нужно находится в текущем голосом канале!",
                ephemeral=True
            )
        else:
            if self.repeat_enabled:
                self.repeat_enabled = False
            VM.voiceClient.stop()

            await interaction.response.edit_message(view=self)


    @ui.button(label="Пропустить плейлист", style=ButtonStyle.blurple, custom_id="skip_playlist", row=3, emoji="<:forward:1172248078674317394>")
    @check_voice
    async def skip_playlist(self, interaction: Interaction, button: ui.Button):
        VM: VoiceManager = await GM.get_guild(interaction.user.voice.channel, interaction.channel)
        if not interaction.user.voice.channel or interaction.user.voice.channel.id != VM.voiceChannel.id:
             await interaction.response.send_message(
                "Для этого действия вам нужно находится в текущем голосом канале!",
                ephemeral=True
            )
        else:
            if self.repeat_enabled:  # Проверяем, включено ли повторение
                self.repeat_enabled = False  # Отключаем повторение
            VM.counter = 0
            await VM.skip(playlist=True)
            VM.voiceClient.stop()
            await interaction.response.edit_message(view=self)


    @ui.button(label="Остановить", style=ButtonStyle.red, custom_id="stop", row=1, emoji="<:Stop:1172248091336904755>")
    @check_voice
    async def stop(self, interaction: Interaction, button:ui.Button):
        VM: VoiceManager = await GM.get_guild(interaction.user.voice.channel, interaction.channel)
        if not interaction.user.voice.channel or interaction.user.voice.channel.id != VM.voiceChannel.id:
             await interaction.response.send_message(
                "Для этого действия вам нужно находится в текущем голосом канале!",
                ephemeral=True
            )
        else:
            VM.queue.clear()
            VM.voiceClient.stop()


    @ui.button(label="Повтор трека", style=ButtonStyle.grey, custom_id="repeat_track", row=2, emoji="<:Replay:1172248084114325514>")
    @check_voice
    async def repeat_track(self, interaction: Interaction, button: ui.Button):
        VM: VoiceManager = await GM.get_guild(interaction.user.voice.channel, interaction.channel)
        if not interaction.user.voice.channel or interaction.user.voice.channel.id != VM.voiceChannel.id:
            await interaction.response.send_message(
                "Для этого действия вам нужно находиться в текущем голосовом канале!",
                ephemeral=True
            )
        else:
            if self.repeat_enabled:  # Проверяем, включено ли повторение
                self.repeat_enabled = False  # Отключаем повторение
                button.style = ButtonStyle.grey
                button.emoji = "<:Replay:1172248084114325514>"
            else:
                self.repeat_enabled = True  # Включаем повторение
                button.style = ButtonStyle.green
                button.emoji = "<:Replay:1172248084114325514>"
            await interaction.response.edit_message(view=self)

    @ui.button(label="Перемешать", style=ButtonStyle.grey, custom_id="shuffle_tracks", row=2,
               emoji="<:shuffle:1172612523808276571>")
    @check_voice
    async def shuffle_tracks(self, interaction: Interaction, button:ui.Button):
        VM: VoiceManager = await GM.get_guild(interaction.user.voice.channel, interaction.channel)
        if not interaction.user.voice.channel or interaction.user.voice.channel.id != VM.voiceChannel.id:
             await interaction.response.send_message(
                "Для этого действия вам нужно находится в текущем голосом канале!",
                ephemeral=True
            )
        else:
            await VM.shuffle_tracks()
            embed = Embed(
                title="Перемешать треки",
                colour=Colour.green()
            )

            embed.description = "Все треки в каждом плейлисте были перемешаны!"

            await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )
    @ui.button(label="Похожие треки", style=ButtonStyle.grey, custom_id="similars_tracks", row=2,
               emoji="<:similartrack:1178232889213726771>")
    @check_voice
    async def similars_tracks(self, interaction: Interaction, button:ui.Button):
        VM: VoiceManager = await GM.get_guild(interaction.user.voice.channel, interaction.channel)
        if not interaction.user.voice.channel or interaction.user.voice.channel.id != VM.voiceChannel.id:
             await interaction.response.send_message(
                "Для этого действия вам нужно находится в текущем голосом канале!",
                ephemeral=True
            )
        else:
            first_track = (await VM.first_track()).track_object
            track_exists = await Playlist(user_id=f"{first_track.id}", playlist_id=f"{first_track.albums[0]['id']}").find_similar_tracks()

            if track_exists is not None:
                VM.queue.append(track_exists)

                embed = Embed(
                    title="Похожие треки",
                    colour=Colour.green()
                )

                embed.description = "Похожие треки были добавлены в очередь!"

            else:
                embed = Embed(
                    title="Похожие треки",
                    colour=Colour.red()
                )

                embed.description = "Не найдено похожих треков!"

            await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )

    @ui.button(label="Помощь", style=ButtonStyle.grey, custom_id="help", row=4, emoji="<:help:1172248485429510154>")
    async def help(self, interaction: Interaction, button: ui.Button):
        embed = Embed(
            title="Подсказка",
            colour=Colour.green()
        )

        embed.description = "<:yandexm:1172239147969302559> Данный бот проигрывает Треки/Альбомы/Плейлисты/Подкасты/Книги" \
                            " из Яндекс.Музыки!\n\n" \
                            "Вы можете добавить трек отправив ссылку/название трека или отрывок из песни с помощью команды: </play:1171295728300212344>\n\n" \

        embed.add_field(
            name="Подсказки по кнопкам",
            value="<:Pause:1172248080129732749> \ <:Play:1172248082197528658> - Паузка или продолжение проигрывания.\n" \
                  "<:Skip:1172248088451235870> - Пропустить один Трек\Подкаст\Книгу в очереди.\n" \
                  "<:forward:1172248078674317394> - Пропустить целый плейлист в очереди.\n" \
                  "<:Replay:1172248084114325514> - Повторять Трек\Подкаст\Книгу в очереди.\n" \
                  "<:shuffle:1172612523808276571> - Перемешать все треки во всех плейлистах.\n" \
                  "<:Stop:1172248091336904755> - Полностью остановить проигрывание и очистить очередь!\n" \
                  "<:Tracklist:1172248092913967285> - Очередь треков."
        )
        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )


    @ui.button(label="Треки в очереди", style=ButtonStyle.grey, custom_id="queue", row=4, emoji="<:Tracklist:1172248092913967285>")
    @check_voice
    async def queue(self, interaction: Interaction, button: ui.Button):
        embed = Embed(
            title="Очередь треков"
        )

        VM: VoiceManager = await GM.get_guild(interaction.user.voice.channel, interaction.channel)

        for mediaItem in VM.queue[:8]:
            if isinstance(mediaItem, Track):
                mediaItemQueue = []
                if mediaItem.artists:
                    artists = ", ".join([artist.name for artist in mediaItem.artists])
                    mediaItemQueue.append(f"**{artists}** - _{mediaItem.title}_")
                else:
                    mediaItemQueue.append(f"_{mediaItem.title}_")

                embed.add_field(
                    name="Трек",
                    value='\n'.join(mediaItemQueue)
                )
            else:
                mediaItemQueue = []
                for index, item in enumerate(mediaItem.tracks[:8]):
                    if item.artists:
                        artists = ", ".join([artist.name for artist in item.artists])
                        mediaItemQueue.append(f"{index+1}. **{artists}** - _{item.title}_")
                    else:
                        mediaItemQueue.append(f"{index+1}. _{item.title}_")

                if len(mediaItem.tracks) < 8:
                    embed.add_field(
                        name=mediaItem.title,
                        value=('\n'.join(mediaItemQueue))
                    )
                else:
                    embed.add_field(
                        name=mediaItem.title,
                        value=('\n'.join(mediaItemQueue)) + f"\n\n И ещё {len(mediaItem.tracks) - 8} треков!"
                    )
        await interaction.response.send_message(embed=embed, ephemeral=True)





