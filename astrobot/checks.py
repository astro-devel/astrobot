def is_kevinshome(ctx):
    """check to see if invoking user is kevinshome"""
    return ctx.author.id == 416752352977092611

def is_victor(ctx):
    """check to see if invoking user is victorisasleep"""
    return ctx.author.id == 593511728973742082

def invoker_is_lower_rank(ctx):
    """check if invoker is above victim in role hierarchy"""
    if ctx.author.bot or ctx.message.content[1:] == 'help' or ctx.author == ctx.guild.owner:
        # check doesn't need to be run if:
            # - command is bot invoked (i.e. automod)
            # - command is being run by HelpCommand (TODO: check on why this is)
            # - command invoker is the guild owner
        return True
    return ctx.author.top_role.position > ctx.message.mentions[0].top_role.position