# 1 - Import the necessary libraries
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext, CallbackQueryHandler)
from datetime import datetime
import logging
import json
import os

# Define empty lists for received_messages and start_command_triggered
received_messages = []
start_command_triggered = []


def load_menus_json():
    global menus  # This line allows us to access and modify the global menus variable
    if os.path.exists('menus.json'):
        with open('menus.json', 'r') as file:
            menus = json.load(file)
    else:
        menus = create_menu_json()
    return menus

def create_menu_json():
    global menus  # This line allows us to access and modify the global menus variable
    # creating a dictionary to represent the menu and sub-menus
    menus = {
        'main_menu': {
            'buttons': [],
            'sub_menus': {}
        }
    }

    # writing the menu data to a JSON file
    with open('menus.json', 'w') as file:
        json.dump(menus, file)

    return menus

log_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'bot.log')
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

# Define the function to create the inline keyboard from menus
def create_keyboard_from_menus(menus):
    keyboard = []

    for menu_name, menu_content in menus.items():
        # Add a new row for each menu
        row = []
        
        for button in menu_content['buttons']:
            row.append(InlineKeyboardButton(button['text'], callback_data=button['id']))

        keyboard.append(row)

    return InlineKeyboardMarkup(keyboard)


menus = load_menus_json()

def start(update: Update, _: CallbackContext) -> None:
    """Sends a welcome message and helps the user use the bot."""
    logger.info("Command received: %s", update.message.text)

    # Add a print statement to check if the function is called
    print("Start function called")

    try:
        # Load the JSON file
        with open('menus.json') as file:
            menus = json.load(file)

        # Print menus for debugging
        print(f"Loaded menus: {menus}")

        # Create inline keyboard from the menus
        keyboard = create_keyboard_from_menus(menus)

        # Send a message with the created inline keyboard
        update.message.reply_text(
            "Welcome to our Telegram Bot! Please select an option:",
            reply_markup=keyboard
        )
    except Exception as e:
        print(f"Error occurred: {e}")



def echo(update: Update, _: CallbackContext) -> None:
    """Echo the user message."""
    logger.info("Message received: %s", update.message.text)
    update.message.reply_text(update.message.text)

# Nuke states
confirm_nuke, get_nuke_password, final_warning = range(3)

# Nuke command handler
def nuke(update: Update, context: CallbackContext) -> int:
    logger.info("Command received: %s", update.message.text)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Nuke command received. Please confirm by typing 'CONFIRM'. This action cannot be undone.")
    return confirm_nuke

# Confirm nuke
def confirm_nuke(update: Update, context: CallbackContext) -> int:
    logger.info("Command received: %s", update.message.text)
    if update.message.text == 'CONFIRM':
        context.bot.send_message(chat_id=update.effective_chat.id, text="Confirmation received. Please enter the nuke password:")
        return get_nuke_password
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Incorrect confirmation. Nuke command cancelled.")
        return ConversationHandler.END

# Get nuke password
def get_nuke_password(update: Update, context: CallbackContext) -> int:
    logger.info("Command received: %s", update.message.text)
    entered_password = update.message.text
    if entered_password == config['nuke_password']:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Correct nuke password entered. This is your final warning. Type 'NUKE' to execute. This action cannot be undone.")
        return final_warning
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Incorrect nuke password. Nuke command cancelled.")
        return ConversationHandler.END

# Final warning before nuke
def final_warning(update: Update, context: CallbackContext) -> int:
    logger.info("Command received: %s", update.message.text)
    if update.message.text == 'NUKE':
        # Here you can add the logic to block all users, delete conversations and files
        # Since this is a destructive operation, I will leave it empty for now
        # Remember to exclude the admin from the nuke operation
        context.bot.send_message(chat_id=update.effective_chat.id, text="Nuke executed.")
        return ConversationHandler.END
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Incorrect final warning response. Nuke command cancelled.")
        return ConversationHandler.END

