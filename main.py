import discord
from discord.ext import commands
import random
import string
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io
import asyncio
import time
import logging

# Constants for CAPTCHA settings
CAPTCHA_TIMEOUT = 60  # Timeout in seconds
CAPTCHA_ATTEMPTS_LIMIT = 3  # Maximum number of attempts
RATE_LIMIT_WINDOW = 60  # Time window in seconds
RATE_LIMIT_MAX_ATTEMPTS = 3  # Maximum number of attempts allowed within the window

# Placeholder for storing verified users
verified_users = {}

# Placeholder for tracking ongoing CAPTCHA verification processes
verifying_users = {}

# Placeholder for storing timestamp of last CAPTCHA attempt for each user
last_attempt_timestamp = {}

# Placeholder for tracking failed CAPTCHA attempts for each user
failed_attempts = {}

# Constants for CAPTCHA retry limit
CAPTCHA_RETRY_LIMIT = 3  # Maximum number of retry attempts
CAPTCHA_RETRY_BAN_DURATION = 300  # Ban duration in seconds (5 minutes)

# Additional logging configuration
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

intents = discord.Intents.default()
intents.members = True  # Enable the members intent to receive member join events

bot = commands.Bot(command_prefix='!', intents=intents)

# Function to log IP address if available
def log_ip_address(member):
    try:
        ip_address = member.guild.get_member(member.id).guild.me.guild.voice_states[member.id].self_mute
        logging.info(f"IP address of {member.display_name}: {ip_address}")
    except:
        logging.info(f"No IP address available for {member.display_name}")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    logging.info(f'Logged in as {bot.user}')

    # Set the custom status
    activity = discord.Activity(type=discord.ActivityType.listening, name="all CAPTCHA verifications 🧙‍♂️")
    await bot.change_presence(status=discord.Status.online, activity=activity)

@bot.event
async def on_member_join(member):
    logging.info(f'{member.display_name} joined the server.')
    await send_captcha(member)

async def send_captcha(member):
    try:
        # Check rate limit
        if member.id in last_attempt_timestamp:
            current_time = time.time()
            time_since_last_attempt = current_time - last_attempt_timestamp[member.id]
            if time_since_last_attempt < RATE_LIMIT_WINDOW:
                await member.send(f"You've exceeded the rate limit. Please wait for {int(RATE_LIMIT_WINDOW - time_since_last_attempt)} seconds before trying again.")
                return

        if member.id not in verified_users and member.id not in verifying_users:
            captcha_text = generate_captcha_text()
            captcha_image = generate_captcha_image(captcha_text)
            file = discord.File(captcha_image, filename="captcha.png")

            embed = discord.Embed(
                title="Welcome to the Server!",
                description=f"Hello {member.display_name}!\nPlease complete the CAPTCHA below to gain access.",
                color=0x7289DA
            )
            embed.set_image(url="attachment://captcha.png")
            embed.set_footer(text="You have 60 seconds to solve the CAPTCHA. Type the text in the chat.")
            # Send CAPTCHA with clear instructions and interactive feedback
            message = await member.send(embed=embed, file=file)
            verifying_users[member.id] = {
                "captcha_text": captcha_text,
                "message_id": message.id
            }
            await verify_captcha(member, captcha_text)
            # Update last attempt timestamp
            last_attempt_timestamp[member.id] = time.time()
    except Exception as e:
        logging.error(f'Error sending CAPTCHA to {member.display_name}: {e}')

async def verify_captcha(member, captcha_text):
    data = verifying_users.get(member.id)
    if not data:
        return

    message_id = data["message_id"]

    def check(message):
        return message.author == member and message.content.lower() == captcha_text.lower()  # Ensure exact match, case-insensitive

    try:
        response = await bot.wait_for('message', check=check, timeout=CAPTCHA_TIMEOUT)  # Wait for user response
        await handle_verification_success(member)
    except asyncio.TimeoutError:
        await handle_verification_failure(member, "timeout")
    except Exception as e:
        logging.error(f'Error verifying CAPTCHA for {member.display_name}: {e}')
        await handle_verification_failure(member, "an unexpected error")
    finally:
        # Use await to fetch the message before deleting
        try:
            message = await member.dm_channel.fetch_message(message_id)
            await message.delete()
        except discord.NotFound:
            logging.error(f"Message with ID {message_id} not found.")
        except discord.Forbidden:
            logging.error(f"Bot does not have permission to delete message with ID {message_id}.")

