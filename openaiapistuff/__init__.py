from .openaistuff import OpenAIStuff


async def setup(bot):
    await bot.add_cog(OpenAIStuff(bot))
