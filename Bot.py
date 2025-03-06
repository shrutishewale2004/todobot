import os
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext
)
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Global dictionary to store user to-do lists
user_todos = {}

# Define conversation states
ADDING_TODO = 1

# /start command
async def start(update: Update, context: CallbackContext):
    if update.message:
        await update.message.reply_text("Hello! I am your Task bot. Use /addtask to add tasks.")

# /addtask command - Start task addition
async def addtask(update: Update, context: CallbackContext):
    if update.message:
        await update.message.reply_text("Please send me your tasks, one per message. Send /donetask when you're done.")
        user_id = update.message.from_user.id
        user_todos[user_id] = []  # Initialize user's task list
    return ADDING_TODO

# Adding tasks handler
async def add_todo_item(update: Update, context: CallbackContext):
    if update.message:
        user_id = update.message.from_user.id
        todo_item = update.message.text

        user_todos[user_id].append(todo_item)  # Add task to user's list
        await update.message.reply_text(f"Added: {todo_item}")

    return ADDING_TODO  # Keep collecting tasks

# /donetask command - End task addition and show list
async def donetask(update: Update, context: CallbackContext):
    if update.message:
        user_id = update.message.from_user.id

        if user_id in user_todos and user_todos[user_id]:
            todos = "\n".join(user_todos[user_id])
            await update.message.reply_text(f"Here is your task list:\n{todos}")
        else:
            await update.message.reply_text("You don't have any tasks.")

    return ConversationHandler.END  # End the conversation

# /showtask command - Show current tasks
async def showtask(update: Update, context: CallbackContext):
    if update.message:
        user_id = update.message.from_user.id

        if user_id in user_todos and user_todos[user_id]:
            todos = "\n".join(user_todos[user_id])
            await update.message.reply_text(f"Here are your current tasks:\n{todos}")
        else:
            await update.message.reply_text("You don't have any tasks yet. Use /addtask to add some.")

# /deletetask command - Delete a task or clear the list
async def deletetask(update: Update, context: CallbackContext):
    if update.message:
        user_id = update.message.from_user.id

        if user_id in user_todos and user_todos[user_id]:
            if context.args:
                try:
                    task_number = int(context.args[0]) - 1  # Convert argument to index

                    if 0 <= task_number < len(user_todos[user_id]):
                        deleted_task = user_todos[user_id].pop(task_number)
                        await update.message.reply_text(f"Deleted task: {deleted_task}")
                    else:
                        await update.message.reply_text("Invalid task number.")
                except ValueError:
                    await update.message.reply_text("Please provide a valid task number.")
            else:
                user_todos[user_id].clear()  # Delete all tasks
                await update.message.reply_text("Deleted the entire task list.")
        else:
            await update.message.reply_text("You don't have any tasks to delete.")

# Unknown command handler
async def unknown(update: Update, context: CallbackContext):
    if update.message:
        await update.message.reply_text("Sorry, I didn't understand that command.")

# Main function
def main():
    # Get bot token from environment variable
    bot_token = os.getenv("BOT_TOKEN")

    # Debug: Ensure bot token is loaded
    if bot_token is None:
        print("Error: Bot token not found in environment variables.")
        return
    else:
        print("Bot token loaded successfully.")

    # Create bot application
    application = Application.builder().token(bot_token).build()

    # Conversation handler for adding tasks
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("addtask", addtask)],
        states={
            ADDING_TODO: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_todo_item)],
        },
        fallbacks=[CommandHandler("donetask", donetask)]
    )

    # Register command handlers
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("showtask", showtask))
    application.add_handler(CommandHandler("deletetask", deletetask))
    application.add_handler(MessageHandler(filters.COMMAND, unknown))  # Catch unknown commands

    # Start polling for updates
    application.run_polling()

# Run the bot
if __name__ == "__main__":
    main()
