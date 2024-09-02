async def setup(bot):
    import discord
    from discord import app_commands

    tree = bot.tree

    @tree.command(name="ping",description="Pong")
    async def ping(interaction:discord.interactions):
        latency = bot.latency
        ping = round(latency * 1000)
        await interaction.response.send_message(f"Pong🛰 {ping}ms")