def generate_captcha_text():
    captcha_characters = string.ascii_letters + string.digits
    captcha_text = ''.join(random.choices(captcha_characters, k=6))
    return captcha_text

def generate_captcha_image(text):
    # Define image dimensions and colors
    width, height = 200, 80
    background_color = (240, 240, 240)  # Light background color
    text_color = (random.randint(0, 100), random.randint(0, 100), random.randint(0, 100))  # Random dark text color
    noise_color = (random.randint(150, 255), random.randint(150, 255), random.randint(150, 255))  # Random light noise color

    # Create a blank image with specified background color
    image = Image.new("RGB", (width, height), color=background_color)

    # Create a drawing object
    draw = ImageDraw.Draw(image)

    # Add noise to the image
    for _ in range(1000):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        draw.point((x, y), fill=noise_color)

    # Add random lines
    for _ in range(5):
        x1, y1 = random.randint(0, width - 1), random.randint(0, height - 1)
        x2, y2 = random.randint(0, width - 1), random.randint(0, height - 1)
        draw.line(((x1, y1), (x2, y2)), fill=noise_color, width=2)

    # Load a random font
    font_path = random.choice(["arial.ttf", "times.ttf", "cour.ttf"])
    font_size = random.randint(36, 42)
    font = ImageFont.truetype(font_path, font_size)

    # Add text to the image with slight distortion
    for char_index, char in enumerate(text):
        char_offset_x = random.randint(-5, 5)
        char_offset_y = random.randint(-5, 5)  # <- This line was incomplete
        char_position = (10 + char_index * (font_size // 2) + char_offset_x, random.randint(5, 20) + char_offset_y)
        draw.text(char_position, char, fill=text_color, font=font)

    # Apply a blur filter to the image for a smoother appearance
    image = image.filter(ImageFilter.GaussianBlur(radius=1.5))

    # Add a border around the image
    draw.rectangle([0, 0, width - 1, height - 1], outline=(0, 0, 0), width=1)

    # Save image to a buffer
    image_buffer = io.BytesIO()
    image.save(image_buffer, format="PNG")
    image_buffer.seek(0)

    return image_buffer

async def handle_verification_success(member):
    await member.send("CAPTCHA verification successful! Welcome to the server.")
    verified_users[member.id] = True  # Add the member to the dictionary of verified users

    # Assign a role to the verified member by ID
    role_id = ROLE ID HERE  # Replace this with the actual role ID
    role = member.guild.get_role(role_id)
    if role:
        await member.add_roles(role)
    else:        
        logging.error(f"Role with ID {role_id} not found.")

    # Optionally, you can grant additional permissions or perform other actions here
    verifying_users.pop(member.id)
    logging.info(f'{member.display_name} successfully verified.')

async def handle_verification_failure(member, reason):
    await member.send(f"CAPTCHA verification failed: {reason}. You have been removed from the server.")
    await member.kick(reason=f"Failed CAPTCHA verification: {reason}")
    verifying_users.pop(member.id)
    logging.info(f'{member.display_name} failed CAPTCHA verification: {reason}')
    # Add user to failed attempts dictionary
    if member.id not in failed_attempts:
        failed_attempts[member.id] = 1
    else:
        failed_attempts[member.id] += 1
        # If retry limit exceeded, ban user temporarily
        if failed_attempts[member.id] >= CAPTCHA_RETRY_LIMIT:
            await member.ban(reason=f"Exceeded CAPTCHA retry limit: {CAPTCHA_RETRY_LIMIT} attempts")
            logging.info(f'{member.display_name} banned for exceeding CAPTCHA retry limit.')
            # Reset failed attempts after ban duration
            await asyncio.sleep(CAPTCHA_RETRY_BAN_DURATION)
            await member.guild.unban(member)
            logging.info(f'{member.display_name} unbanned after {CAPTCHA_RETRY_BAN_DURATION} seconds.')
            failed_attempts.pop(member.id)

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
