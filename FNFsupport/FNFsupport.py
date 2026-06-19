import asyncio
import discord
from discord.ext import commands
from core import checks
from core.models import PermissionLevel

class CloseRequestView(discord.ui.View):
    def __init__(self, bot, original_ctx, reason):
        super().__init__(timeout=21600) # 6 hours timeout
        self.bot = bot
        self.original_ctx = original_ctx
        self.reason = reason
        self.message = None

    async def on_timeout(self):
        if self.message:
            await self.message.edit(content="Ticket was automatically closed due to inactivity.", view=None)
        await self.close_ticket(self.original_ctx, "Automatically closed after 6 hours of inactivity.")

    async def close_ticket(self, ctx, close_reason):
        # Modmail bot specific closing logic
        # This part needs to interact with Modmail's internal closing mechanism.
        # Since direct Modmail API access is not available in this sandbox, we'll simulate it.
        log_channel_id = 1445473996081725460 # User provided log channel ID
        log_channel = self.bot.get_channel(log_channel_id)

        if log_channel:
            embed = discord.Embed(title="Ticket Closed", description=f"Reason: {close_reason}", color=discord.Color.red())
            embed.add_field(name="Ticket ID", value=ctx.channel.name, inline=False)
            embed.add_field(name="Closed by", value=self.bot.user.display_name, inline=False)
            await log_channel.send(embed=embed)
        
        # Send closing message to the ticket channel (user who opened the ticket)
        await ctx.channel.send(embed=discord.Embed(description=f"Your ticket has been closed. Reason: {close_reason}", color=discord.Color.red()))
        
        # In a real Modmail plugin, you would call a Modmail API to close the ticket.
        # Example: await self.bot.modmail_api.close_ticket(ctx.channel.id, close_reason)
        # For now, we are simulating the closing by sending messages.


    @discord.ui.button(label="Accept", style=discord.ButtonStyle.success)
    async def accept_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="Ticket is being closed.", view=None)
        await self.close_ticket(self.original_ctx, self.reason)
        self.stop()

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.danger)
    async def decline_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="Ticket remains open.", view=None)
        self.stop()

class FNFsupport(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="closerequest", description="Sends a request to close the ticket with a reason.")
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def closerequest(self, ctx: commands.Context, *, reason: str):
        embed = discord.Embed(
            title="Close Request",
            description=f"Are you ready for your ticket to be closed? Please accept or decline.\nReason: {reason}",
            color=discord.Color.blue()
        )
        view = CloseRequestView(self.bot, ctx, reason)
        message = await ctx.send(embed=embed, view=view)
        view.message = message

async def setup(bot: commands.Bot):
    await bot.add_cog(FNFsupport(bot))
