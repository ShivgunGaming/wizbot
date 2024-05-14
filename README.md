# Wizbot - CAPTCHABOT 🧙‍♂️

## Introduction

This Discord bot is designed to add a CAPTCHA verification process for new members joining a server. It helps in preventing spam or unauthorized access by requiring users to solve a CAPTCHA puzzle before gaining full access to the server.

## Features

- CAPTCHA verification for new members joining the server.
- Customizable CAPTCHA text generation.
- Automatic role assignment upon successful verification.
- Timeout mechanism for CAPTCHA verification process.
- Real-time verification feedback to the user.

## Setup Instructions 📝

1. **Installation**:
   - Clone this repository to your local machine.
   - Ensure you have Python 3.6 or higher installed.

2. **Dependencies**:
   - Install the required dependencies using pip:
     ```bash
     pip install discord.py
     ```

3. **Bot Token**:
   - Obtain a bot token from the Discord Developer Portal.
   - Replace `'TOKEN HERE'` in the code with your bot token.

4. **Running the Bot**:
   - Execute the bot script using Python:
     ```bash
     python main.py
     ```
   - Ensure the bot has necessary permissions to read/write messages, manage roles, and kick members.

5. **Customization**:
   - Customize the CAPTCHA text generation logic in the `generate_captcha_text()` function to suit your needs.
   - Modify the verification process, such as timeout duration or role assignment, according to your server's requirements.

## Usage 🧩

- When a new member joins the server, the bot sends them a direct message with a CAPTCHA challenge.
- The member must solve the CAPTCHA within a specified time limit by replying to the bot's message with the correct text.
- Upon successful verification, the member gains access to the server and is assigned a specified role.
- If the verification fails (e.g., due to timeout), the bot removes the member from the server.

## Inviting the Bot to Your Server 🚪

To invite the Wizbot CAPTCHABOT to your server, use the following invite link: [Invite Wizbot](https://discord.com/oauth2/authorize?client_id=1239446199661232248&permissions=29681915919607&scope=bot)
- Note: To assign roles, the bot needs to be placed on the top of the role hierarchy to ensure it can assign roles effectively.


## Contributing 🚀

Contributions are welcome! If you have suggestions, feature requests, or found a bug, feel free to open an issue or submit a pull request.
