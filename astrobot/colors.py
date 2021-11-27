import discord

class MochjiColor(discord.Colour):
    @classmethod
    def black(c):
        return c.from_rgb(24, 24, 24)
    @classmethod
    def red(c):
        return c.from_rgb(201, 54, 80)
    @classmethod
    def orange(c):
        return c.from_rgb(221, 129, 54)
    @classmethod
    def yellow(c):
        return c.from_rgb(221, 200, 98)
    @classmethod
    def green(c):
        return c.from_rgb(118, 197, 104)
    @classmethod
    def blue(c):
        return c.from_rgb(59, 121, 190)
    @classmethod
    def purple(c):
        return c.from_rgb(134, 76, 194)
    @classmethod
    def white(c):
        return c.from_rgb(217, 217, 217)
    