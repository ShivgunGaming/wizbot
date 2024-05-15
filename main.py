import discord
from discord.ext import commands
import random
import string

intents = discord.Intents.default()
intents.members = True  # Enable the members intent to receive member join events

bot = commands.Bot(command_prefix='!', intents=intents)

# Placeholder for storing verified users
verified_users = {}

# Placeholder for tracking ongoing CAPTCHA verification processes
verifying_users = set()

@bot.event
async def on_member_join(member):
    await send_captcha(member)

async def send_captcha(member):
    if member.id not in verified_users and member.id not in verifying_users:
        captcha_text = generate_captcha_text()
        embed = discord.Embed(
            title="CAPTCHA Verification",
            description=f"Welcome to the server, {member.display_name}!\n\nPlease solve the CAPTCHA below to gain access.",
            color=0x7289DA
        )
        embed.set_image(url=f"https://dummyimage.com/300x100/7289DA/FFFFFF.png&text={captcha_text}")
        embed.set_footer(text="You have 60 seconds to solve the CAPTCHA.")
        await member.send(embed=embed)
        verifying_users.add(member.id)
        await verify_captcha(member, captcha_text)

async def verify_captcha(member, expected_text):
    def check(message):
        return message.author == member and message.content.lower() == expected_text.lower()

    try:
        response = await bot.wait_for('message', check=check, timeout=60)  # Wait for user response
    except asyncio.TimeoutError:
        await member.kick(reason="Failed CAPTCHA verification (timeout)")
        verifying_users.remove(member.id)
        return

    await member.send("CAPTCHA verification successful! Welcome to the server.")
    verified_users[member.id] = True  # Add the member to the dictionary of verified users
    verifying_users.remove(member.id)

    # Assign a role to the verified member by ID
    role_id = ROLE HERE  # Replace this with the actual role ID
    role = member.guild.get_role(role_id)
    if role:
        await member.add_roles(role)
    else:
        print(f"Role with ID {role_id} not found.")

    # Optionally, you can grant additional permissions or perform other actions here

def generate_captcha_text():
    captcha_characters = string.ascii_letters + string.digits
    captcha_text = ''.join(random.choices(captcha_characters, k=6))
    return captcha_text

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_message(message):
    # Check if the message author is a member who has not yet been verified
    if isinstance(message.author, discord.Member) and message.author.id not in verified_users:
        # Delete the message sent by unverified users
        await message.delete()
        # Optionally, you can send a warning message to the user explaining the verification process
        if message.author.id not in verifying_users:
            await message.author.send("You must verify the CAPTCHA before you can send messages in the server.")
            await send_captcha(message.author)
    else:
        # Allow messages from verified users to be processed normally
        await bot.process_commands(message)

bot.run('TOKEN HERE')
