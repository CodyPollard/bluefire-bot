import discord, secrets, sqlite3, re, asyncio
from discord.ext import commands
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from eveonline.eveapi import system_kill
from sqlite3 import Error

BOT_TOKEN = secrets.BOT_TOKEN
# Set ping range in seconds, current 29-30 minutes
PING_RANGE_LOW = 1740
PING_RANGE_HIGH = 1800
PINGED = []
REFRESH_INTERVAL = 5
# Client info
prefix = '!'
bot = commands.Bot(command_prefix=prefix)
scheduler = BackgroundScheduler()


@bot.event
async def on_ready():
    # Run at start
    print('Ready.')


# Trade Block Commands #

@bot.command()
async def block(ctx, *args):
    if is_tradeblock(ctx.message.channel):
        if 'Admin' in ctx.message.author.top_role.name:
            if 'init' in args:
                # Clear Channel
                all_messages = await ctx.message.channel.history().flatten()
                for m in all_messages:
                    await m.delete()
                # Get User List
                all_users = []
                for u in ctx.guild.members:
                    if 'milk-bot' not in u.display_name:
                        all_users.append(u.display_name)
                # Make Block
                block_string = '```css\nTrade Block - !add "Player Name" or !clear\n-----------\n'
                for u in all_users:
                    block_string += '%s: \n' % u
                block_string += '```'
                # Post Block
                await ctx.send(block_string)

            elif 'purge' in args:
                await ctx.send('Purging everything but tradeblock, please wait.')
                # Get messages and return all but tradeblock
                all_messages = await ctx.message.channel.history().flatten()
                # Pop tradeblock
                all_messages.pop()
                for m in all_messages:
                    await m.delete()

            elif 'test' in args:
                all_messages = await ctx.message.channel.history().flatten()
                first_message = tblock.get_tradeblock_message(all_messages).author
                # Checking
                await ctx.send('UPDATED BLOCK')
                await ctx.send(first_message)
                all_users = ctx.guild.members
                for u in all_users:
                    print(u.display_name)
                await ctx.send(ctx.message.author.roles.name)

            else:
                await ctx.send('No arg given.')
        else:
            await ctx.send('No permissions for this command')


@bot.command(name='add')
async def block_add(ctx, arg=''):
    if is_tradeblock(ctx.message.channel):
        # Get block message
        block = tblock.get_tradeblock_message(await ctx.message.channel.history().flatten())
        if arg is '':
            await ctx.send('Missing player, try !add "Player Name".')
        else:
            new_block = ''
            for line in block.content.split('\n'):
                if ctx.message.author.display_name in line:
                    line += '%s,' % arg
                new_block += '%s\n' % line

            await block.edit(content=new_block)
            await ctx.message.delete()


@bot.command(name='clear')
async def block_clear(ctx):
    if is_tradeblock(ctx.message.channel):
        # Get block message
        block = tblock.get_tradeblock_message(await ctx.message.channel.history().flatten())
        new_block = ''
        for line in block.content.split('\n'):
            if ctx.message.author.display_name in line:
                line = '%s: ' % ctx.message.author.display_name
            new_block += '%s\n' % line

        await block.edit(content=new_block)
        await ctx.message.delete()


# Timer Commands #

@bot.command()
async def timer(ctx):
    """Passes a user message to an instance of Timers.process_timer"""
    await ctx.message.channel.send(bftimers.process_timer(ctx.message.content))


@bot.command()
async def timers(ctx):
    """Displays a list of user added timers"""

    timer_list = {}
    timer_out = ''
    # Get all timers
    for l_timers in bftimers.get_all_timers():
        timer_list[l_timers[1]] = [l_timers[0], l_timers[2]]
    # Sort timers to show closest first
    for l_timer, index in sorted(timer_list.items()):
        # Get delta between now and timer, skip if timer has passed
        delta = l_timer - datetime.now()
        if delta.total_seconds() > 0:
            timer_out += '[{}]{} {}:{} -{} - {}\n'.format(index[0], l_timer.date(), l_timer.hour,
                                                          l_timer.minute, index[1], str(delta).split('.')[0])
    # Send formated message of all timers or prompt user if none exists
    if timer_out == "":
        await ctx.message.channel.send('No timers exist. Use !timer to add one')
    else:
        await ctx.message.channel.send('```Upcoming:\n{}```'.format(timer_out))


