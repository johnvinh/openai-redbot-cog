import redbot.core.bot
from redbot.core import commands, app_commands
from redbot.core.utils.chat_formatting import pagify
import openai
import discord
from discord.ext.commands import Context
from discord import Message
from typing import List
from dotenv import load_dotenv
import os

load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')


class OpenAIStuff(commands.Cog):
    """My custom cog"""

    def __init__(self, bot: redbot.core.bot.Red, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot

    @commands.command()
    async def prompt(self, ctx: Context, *args):
        prompt = ' '.join(args)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "You are a Discord bot named Sliske, who is sarcastic and sometimes rude, but still provides a real answer in the end."},
                {"role": "user", "content": prompt},
            ]
        )
        await ctx.send(response.choices[0].message.content)

    @commands.command(name="myname")
    async def my_name(self, ctx: Context):
        await ctx.send(f"Your name is {ctx.author.nick}.")

    @commands.command(name="previousmessages")
    async def previous_messages(self, ctx: Context):
        output = ""
        for message in self.bot.cached_messages:
            output += f"{message.content}\n"

        for page in pagify(output):
            await ctx.send(page)

    @commands.command()
    async def summarize(self, ctx: Context, n: int):
        """
        Summarize a conversation.
        """
        try:
            int(n)
        except ValueError:
            await ctx.send("Bad number.")
            return

        filtered_messages: List[Message] = [message for message in self.bot.cached_messages if
                                            message.author != self.bot.user]
        filtered_messages = [message for message in filtered_messages if not message.content.startswith(".")]
        filtered_messages = [message for message in filtered_messages if message.channel == ctx.channel]
        
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

        # await ctx.send(xml_output)

        # await ctx.send(prompt)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "Some users are having a conversation through Discord. The conversation is provided in XML format. Summarize their conversation in a way that will sound humorous to the users involved."},
                {"role": "user", "content": xml_output},
            ]
        )
        await ctx.send(response.choices[0].message.content)
