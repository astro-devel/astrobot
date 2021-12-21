def is_kevinshome(ctx):
    '''check to see if invoking user is kevinshome'''
    return ctx.author.id == 416752352977092611

def is_victor(ctx):
    '''check to see if invoking user is victorisasleep'''
    return ctx.author.id == 593511728973742082


def always_false(ctx):
    '''always returns false; used for testing'''
    return False
def always_true(ctx):
    '''always returns true; used for testing'''
    return True

def invoker_is_lower_rank(ctx):
    '''check if invoker is above victim in role hierarchy'''
    if ctx.author.bot or ctx.message.content[1:] == 'help':
        # check doesn't need to be run if bot-invoked
        # also had to add exception for help command??
        # idk why this check has to be invoked each time '!help' is, but whatever, this is a simple patch for rn
        # TODO: figure this out ^^^
        return True
    return ctx.author.top_role.position > ctx.message.mentions[0].top_role.position