def normal_message(update: Update, context: CallbackContext) -> None:
    logger.info("Command received: %s", update.message.text)
    """
    Handles any text messages that are not commands
    """
    # Get the user's message
    message = update.message.text

    # Log the user's message
    logger.info("Received non-command message: %s", message)

    # You can define default bot behavior for non-command messages here. For example:
    update.message.reply_text(
        "I'm sorry, I didn't understand that. Could you please try again or use a command?"
    )


def config(update, context):
    """Enter the configuration menu, saving the current state."""
    # Save the current state
    context.user_data['previous_state'] = context.user_data.get('state')
    logger.info("Command received: %s", update.message.text)

    keyboard = [
        [InlineKeyboardButton("Add Button", callback_data="add_button")],
        [InlineKeyboardButton("Remove Button", callback_data="remove_button")],
        [InlineKeyboardButton("Rename Button", callback_data="rename_button")],
        [InlineKeyboardButton("Move Button", callback_data="move_button")],
        [InlineKeyboardButton("Change Password", callback_data="change_password")],
        [InlineKeyboardButton("Exit Config", callback_data="exit_config")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Please choose an action:', reply_markup=reply_markup)

    return start

def exit_config(update, context):
    """Exit the configuration menu and return to the previous state."""
    # Create and send an exit message
    text = "Exiting configuration menu."
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    # Return to the previous state
    return context.user_data.get('previous_state', start)  # Fallback to start if no previous state is saved

# Define the add_button function
def add_button(update, context):
    logger.info("Command received: %s", update.message.text)
    query = update.callback_query
    query.answer()

    # Load the JSON file
    menus = load_menus_json()

    # Generate a list of all menus and sub-menus
    menu_names = []
    for menu in menus:
        menu_names.append(menu)
        if "sub_menus" in menus[menu]:
            for sub_menu in menus[menu]["sub_menus"]:
                menu_names.append(sub_menu)

    # Display the list to the admin for selection
    keyboard = [[InlineKeyboardButton(m, callback_data=f"add_to_{m}")] for m in menu_names]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Select a menu to add the button to:", reply_markup=reply_markup)

    return add_button_type

# Define the function to handle the button type selection
def add_button_type(update: Update, context: CallbackContext) -> int:
    logger.info("Command received: %s", update.callback_query.data)
    query = update.callback_query
    query.answer()

    # Parse the callback_data to extract the menu name
    menu_name = query.data.split("_")[2]

    # Store the menu name in the context user data for later use
    context.user_data['menu'] = menu_name

    # Provide button types for the admin to choose
    keyboard = [
        [InlineKeyboardButton("Text", callback_data="text")],
        [InlineKeyboardButton("Image", callback_data="image")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Select the type of button:", reply_markup=reply_markup)

    return add_button_name

# Define the function to handle the button name input
def add_button_name(update: Update, context: CallbackContext) -> int:
    logger.info("Command received: %s", update.callback_query.data)
    query = update.callback_query
    query.answer()

    # Capture the button type from the previous step
    button_type = query.data

    # Store the button type in the context user data for later use
    context.user_data['type'] = button_type

    # Ask the admin to send the button name
    query.edit_message_text(text="Please send the name of the button.")

    return add_button_image if button_type == "image" else add_button_text

# Define function to handle image button addition
def add_button_image(update: Update, context: CallbackContext) -> None:
    # Obtain user data
    user_data = context.user_data

    # Save received image to a file with the specified name and format
    button_name = user_data["button_name"]
    date_time_now = datetime.datetime.now()
    formatted_time = date_time_now.strftime("%d-%m-%Y_%I-%M-%p")
    image_file_name = f"{button_name}_{formatted_time}.jpg"
    image_file_path = f"images/{image_file_name}"
    context.bot.getFile(update.message.photo[-1].file_id).download(image_file_path)

    # Create new button with the received image as content
    new_button = {
        "type": "image",
        "name": button_name,
        "content": image_file_path
    }

    # Add new button to the corresponding menu in menu_data
    user_data["menu_data"][user_data["current_menu"]]["buttons"].append(new_button)

    # Inform the user about successful button addition
    update.message.reply_text("Image button added successfully!")
    
    # Set the current menu back to config after successful button addition
    context.user_data['current_menu'] = 'config'

def add_button_text(update: Update, context: CallbackContext) -> int:
    logger.info("Command received: %s", update.message.text)

    # Extracting the user message
    text = update.message.text
    # Storing the text message into the user_data dictionary
    context.user_data['message'] = text

    # We're now ready to create the button
    return create_button(update, context)

def create_button(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

    button_name = query.data.split("_")[2]

    # Instead of a unique callback, we'll use the button name
    new_button = {
        "name": button_name,
        "callback": button_name,
        "type": context.user_data['button_type'],
        "message" if context.user_data['button_type'] == "text" else "image": context.user_data['button_info']
    }

    # Add the button to the selected menu
    for menu in menus:
        if menu['name'] == context.user_data['menu_name']:
            menu["buttons"].append(new_button)
            break

    # Save the updated menus
    save_menu()

    query.edit_message_text(text=f"Button {button_name} has been created.")
    
    return config(update, context)


# This function handles the "remove_button" state
def remove_button(update: Update, context: CallbackContext) -> None:
    logger.info("Command received: %s", update.callback_query.data)
    global menus  # This line allows us to access and modify the global menus variable

    query = update.callback_query
    query.answer()

    # Generate a list of all buttons (from both main menus and sub-menus)
    buttons = []
    for menu_key, menu_value in menus.items():
        buttons += menu_value["buttons"]

    # Display the list to the admin for selection
    keyboard = [
        [InlineKeyboardButton(b["text"], callback_data=f"confirm_button_removal_{b['id']}") for b in buttons]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Select a button to remove:", reply_markup=reply_markup)

# This function handles the "confirm_button_removal" state
def confirm_button_removal(update: Update, context: CallbackContext) -> None:
    logger.info("Command received: %s", update.callback_query.data)
    global menus  # This line allows us to access and modify the global menus variable

    query = update.callback_query
    query.answer()

    # Extract the button ID from the callback data
    button_id = query.data.split("_")[2]

    # Find the button to remove and delete its associated image (if any)
    for menu_key, menu_value in menus.items():
        for i, button in enumerate(menu_value["buttons"]):
            if button["id"] == button_id:
                if button["type"] == "image":
                    os.remove(button["content"])
                del menu_value["buttons"][i]
                break

    # Save the updated menu using the save_menu() function
    save_menu()

    query.edit_message_text(text="Button removed successfully.")


def rename_button(update: Update, context: CallbackContext):
    logger.info("Command received: %s", update.message.text)
    global menus  # This line allows us to access and modify the global menus variable
    """This state will ask the admin what type of item (menu, sub-menu, button) they want to rename"""
    query = update.callback_query
    query.answer()

    # Prepare the options
    options = ["menu", "sub-menu", "button"]

    # Create an inline keyboard with the options
    keyboard = [
        [InlineKeyboardButton(opt, callback_data=f"rename_{opt}") for opt in options]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Ask the admin what type of item they want to rename
    query.edit_message_text(text="What type of item do you want to rename?", reply_markup=reply_markup)

    return rename_item_selection

def rename_item_selection(update: Update, context: CallbackContext):
    logger.info("Command received: %s", update.message.text)
    global menus  # This line allows us to access and modify the global menus variable
    """This state will present a list of items (of the selected type) for the admin to select which one to rename"""
    query = update.callback_query
    query.answer()

    # Get the selected item type
    item_type = query.data.split("_")[1]

    # Load the menu JSON
    menus = load_menus_json()

    # Prepare the list of items based on the selected type
    items = []
    if item_type == "menu":
        items = [menu["name"] for menu in menus]
    elif item_type == "sub-menu":
        items = [submenu["name"] for menu in menus for submenu in menu["submenus"]]
    elif item_type == "button":
        items = [button["name"] for menu in menus for button in menu["buttons"]]

    # Create an inline keyboard with the items
    keyboard = []
    for i in range(0, len(items), 2):  # We make it 2 columns wide
        row = [InlineKeyboardButton(items[i], callback_data=f"rename_{items[i]}")]
        if i + 1 < len(items):
            row.append(InlineKeyboardButton(items[i+1], callback_data=f"rename_{items[i+1]}"))
        keyboard.append(row)

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Ask the admin which item they want to rename
    query.edit_message_text(text=f"Which {item_type} do you want to rename?", reply_markup=reply_markup)

    return rename_item_name

def rename_item_name(update: Update, context: CallbackContext):
    logger.info("Command received: %s", update.message.text)
    global menus  # This line allows us to access and modify the global menus variable
    """This state will receive the new item name and update the JSON and local image file if needed"""
    new_item_name = update.message.text

    # Load the menu JSON
    menus = load_menus_json()

    # Find the item to be renamed and update its name
    for menu in menus:
        if menu["name"] == context.user_data["item_to_rename"]:
            menu["name"] = new_item_name
        else:
            for submenu in menu["submenus"]:
                if submenu["name"] == context.user_data["item_to_rename"]:
                    submenu["name"] = new_item_name
                else:
                    for button in menu["buttons"]:
                        if button["name"] == context.user_data["item_to_rename"]:
                            # Update the button name
                            button["name"] = new_item_name

                            # If it's an image button, rename the image file
                            if button["type"] == "image":
                                old_image_path = button["image_path"]
                                new_image_path = old_image_path.replace(context.user_data["item_to_rename"], new_item_name)
                                os.rename(old_image_path, new_image_path)
                                button["image_path"] = new_image_path

    # Save the updated menus
    save_menu(menus)

    # Inform the admin that the item has been renamed
    update.message.reply_text(f"The item has been renamed to {new_item_name}.")

    # Return back to config menu
    return config(update, context)

def move_button(update: Update, context: CallbackContext) -> str:
    logger.info("Command received: %s", update.message.text)
    global menus  # This line allows us to access and modify the global menus variable
    """Handles the initial stage of moving a button by presenting the admin with types of buttons to move"""
    query = update.callback_query
    query.answer()

    # Define an InlineKeyboard with the options for the button types
    keyboard = [
        [InlineKeyboardButton("Menu", callback_data="menu_move")],
        [InlineKeyboardButton("Sub-menu", callback_data="sub_menu_move")],
        [InlineKeyboardButton("Button", callback_data="button_move")],
        [InlineKeyboardButton("Cancel", callback_data="cancel_move")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Ask the admin to select the type of button they want to move
    query.edit_message_text(text="What type of button would you like to move?", reply_markup=reply_markup)

    # Transition to the next state where we'll process the type of button to move
    return move_button_type

def move_button_type(update: Update, context: CallbackContext) -> str:
    logger.info("Command received: %s", update.message.text)
    global menus  # This line allows us to access and modify the global menus variable
    """Handles the selected button type and displays the corresponding list of buttons"""
    query = update.callback_query
    query.answer()

    # Extract the type of button to move from the callback data
    move_type = query.data

    # If the admin has decided to cancel the operation, we return to the config menu
    if move_type == "cancel_move":
        query.edit_message_text(text="Button moving cancelled. Returning to the config menu.")
        return config(update, context)

    # Store the move type in context.user_data for use in subsequent states
    context.user_data['move_type'] = move_type

    # Load the menus from the JSON file
    menus = load_menus_json()

    # Depending on the move_type, we prepare different lists of options
    options = []
    if move_type == "menu_move":
        options = [InlineKeyboardButton(menu['name'], callback_data=menu['name']) for menu in menus]
    elif move_type == "sub_menu_move":
        options = [InlineKeyboardButton(submenu['name'], callback_data=submenu['name']) for menu in menus for submenu in menu['submenus']]
    elif move_type == "button_move":
        options = [InlineKeyboardButton(button['text'], callback_data=button['callback_data']) for menu in menus for button in menu['buttons']]

    # We generate a 2-column keyboard layout with the prepared options and a 'Cancel' button
    keyboard = [options[i:i+2] for i in range(0, len(options), 2)]
    keyboard.append([InlineKeyboardButton("Cancel", callback_data="cancel_move")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Ask the admin to select the button to move
    query.edit_message_text(text="Choose the button to move:", reply_markup=reply_markup)

    # Transition to the next state where we'll process the button to be moved
    return move_button_selection

def move_button_selection(update: Update, context: CallbackContext) -> str:
    logger.info("Command received: %s", update.message.text)
    global menus  # This line allows us to access and modify the global menus variable
    """Handles the selected button to move and presents the admin with a list of locations to move the button to"""
    query = update.callback_query
    query.answer()

    # Get the button to move from the callback data
    button_to_move = query.data

    # If the admin has decided to cancel the operation, we return to the config menu
    if button_to_move == "cancel_move":
        query.edit_message_text(text="Button moving cancelled. Returning to the config menu.")
        return config(update, context)

    # Store the button to move in context.user_data for use in subsequent states
    context.user_data['button_to_move'] = button_to_move

    # Load the menus from the JSON file
    menus = load_menus_json()

    # Prepare a list of InlineKeyboardButtons representing all the buttons, excluding the one to move
    buttons = []
    for menu in menus:
        for button in menu['buttons']:
            if button['callback_data'] != button_to_move:
                buttons.append(InlineKeyboardButton(button['text'], callback_data=button['callback_data']))

    # Generate a 2-column keyboard layout with the buttons and an 'Other menu/sub-menu' option
    keyboard = [buttons[i:i+2] for i in range(0, len(buttons), 2)]
    keyboard.append([InlineKeyboardButton('Other menu/sub-menu', callback_data='other_menu')])
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Ask the admin to choose the new location for the button
    query.edit_message_text(text="Choose the new location for the button:", reply_markup=reply_markup)

    # Transition to the next state where we'll process the new location for the button
    return move_button_to_other_menu

def move_button_to_other_menu(update: Update, context: CallbackContext) -> str:
    logger.info("Command received: %s", update.message.text)
    global menus  # This line allows us to access and modify the global menus variable
    """Presents the admin with a list of other menus/sub-menus to move the button to"""
    query = update.callback_query
    query.answer()

    # Load the menus from the JSON file
    menus = load_menus_json()

    # Create a list of InlineKeyboardButtons, one for each menu/sub-menu
    menu_buttons = [InlineKeyboardButton(menu['name'], callback_data=menu['name']) for menu in menus]

    # Add a 'cancel' option to the list of buttons
    menu_buttons.append(InlineKeyboardButton('Cancel', callback_data='cancel_move'))

    # Generate a 2-column keyboard layout with the menu buttons
    keyboard = [menu_buttons[i:i+2] for i in range(0, len(menu_buttons), 2)]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Ask the admin to select the destination menu or submenu
    query.edit_message_text(text="Select the destination menu or submenu:", reply_markup=reply_markup)

    # Transition to the next state where we'll process the selected destination
    return move_button_to_other_menu_selected

def move_button_to_other_menu_selected(update: Update, context: CallbackContext) -> str:
    logger.info("Command received: %s", update.message.text)
    global menus  # This line allows us to access and modify the global menus variable
    """
    This function is triggered after the admin has selected a menu or submenu to move the button to.
    It allows the admin to choose the exact location within the selected menu or submenu for the button.
    If confirmed, the button is moved to the chosen location.
    The updated information is then written to the JSON file.
    """
    query = update.callback_query
    query.answer()

    if query.data == 'cancel_move':
        query.edit_message_text(text="Button move cancelled. Returning to the config menu.")
        return config(update, context)

    selected_menu = query.data
    context.user_data['selected_menu'] = selected_menu

    # Load the menus from the JSON file
    menus = load_menus_json()

    # Find the selected menu or submenu and generate a list of its buttons
    for menu in menus:
        if menu['name'] == selected_menu:
            if len(menu['buttons']) > 0:
                button_texts = [button['text'] for button in menu['buttons']]
                button_texts.append('Place here')
                keyboard = [button_texts[i:i+2] for i in range(0, len(button_texts), 2)]
                reply_markup = InlineKeyboardMarkup(keyboard)

                query.edit_message_text(
                    text="Choose the new location for the button within the selected menu or submenu:",
                    reply_markup=reply_markup,
                )
            else:
                menu['buttons'].append(context.user_data['button_to_move'])
                # Save the updated menus
                save_menu(menus)

                query.edit_message_text(
                    text="Button moved. Returning to the config menu.",
                )
            break

    return config(update, context)

def back(update: Update, context: CallbackContext) -> int:
    logger.info("Command received: %s", update.message.text)
    global menus  # This line allows us to access and modify the global menus variable
    """Go back to previous state."""

    # Pop the last state from the list of states in context.user_data
    previous_state = context.user_data.get('states', []).pop(-1)

    # Go back to the previous state
    return previous_state


# define a function to change password
def change_password(update: Update, context: CallbackContext) -> int:
    logger.info("Command received: %s", update.message.text)
    global menus  # This line allows us to access and modify the global menus variable
    """
    This function handles the 'change_password' state.
    It allows the admin to choose which password they want to change.
    """
    # fetch the query data
    query = update.callback_query
    query.answer()

    # create an inline keyboard to ask the admin which password they want to change
    keyboard = [
        [InlineKeyboardButton("Admin Password", callback_data='admin_password')],
        [InlineKeyboardButton("Nuke Password", callback_data='nuke_password')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # update the message text
    query.edit_message_text(
        text="Please choose the password you want to change:",
        reply_markup=reply_markup
    )

    return change_password_select

# define a function to handle password selection
def change_password_select(update: Update, context: CallbackContext) -> int:
    logger.info("Command received: %s", update.message.text)
    global menus  # This line allows us to access and modify the global menus variable
    """
    This function handles the selection of password to change.
    It changes the appropriate password based on the admin's selection.
    """
    # fetch the query data
    query = update.callback_query
    query.answer()

    # change the appropriate password based on the admin's selection
    if query.data == 'admin_password':
        context.user_data['admin_password'] = query.data
    else:
        context.user_data['nuke_password'] = query.data

    # save the updated password in the JSON file
    with open('config.json', 'w') as f:
        json.dump(context.user_data, f)

    # inform the admin that password has been changed
    query.edit_message_text(text="Password has been changed.")

    # return to the config menu
    return config

# define a function to save the current menu JSON
def save_menu() -> None:
    global menus  # This line allows us to access and modify the global menus variable
    """
    This function handles the saving of the current menu JSON file.
    It writes the current state of the menus to the JSON file.
    """
    # write the current state of the menus to the JSON file
    with open('menus.json', 'w') as f:
        json.dump(menus, f)
# Now whenever we make a change to the menu, we can simply call save_menu(context) to update the JSON file.

# Command handler for '/admin'
def admin(update: Update, context: CallbackContext) -> int:
    logger.info("Command received: %s", update.message.text)
    """Asks the user for the password to access admin settings."""
    update.message.reply_text('Please enter the admin password:')
    return admin_password

def admin_password(update: Update, context: CallbackContext) -> int:
    logger.info("Command received: %s", update.message.text)
    """Checks if the entered password is correct. If correct, takes the user to the config menu."""
    
    # load the current config
    config_data = load_config_json()
    
    # Check if the entered password is correct
    if update.message.text == config_data['admin_password']:
        # If correct password, go to config menu
        return config(update, context)
    else:
        # If incorrect password, ask to try again
        update.message.reply_text('Incorrect password, please try again:')
        return admin_password

def load_config_json() -> dict:
    """Loads and returns the data from the config.json file."""
    if not os.path.exists('config.json'):
        # Default config dictionary
        default_config = {
            'key1': 'value1',
            'key2': 'value2'
            #... other default keys and values
        }

        # Create and write default config to 'config.json'
        with open('config.json', 'w') as json_file:
            json.dump(default_config, json_file)

    # Now, 'config.json' either existed already or was just created
    with open('config.json') as json_file:
        data = json.load(json_file)
        
    return data

def unknown_command(update, context):
    logger.info("Command received: %s", update.message.text)
    """
    This function is called when the user sends a command that the bot does not recognize.
    It sends a message back to the user stating that the command is not recognized and provides
    some guidance on what commands are available.
    """

    # Send a message to the user indicating that the command is not recognized
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm sorry, but I didn't understand that command. You can use /start to start a new conversation or /help for a list of available commands.")
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    logger.info("Command received: %s", update.message.text)
    """
    Cancel function to cancel the current operation
    and return the user to the previous state
    """
    user = update.message.from_user
    logger.info("User %s canceled the operation.", user.first_name)
    
    # Cleanup code to reset any variables or data related to the operation
    context.user_data.clear()

    # Inform user about the cancellation
    update.message.reply_text(
        "Operation canceled. Returning to previous menu...",
        reply_markup=ReplyKeyboardRemove(),
    )
    
    # Use the back function to return the user to the previous state
    return back(update, context)

def handle_button_press(update: Update, context: CallbackContext) -> None:
    query = update.callback_query

    # Acknowledge the button press to Telegram
    query.answer()

    # Log the received command for debugging purposes
    logger.info("Command received: %s", query.data)

    # Load the menus data from the JSON file
    menus = load_menus_json()

    # Get the callback data, which we'll assume is a button ID
    button_id = query.data  # Keep callback data as string

    # Get the current menu from user data (defaulting to "main_menu" if not found)
    current_menu = context.user_data.get('current_menu', 'main_menu')

    # Check if the pressed button corresponds to a submenu
    if button_id in menus[current_menu].get('sub_menus', {}):
        # Set the current menu to the pressed submenu
        context.user_data['current_menu'] = button_id

        # Generate new inline keyboard for the submenu
        keyboard = create_keyboard_from_menus(menus[button_id])

        # Edit the message with new keyboard
        query.edit_message_text(
            "You are now in a submenu. Please select an option:",
            reply_markup=keyboard
        )
    else:
	# Define a mapping from button IDs to functions
        button_functions = {
            "add_button": add_button,
            "add_button_type": add_button_type,
            "add_button_name": add_button_name,
            "add_button_image": add_button_image,
            "add_button_text": add_button_text,
            "create_button": create_button,
            "remove_button": remove_button,
            "confirm_button_removal": confirm_button_removal,
            "rename_button": rename_button,
            "rename_item_selection": rename_item_selection,
            "rename_item_name": rename_item_name,
            "move_button": move_button,
            "move_button_type": move_button_type,
            "move_button_selection": move_button_selection,
            "move_button_to_other_menu": move_button_to_other_menu,
            "move_button_to_other_menu_selected": move_button_to_other_menu_selected,
            "change_password": change_password,
            "change_password_select": change_password_select,
            "nuke": nuke,
            "confirm_nuke": confirm_nuke,
            "get_nuke_password": get_nuke_password,
            "final_warning": final_warning,
            "back": back,
            "exit_config": exit_config,
            "admin_password": admin_password,
        }


	# Get the function corresponding to the button ID
    function_to_call = button_functions.get(button_id)

    try:
        if function_to_call:
			# If a corresponding function was found, call it
            logger.info(f"Calling function: {button_id}")
            function_to_call(update, context)
        else:
			# If no corresponding function was found, reply with an error message
            update.effective_message.reply_text("An error occurred.")
            logger.error('No corresponding function was found for button ID "%s".', button_id)
    except Exception as e:
        logger.error(f"Exception occurred when calling function for button {button_id}: {e}")

def handle_message(update: Update, _: CallbackContext) -> None:
    """Handles an incoming message."""
    logger.info("Message received: %s", update.message.text)

    # Add the received message to received_messages list
    received_messages.append(update.message.text)

    # Handle the message and send a response
    response = process_message(update.message.text)
    update.message.reply_text(response)

def process_message(message: str) -> str:
    """
    Process the user's message and return a response.

    Args:
        message: The user's message.

    Returns:
        The bot's response as a string.
    """
    # Process the message based on the requirements
    if message == "hello":
        response = "Hi! How can I assist you today?"
    elif message == "how are you":
        response = "I'm an AI, so I don't have feelings, but thanks for asking!"
    elif message == "goodbye":
        response = "Goodbye! Have a great day!"
    else:
        response = "I'm sorry, I couldn't understand your message. Could you please rephrase?"

    return response

def main():
    """Start the bot."""
    # State definitions
    add_button, add_button_type, add_button_name, add_button_image, add_button_text, create_button, remove_button = range(7)
    confirm_button_removal, rename_button, rename_item_selection, rename_item_name, move_button, move_button_type, move_button_selection = range(7, 14)
    move_button_to_other_menu, move_button_to_other_menu_selected, change_password, change_password_select, nuke, confirm_nuke = range(14, 20)
    get_nuke_password, final_warning, back, exit_config, admin_password, cancel = range(20, 26)
    # Removed config, unknown_command, normal_message, echo, error states
    # Created a general CALLBACK state
    callback = 26

    # Create the Updater and pass it your bot's token.
    updater = Updater("TOKEN", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add ConversationHandler to dispatcher that will be used for handling updates
    conv_handler = ConversationHandler(
        # 'config' added to the entry points
        entry_points=[CommandHandler('start', start), CommandHandler('admin', admin), CommandHandler('nuke', nuke), CommandHandler('config', config)],
        states={
            # Defined a general CALLBACK state for handle_button_press
            callback: [CallbackQueryHandler(handle_button_press)],
            add_button: [MessageHandler(Filters.text & ~Filters.command, add_button)],
            add_button_type: [MessageHandler(Filters.text & ~Filters.command, add_button_type)],
            add_button_name: [MessageHandler(Filters.text & ~Filters.command, add_button_name)],
            add_button_image: [MessageHandler(Filters.photo, add_button_image)],
            add_button_text: [MessageHandler(Filters.text & ~Filters.command, add_button_text)],
            create_button: [MessageHandler(Filters.text & ~Filters.command, create_button)],
            remove_button: [CallbackQueryHandler(remove_button)],
            confirm_button_removal: [CallbackQueryHandler(confirm_button_removal)],
            rename_button: [CallbackQueryHandler(rename_button)],
            rename_item_selection: [CallbackQueryHandler(rename_item_selection)],
            rename_item_name: [CallbackQueryHandler(rename_item_name)],
            move_button: [CallbackQueryHandler(move_button)],
            move_button_type: [CallbackQueryHandler(move_button_type)],
            move_button_selection: [CallbackQueryHandler(move_button_selection)],
            move_button_to_other_menu: [CallbackQueryHandler(move_button_to_other_menu)],
            move_button_to_other_menu_selected: [CallbackQueryHandler(move_button_to_other_menu_selected)],
            change_password: [CallbackQueryHandler(change_password)],
            change_password_select: [CallbackQueryHandler(change_password_select)],
            nuke: [CallbackQueryHandler(nuke)],
            confirm_nuke: [CallbackQueryHandler(confirm_nuke)],
            get_nuke_password: [CallbackQueryHandler(get_nuke_password)],
            final_warning: [CallbackQueryHandler(final_warning)],
            back: [CallbackQueryHandler(back)],
            exit_config: [CallbackQueryHandler(exit_config)],
            admin_password: [MessageHandler(Filters.text & ~Filters.command, admin_password)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        per_user=True,
        per_chat=False,
    )

    dp.add_handler(conv_handler)

    # Log all errors
    dp.add_error_handler(error)

    logger.info("Bot script is running...")

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()

input("Press Enter to exit...")