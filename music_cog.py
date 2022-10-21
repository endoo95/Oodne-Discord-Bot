import nextcord
import wavelink
import datetime

from nextcord.ext import commands
from wavelink.ext import spotify
from utility import SPOTIFY_SECRET

class music_cog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        bot.loop.create_task(self.node_connect())

    def check_channel(self, ctx: commands.Context):
        if not ctx.voice_client:
            return ctx.send("Are you sure that I'm playing right now? Cause oviously I'm not.")
        elif not getattr(ctx.author.voice, "channel", None):
            return ctx.send("Hey! You're not in the voice channel!")
        elif not ctx.author.voice.channel == ctx.me.voice.channel:
            ctx.send("We're not in the same channel!")
            return ctx.send(f"Write 'm!join!'")
        else:
            vc: wavelink.Player = ctx.voice_client
            return vc

    def now_playing(self, ctx: commands.Context, vc):
        em = nextcord.Embed(title="Now playing")
        em.add_field(name="Song:", value=f"{vc.track.title}", inline=False)
        em.add_field(name="Duration:", value=f"{str(datetime.timedelta(seconds=vc.track.length))}")
        return ctx.send(embed=em)

    async def node_connect(self):
        await self.bot.wait_until_ready()
        SPOTIFY_CLIENT = "ad798d4ccd924ea18b71d25d4d7683ea"
        await wavelink.NodePool.create_node(bot=self.bot, host='krn.2d.gay', port=443, password='AWP)JQ$Gv9}dm.u', https=True, spotify_client=spotify.SpotifyClient(client_id=SPOTIFY_CLIENT, client_secret=SPOTIFY_SECRET))

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        print(f"Node {node.identifier} is ready!")

    async def on_wavelink_track_end(player: wavelink.Player, track: wavelink.Track, reason):
        ctx = player.ctx
        vc: player = ctx.voice_client

        if vc.loop:
                return await vc.play(track)

        next_song = vc.queue.get()
        await vc.play(next_song)
        music_cog.now_playing(ctx, vc)

    @commands.command(name="play", aliases=["Play", "p"], help="Play the selected song from youtube")
    async def play(self, ctx: commands.Context, *, search: wavelink.YouTubeTrack):
        if not ctx.voice_client:
            vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        elif not getattr(ctx.author.voice, "channel", None):
            return await ctx.send("Hey! You're not in the voice channel!")
        elif not ctx.author.voice.channel == ctx.me.voice.channel:
            await ctx.send("We're not in the same channel")
            return await ctx.send(f"Write 'm!join'!")
        else:
            vc: wavelink.Player = ctx.voice_client

        await vc.set_volume(5)

        if vc.track == None:
            await vc.play(search)
            if vc.is_playing():
                await music_cog.now_playing(self, ctx, vc)
        else:
            await vc.queue.put_wait(search)
            await ctx.send(f"Added '{search.title}' to the queue!")

        vc.ctx = ctx
        setattr(vc, "loop", False)

    @commands.command(name="splay", aliases=["sPlay", "sp"], help="Play the selected song from spotify")
    async def splay(self, ctx: commands.Context, *, search: str):
        if not ctx.voice_client:
            vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        elif not getattr(ctx.author.voice, "channel", None):
            return await ctx.send("Hey! You're not in the voice channel!")
        elif not ctx.author.voice.channel == ctx.me.voice.channel:
            await ctx.send("We're not in the same channel")
            return await ctx.send(f"Write 'm!join'!")
        else:
            vc: wavelink.Player = ctx.voice_client

        await vc.set_volume(5)

        if vc.track == None:
            try:
                track = await spotify.SpotifyTrack.search(query=search, return_first=True)
                await vc.play(track)
                if vc.is_playing():
                    await music_cog.now_playing(self, ctx, vc)
            except Exception as e:
                await ctx.send("Hey! It's not URL form spotify...")
                return print(e)
        else:
            await vc.queue.put_wait(track)
            await ctx.send(f"Added '{track.title}' to the queue!")

        vc.ctx = ctx
        setattr(vc, "loop", False)

    @commands.command(name="stop", aliases=["Stop", "s"], help="Stops playing, and resets song queue")
    async def stop(self, ctx:commands.Context):
        vc = self.check_channel(ctx)

        await vc.stop()
        await ctx.send("I shall remain silent.")
        
        await vc.queue.clear()
 
    @commands.command(name="pause", aliases=["Pause", "ps"], help="Pauses song that is currently being played")
    async def pause(self, ctx:commands.Context):
        vc = self.check_channel(ctx)

        if vc.track == None:
            return await ctx.send("I'm not playing anything, lol")
        else:
            await vc.pause()
            await ctx.send("Ok, I'll pause")

    @commands.command(name="resume", aliases=["Resume", "r"], help="Resumes playing the current song")
    async def resume(self, ctx:commands.Context):
        vc = self.check_channel(ctx)

        if vc.track == None:
            return await ctx.send("Hush, I'm asleep.")
        else:
            await vc.resume()
            await ctx.send("Ahh ye! Hey DJ! Spin that shit!")

    @commands.command(name="next", aliases=["Next", "n"], help="plays next song in queue")
    async def next(self, ctx:commands.Context):
        vc = self.check_channel(ctx)

        if vc.queue.count == 0:
            return await ctx.send("There is no songs in queue")
        else: 
            next_song = vc.queue.get()
            await vc.play(next_song)
            await music_cog.now_playing(self, ctx, vc)

    @commands.command(name="join", aliases=["Join", "j"], help="Make me join your channel")
    async def join(self, ctx:commands.Context):
        if not ctx.voice_client:
            vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        elif not getattr(ctx.author.voice, "channel", None):
            return ctx.send("Hey! You're not in the voice channel!")
        else:
            vc: wavelink.Player = ctx.voice_client
            channel = ctx.author.voice.channel
            await channel.connect(cls=wavelink.Player)

        await vc.set_volume(5)

    @commands.command(name="kick", aliases=["Kick", "k", "Leave", "leave"], help="Kick the bot from the voice channel")
    async def leave(self, ctx:commands.Context):
        vc = self.check_channel(ctx)

        await vc.disconnect()
        await ctx.send("Till next time!")

    @commands.command(name="nowplaying", aliases=["NowPlaying", "now", "Now", "np"], help="Shows currently played track")
    async def nowplaying(self, ctx: commands.Context):
        vc = self.check_channel(ctx)

        #Naprawić błąd. Po zmianie piosenki nie czyta "is_playing"
        if not vc.is_playing():
            return await ctx.send("Nothing here")

        return await music_cog.now_playing(self, ctx, vc)

    @commands.command(name="loop", aliases=["Loop", "l"], help="Kick the bot from the voice channel")
    async def loop(self, ctx:commands.Context):
        vc = self.check_channel(ctx)

        try:
            vc.loop ^= True
        except Exception:
            setattr((vc, "loop", False))

        if vc.loop:
            return await ctx.send("Loop'n!")
        else:
            return await ctx.send("Disabling loop!")

    @commands.command(name="queue", aliases=["Queue", "q"], help="Displays next four songs from the queue")
    async def queue(self, ctx:commands.Context):
        vc = self.check_channel(ctx)

        if vc.queue.is_empty:
            return await ctx.send("Queue is empty")

        em = nextcord.Embed(title="Queue", type="rich")
        queue = vc.queue.copy()
        song_count = 0
        for song in queue:
            song_count += 1
            em.add_field(name=f"Song {song_count}", value=f"{song.title}", inline=False)

        return await ctx.send(embed=em)

    @commands.command(name="volume", aliases=["Volume", "v"], help="Changes volume of the track in '%' from 0-100")
    async def volume(self, ctx:commands.Context, volume: int):
        vc = self.check_channel(ctx)

        if volume > 100 or volume < 0:
            return await ctx.send("Put number between 0-100!")
        else:
            await ctx.send(f"Volume is now {volume}%!")
            return await vc.set_volume(volume)