@bot.command(name='clear-timers')
async def clear(ctx):
    """Clears entire list of timers"""

    bftimers.clear_table()
    await ctx.message.channel.send('Timers cleared')


@bot.command()
async def delete(ctx):
    """Deletes a timer at a given index"""

    try:
        timer_index = int(ctx.message.content.split(' ')[-1])
        bftimers.delete_timer(timer_index)
        await ctx.message.channel.send('Timer deleted')
    except ValueError:
        await ctx.message.channel.send('Invalid timer ID given.')


@bot.command(name='scramblethejets')
async def rat_kills(ctx):
    """Outputs list of systems with rat kills above limit"""
    in_range = system_kill()
    msg_str = '```css\nActive Systems in Range:\n'
    for sys in in_range:
        msg_str += '%s\n' % sys
    msg_str += '```'
    await ctx.message.channel.send(msg_str)


# Not Commands #
def is_tradeblock(channel):
    """Returns true if channel message is sent in contains trade-block"""

    if 'trade-block' in str(channel):
        return True


class TradeBlock:

    def get_tradeblock_message(self, messages):
        return messages[-1]


class Timers:

    is_valid = False

    def get_connection(self):
        """Returns a connection to the database at DB_PATH"""
        return sqlite3.connect(secrets.DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)

    def create_table(self, cursor):
        """Creates table bftimers"""
        cursor.execute('CREATE TABLE bftimers (id integer primary key autoincrement, timer timestamp, description text)')

    def clear_table(self):
        """Clears table bftimers"""
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("DELETE FROM bftimers")
        conn.commit()
        conn.close()

    def delete_timer(self, timer_index):
        """Deletes a timer at a given index"""
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("DELETE FROM bftimers WHERE id={}".format(timer_index))
        conn.commit()
        conn.close()

    def get_all_timers(self):
        """Returns all timers from bftimers"""
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM bftimers")
        return c.fetchall()

    def create_timer(self, timer, description):
        """Accepts a validated timer and adds it to the database"""
        # Connect to the db
        conn = self.get_connection()
        c = conn.cursor()
        # Check if table exists
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bftimers';")
        # Create table if none exists
        if c.fetchone() is None:
            print('Table doesnt exist, running create_table')
            self.create_table(c)
        c.execute("INSERT INTO bftimers (timer, description) VALUES (?, ?)", (timer, description))
        # Save insert and close
        conn.commit()
        conn.close()

    def process_timer(self, message):
        """Accepts a message from the user. Checks message structure against timer structure and adds timer if valid"""
        pattern = re.compile("([0-9]+d\s?[0-9]+h\s?[0-9]+m)")
        # Check message against timer structure
        if pattern.search(message) is not None:
            total_time = pattern.search(message).group().replace(" ", "")
            try:
                t_days = int(re.findall('(\d+)', total_time)[0])
                t_hours = int(re.findall('(\d+)', total_time)[1])
                t_minutes = int(re.findall('(\d+)', total_time)[2])
                time_left = timedelta(days=t_days, hours=t_hours, minutes=t_minutes)
                timer_ends_at = datetime.now() + time_left
            except IndexError:
                pass

            # Add the timer after validation
            self.create_timer(timer_ends_at, re.sub(pattern, '', message.split(' ', 1)[1]))
            return "Timer created for {} {}:{}".format(timer_ends_at.date(), timer_ends_at.hour, timer_ends_at.minute)
        else:
            return "Invalid timer, make sure it includes days, hours, and minutes (even if 0)"


if __name__ == '__main__':
    bftimers = Timers()
    tblock = TradeBlock()
    bot.run(BOT_TOKEN)


