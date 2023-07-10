import redbot.core.bot
from redbot.core import commands, app_commands
from redbot.core.utils.chat_formatting import pagify
import openai
import discord
from discord.ext.commands import Context
from discord import Message
from typing import List, Sequence
from dotenv import load_dotenv
import os

load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')


class OpenAIStuff(commands.Cog):
    """A custom cog for Discord bot that uses OpenAI's GPT-3.5-turbo model."""

    def __init__(self, bot: redbot.core.bot.Red, *args, **kwargs):
        """Initialize the cog with the bot instance."""
        super().__init__(*args, **kwargs)
        self.bot = bot

    @commands.command()
    async def prompt(self, ctx: Context, *args):
        """
        Process a prompt using OpenAI's GPT-3.5-turbo model and send the response to the Discord channel.
        """
        prompt = ' '.join(args)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "You are a Discord bot named Sliske, who is sarcastic and sometimes rude, but still provides a real answer in the end."},
                {"role": "user", "content": prompt},
            ]
        )
        message = response.choices[0].message.content
        for page in pagify(message):
            await ctx.send(page)

    @commands.command(name="myname")
    async def my_name(self, ctx: Context):
        """
        Respond with the nickname of the user who invoked the command.
        """
        await ctx.send(f"Your name is {ctx.author.nick}.")

    @commands.command(name="previousmessages")
    async def previous_messages(self, ctx: Context):
        """
        Send all the cached messages from the bot to the Discord channel.
        """
        output = ""
        for message in self.bot.cached_messages:
            output += f"{message.content}\n"

        for page in pagify(output):
            await ctx.send(page)

    def get_previous_n_messages(self, ctx: Context, include_self: bool, n: int):
        """
        Get the previous 'n' messages formatted in an XML string for sending as a prompt.
        :param ctx: the command Context
        :param n:   the number of previous messages to get
        :return:    the 'n' previous messages formatted in an XML string
        """
        # Filter out messages from the bot and commands
        filtered_messages: Sequence[Message] = self.bot.cached_messages

        if not include_self:
            filtered_messages: List[Message] = [message for message in self.bot.cached_messages if
                                                message.author != self.bot.user]

        filtered_messages = [message for message in filtered_messages if not message.content.startswith(".")]
        filtered_messages = [message for message in filtered_messages if message.channel == ctx.channel]

        # Select the last 'n' messages
        selected_messages = filtered_messages[-n:]
        prompt = ""
        xml_output = ""
        for message in selected_messages:
            if message.author == self.bot.user:
                continue
            if message.author.nick is not None:
                prompt += f"{message.author.nick}: {message.content}\n"
                xml_output += f"<MESSAGE>\n<AUTHOR>{message.author.nick}</AUTHOR>\n<CONTENT>{message.content}</CONTENT>\n</MESSAGE>\n"
            else:
                prompt += f"{message.author.name}: {message.content}\n"
                xml_output += f"<MESSAGE>\n<AUTHOR>{message.author.name}</AUTHOR>\n<CONTENT>{message.content}</CONTENT>\n</MESSAGE>\n"

        return xml_output

    @commands.command()
    async def summarize(self, ctx: Context, n: int):
        """
        Summarize a conversation by selecting the last 'n' messages and generating a summary using OpenAI's GPT-3.5-turbo model.
        """
        try:
            int(n)
        except ValueError:
            await ctx.send("Bad number.")
            return

        # Filter out messages from the bot and commands
        xml_output = self.get_previous_n_messages(ctx, False, n)

        # Generate a summary of the conversation
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "Some users are having a conversation through Discord. The conversation is provided in XML format. Summarize their conversation in a way that will sound humorous to the users involved."},
                {"role": "user", "content": xml_output},
            ]
        )
        await ctx.send(response.choices[0].message.content)

    @commands.command(name="prompt2")
    async def prompt_with_context(self, ctx: Context, *args):
        """
        Prompt but the bot has context of the previous messages.
        """
        prompt = ' '.join(args)
        previous_messages_xml = self.get_previous_n_messages(ctx, True, 50)
        # Generate a summary of the conversation
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "Some users are having a conversation through Discord. The conversation is provided in XML format. You are a Discord bot named Sliske, answer the user's prompt."},
                {"role": "user", "content": previous_messages_xml},
                {"role": "user", "content": f"The user's prompt is: {prompt}"},
            ]
        )
        await ctx.send(response.choices[0].message.content)

