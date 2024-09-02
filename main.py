import discord
import os
from discord.ext import commands
from discord import app_commands
import pathlib
import sys
import psutil
from dotenv import load_dotenv
import os
load_dotenv()


token = os.getenv('TOKEN')
dev = [756728239673573376]

class MyBot(commands.Bot):
    async def setup_hook(self):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f'Loaded extension: {filename[:-3]}')

        bot.tree.add_command(DevGroup(bot))
        await self.tree.sync()

intents = discord.Intents.all()
bot = MyBot(intents=intents,command_prefix="$",case_insensitive=True)
tree = bot.tree

@bot.event
async def on_ready():
    print('-----')
    print(bot.user.name)
    print(bot.user.id)
    print('-----')
    print(f'Login {bot.user}')

class DevGroup(app_commands.Group):
    def __init__(self, *args, **kwargs):
        super().__init__(name="dev")
        self.default_permission = False

    def _get_available_cogs(self):
        folder_name = 'cogs'
        cur = pathlib.Path('.')

        available_cogs = []
        for p in cur.glob(f"{folder_name}/**/*.py"):
            if p.stem == "__init__":
                continue
            module_path = p.relative_to(cur).with_suffix('').as_posix().replace('/', '.')
            if module_path.startswith('cogs.'):
                available_cogs.append(module_path)
        print(available_cogs)
        return available_cogs

    async def cog_autocomplete(
            self,
            interaction: discord.Interaction,
            current: str
    ) -> list[app_commands.Choice[str]]:
        available_cogs = self._get_available_cogs()
        filtered_cogs = [cog for cog in available_cogs if current.lower() in cog.lower()]
        return [
            app_commands.Choice(name=cog, value=cog) for cog in filtered_cogs[:25]
        ]

    @app_commands.command(name="reload", description="コマンドをリロードします")
    @app_commands.autocomplete(cog=cog_autocomplete)
    async def reload_cog(self, interaction: discord.Interaction, cog: str):
        available_cogs = self._get_available_cogs()

        if cog not in available_cogs:
            await interaction.response.send_message(f"'{cog}' は利用可能なcogのリストに含まれていません。")
            return

        try:
            await bot.reload_extension(cog)
            await bot.tree.sync()
            await interaction.response.send_message(f"{cog}を再読み込みしました。")
        except commands.ExtensionNotLoaded:
            await interaction.response.send_message(f"'{cog}' は読み込まれていません。")
        except commands.ExtensionFailed as e:
            await interaction.response.send_message(
                f"'{cog}' の再読み込み中にエラーが発生しました。\n{type(e).__name__}: {e}")
    
    @app_commands.command(name="load", description="コマンドをロードします")
    @app_commands.autocomplete(cog=cog_autocomplete)
    async def load_cog(self, interaction: discord.Interaction, cog: str):
        available_cogs = self._get_available_cogs()

        if cog not in available_cogs:
            await interaction.response.send_message(f"'{cog}' は利用可能なcogのリストに含まれていません。")
            return

        try:
            await bot.load_extension(cog)
            await bot.tree.sync()
            await interaction.response.send_message(f"{cog}をロードしました。")
        except commands.ExtensionAlreadyLoaded:
            await interaction.response.send_message(f"'{cog}' は既に読み込まれています。")
        except commands.ExtensionFailed as e:
            await interaction.response.send_message(
                f"'{cog}' の読み込み中にエラーが発生しました。\n{type(e).__name__}: {e}")
        
    @app_commands.command(name="unload", description="コマンドをアンロードします")
    @app_commands.autocomplete(cog=cog_autocomplete)
    async def unload_cog(self, interaction: discord.Interaction, cog: str):
        available_cogs = self._get_available_cogs()

        if cog not in available_cogs:
            await interaction.response.send_message(f"'{cog}' は利用可能なcogのリストに含まれていません。")
            return

        try:
            await bot.unload_extension(cog)
            await bot.tree.sync()
            await interaction.response.send_message(f"{cog}をアンロードしました。")
        except commands.ExtensionNotLoaded:
            await interaction.response.send_message(f"'{cog}' は読み込まれていません。")
        except commands.ExtensionFailed as e:
            await interaction.response.send_message(
                f"'{cog}' のアンロード中にエラーが発生しました。\n{type(e).__name__}: {e}")
    
    @app_commands.command(name="sync", description="コマンドを同期します")
    async def sync_cog(self, interaction: discord.Interaction):
        await bot.tree.sync()
        await interaction.response.send_message("コマンドを同期しました。")

    @app_commands.command(name="restart", description="Botを再起動する")
    async def bot_restart(self, interaction: discord.Interaction):
        if interaction.user.id not in dev:
            await interaction.response.send_message("このコマンドを実行する権限がありません。", ephemeral=True)
            return
        await interaction.response.send_message("Botを再起動します", ephemeral=True)

        sys.stdout.flush()
        os.execv(sys.executable, ['python3'] + sys.argv)

    @app_commands.command(name="stop", description="Botを停止する")
    async def bot_stop(self, interaction: discord.Interaction):
        if interaction.user.id not in dev:
            await interaction.response.send_message("このコマンドを実行する権限がありません。", ephemeral=True)
            return
        await interaction.response.send_message("Botを停止します", ephemeral=True)

        await bot.close()

    @app_commands.command(name="info", description="botの情報を表示します")
    async def bot_info(self, interaction: discord.Interaction):
        if interaction.user.id not in dev:
            await interaction.response.send_message("このコマンドを実行する権限がありません。", ephemeral=True)
            return
        # CPU info
        cpu_cores = psutil.cpu_count()

        # CPU usage
        cpu_usage = psutil.cpu_percent(interval=1)

        # Memory info
        mem_info = psutil.virtual_memory()
        mem_total_gb = mem_info.total / (1024 ** 3)  # total physical memory available in GB
        mem_used_gb = mem_info.used / (1024 ** 3)  # used memory in GB
        mem_percentage = mem_info.percent  # memory use percentage

        # Disk info
        disk_info = psutil.disk_usage('/')
        disk_total_gb = disk_info.total / (1024 ** 3)  # total disk space in GB
        disk_used_gb = disk_info.used / (1024 ** 3)  # used disk space in GB
        disk_percentage = disk_info.percent  # disk use percentage

        e = discord.Embed(title="Bot Info", color=discord.Color.green())
        e.add_field(name="discord.py", value=discord.__version__, inline=False)
        e.add_field(name="Python", value=sys.version, inline=False)
        e.add_field(name="CPU Cores", value=cpu_cores, inline=False)
        e.add_field(name="CPU Usage", value=f"{cpu_usage}%", inline=False)
        e.add_field(name="Total Memory", value=f"{mem_total_gb:.2f} GB", inline=False)
        e.add_field(name="Memory Usage", value=f"{mem_used_gb:.2f} GB ({mem_percentage}%)", inline=False)
        e.add_field(name="Total Disk Space", value=f"{disk_total_gb:.2f} GB", inline=False)
        e.add_field(name="Disk Usage", value=f"{disk_used_gb:.2f} GB ({disk_percentage}%)", inline=False)
        await interaction.response.send_message(embed=e)

    @app_commands.command(name="extensions", description="エクステンションをすべて表示します")
    async def list_commands(self, interaction: discord.Interaction):
        if interaction.user.id not in dev:
            await interaction.response.send_message("このコマンドを実行する権限がありません。", ephemeral=True)
            return
        embed = discord.Embed(title="Extensions", description="\n".join([i for i in bot.extensions.keys()]))
        await interaction.response.send_message(embed=embed)

        
bot.run(token)