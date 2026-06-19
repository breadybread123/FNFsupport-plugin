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
        self.log_channel_id = 1445473996081725460 # User provided log channel ID

    async def on_timeout(self):
        if self.message:
            await self.message.edit(content="Ticket was automatically closed due to inactivity.", view=None)
        await self._close_modmail_thread(self.original_ctx, "Automatically closed after 6 hours of inactivity.")

    async def _close_modmail_thread(self, ctx, close_reason):
        # Attempt to get the Modmail thread object from the context
        # This assumes ctx.thread is available or can be accessed via ctx.channel
        # If this doesn't work, further investigation into Modmail's internal API would be needed.
        try:
            # Modmail threads often have a 'close' method directly on the thread object
            # or can be accessed via bot.modmail.close_thread(thread_id)
            # For now, we'll try to use ctx.thread.close() if available, or simulate.
            # The Modmail bot's internal structure is not fully exposed here.
            
            # Send log to the specified log channel
            log_channel = self.bot.get_channel(self.log_channel_id)
            if log_channel:
                log_embed = discord.Embed(title="Ticket Closed", description=f"Reason: {close_reason}", color=discord.Color.red())
                log_embed.add_field(name="Ticket ID", value=ctx.channel.name, inline=False)
                log_embed.add_field(name="Closed by", value=self.bot.user.display_name, inline=False)
                await log_channel.send(embed=log_embed)

            # Send closing message to the user who opened the ticket (via the thread channel)
            user_embed = discord.Embed(description=f"Your ticket has been closed. Reason: {close_reason}", color=discord.Color.red())
            await ctx.channel.send(embed=user_embed)

            # Attempt to close the thread using Modmail's internal mechanism
            # This is a placeholder and might need adjustment based on actual Modmail API
            if hasattr(ctx, 'thread') and hasattr(ctx.thread, 'close'):
                await ctx.thread.close(closer=self.bot.user, silent=False, delete_channel=True, message=close_reason)
            elif hasattr(self.bot, 'modmail') and hasattr(self.bot.modmail, 'close_thread'):
                # This is a hypothetical call, actual method might differ
                await self.bot.modmail.close_thread(ctx.channel.id, closer=self.bot.user, reason=close_reason)
            else:
                # Fallback if direct closing method is not found
                await ctx.channel.send(embed=discord.Embed(description="Could not programmatically close the Modmail thread. Please close it manually.", color=discord.Color.orange()))

        except Exception as e:
            print(f"Error closing Modmail thread: {e}")
            await ctx.channel.send(embed=discord.Embed(description=f"An error occurred while trying to close the ticket: {e}", color=discord.Color.red()))

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.success)
    async def accept_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="Ticket is being closed.", view=None)
        await self._close_modmail_thread(self.original_ctx, self.reason)
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
