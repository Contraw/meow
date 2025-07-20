import logging
import os
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- CONFIGURATION ---
# IMPORTANT: Replace this with the token from BotFather
BOT_TOKEN = '7930041841:AAEfeEeKZkIiy_nxCLDmlGtpsra609JL0Ic' 

# The username of the account that will receive the notifications (without the '@')
TARGET_USERNAME = 'marirhaf' 

# This will be populated automatically when the target user sends /start to the bot.
# Do not change this line.
TARGET_CHAT_ID = None
# --- END CONFIGURATION ---


# Set up basic logging to see errors in the console
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    This command is for the target user to authorize the bot.
    The target user MUST send /start to the bot once to register their chat_id.
    """
    global TARGET_CHAT_ID
    user = update.effective_user

    # --- NEW FEATURE: Log sender's info on /start ---
    logger.info(f"Received /start command from user: @{user.username} (Chat ID: {user.id})")

    # Check if the user sending /start is the intended target
    if user.username == TARGET_USERNAME:
        TARGET_CHAT_ID = user.id
        logger.info(f"SUCCESS: Target user authorized. Chat ID set to: {TARGET_CHAT_ID}")
        
        # --- NEW FEATURE: Send confirmation message ---
        await update.message.reply_text(
            f"✅ You are authorized! I will now forward all notifications to you."
        )
        await context.bot.send_message(
            chat_id=TARGET_CHAT_ID,
            text="⚙️ Bot is active and working! Waiting for notifications from websites..."
        )
        # --- END NEW FEATURE ---
        
    else:
        logger.warning(f"Unauthorized user @{user.username} tried to use /start.")
        await update.message.reply_text(
            "❌ You are not authorized to receive notifications from this bot."
        )


async def forward_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Receives a message sent to the bot and forwards it to the target user.
    """
    global TARGET_CHAT_ID
    
    user = update.effective_user
    received_text = update.message.text

    # --- NEW FEATURE: Log ALL incoming messages and sender info ---
    logger.info(f"Received message from @{user.username} (Chat ID: {user.id})")
    logger.info(f"Message content: {received_text}")
    # --- END NEW FEATURE ---

    if TARGET_CHAT_ID:
        try:
            # Forward the message to the target user using their chat_id
            await context.bot.send_message(
                chat_id=TARGET_CHAT_ID,
                text=received_text,
                parse_mode='Markdown'  # The website sends Markdown formatted text
            )
            logger.info(f"Successfully forwarded message to @{TARGET_USERNAME} (ID: {TARGET_CHAT_ID})")
        except Exception as e:
            logger.error(f"Failed to send message to target user: {e}")
    else:
        # This will be printed in your console if the target user hasn't sent /start yet
        logger.warning(
            "Message received, but TARGET_CHAT_ID is not set. "
            f"Please have the user @{TARGET_USERNAME} send the /start command to the bot."
        )


def main() -> None:
    """Start the bot."""
    if not BOT_TOKEN or BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        logger.error("BOT_TOKEN is not set! Please edit the script and add your bot token.")
        return

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(BOT_TOKEN).build()

    # Register the command handlers
    application.add_handler(CommandHandler("start", start_command))

    # Register the message handler to catch all text messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_message_handler))

    # Start the Bot
    logger.info("Bot starting...")
    logger.info(f"Waiting for @{TARGET_USERNAME} to send the /start command...")
    
    # Run the bot until you press Ctrl-C
    application.run_polling()


if __name__ == '__main__':
    main()
