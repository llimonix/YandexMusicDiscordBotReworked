from discord import ui, ButtonStyle, Interaction, Embed, Colour
from ...music import GM
from ...music.voice import VoiceManager
from ...music.YM.Track import Track


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

    @ui.button(label="Пауза", style=ButtonStyle.green, custom_id="play_or_pause", row=1)
    @check_voice
    @check_role(770230393575702558)
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
            else:
                VM.voiceClient.resume()
                button.label = "Пауза"
                button.style = ButtonStyle.green
            await interaction.response.edit_message(view=self)


    @ui.button(label="Пропустить", style=ButtonStyle.blurple, custom_id="skip_track", row=3)
    @check_voice
    @check_role(770230393575702558)
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


    @ui.button(label="Пропустить плейлист", style=ButtonStyle.blurple, custom_id="skip_playlist", row=3)
    @check_voice
    @check_role(770230393575702558)
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


    @ui.button(label="Остановить", style=ButtonStyle.red, custom_id="stop", row=1)
    @check_voice
    @check_role(770230393575702558)
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


    @ui.button(label="Повтор трека", style=ButtonStyle.grey, custom_id="repeat_track", row=2)
    @check_voice
    @check_role(770230393575702558)
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
            else:
                self.repeat_enabled = True  # Включаем повторение
                button.style = ButtonStyle.green
            await interaction.response.edit_message(view=self)

    @ui.button(label="Перемешать", style=ButtonStyle.grey, custom_id="shuffle_tracks", row=2)
    @check_voice
    @check_role(770230393575702558)
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

    @ui.button(label="Помощь", style=ButtonStyle.grey, custom_id="help", row=4)
    async def help(self, interaction: Interaction, button: ui.Button):
        embed = Embed(
            title="Подсказка",
            colour=Colour.green()
        )

        embed.description = "Данный бот проигрывает Треки/Альбомы/Плейлисты/Подкасты/Книги" \
                            " из Яндекс.Музыки!\n\n" \
                            "Вы можете добавить трек отправив ссылку/название трека или отрывок из песни с помощью команды: </play:1171295728300212344>\n\n" \

        embed.add_field(
            name="Подсказки по кнопкам",
            value="Пауза \ Продолжить - Паузка или продолжение проигрывания.\n" \
                  "Пропустить - Пропустить один Трек\Подкаст\Книгу в очереди.\n" \
                  "Пропустить плейлист - Пропустить целый плейлист в очереди.\n" \
                  "Повтор трека - Повторять Трек\Подкаст\Книгу в очереди.\n" \
                  "Перемешать - Перемешать все треки во всех плейлистах.\n" \
                  "Остановить - Полностью остановить проигрывание и очистить очередь!\n" \
                  "Треки в очереди- Очередь треков."
        )
        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )


    @ui.button(label="Треки в очереди", style=ButtonStyle.grey, custom_id="queue", row=4)
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

                embed.add_field(
                    name = mediaItem.title,
                    value=('\n'.join(mediaItemQueue)) + f"\n\n И ещё {len(mediaItem.tracks) - 8} треков!"
                )

        await interaction.response.send_message(embed=embed, ephemeral=True)




