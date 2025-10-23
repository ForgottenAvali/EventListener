# VRChat Group Event Listener

A open-source, read only vrchat bot that will grab events from the given groups and optionally mirror them to a custom website's api.

---

## Features

### Console Commands

- **`help`**
  - Lists all the commands usable in the console

- **`exit`**/**`quit`**
  - Safely exits the bot

- **`reload_env`**
  - Reloads the GROUP_ID portion of the .env file, mainly for if you want to add more groups to your system without restarting the bot

- **`add_group <groupID>`**
  - Adds the given group to the website api straight from the console

- **`update_group <groupID>`**
  - Updates the given groups data on the website

- **`delete_group <groupID>`**
  - Deletes the given group from the websites api

- **`refetch`**
  - Re-fetches the events on the group ids in your .env

- **`add_event <groupID> <eventID> <eventTitle> <eventDescription> <StartTime> <EndTime> <Category> <accessType> <platforms>`**
  - Manually add a group to the website through the console in-case the bot doesn't grab it when scanning.

- **`update_event <websiteEventID> <groupID> <eventID> <eventTitle> <eventDescription> <StartTime> <EndTime> <Category> <accessType> <platforms> <image_url> <tags>`**
  - Updates the given websiteEventID with the new data given

- **`delete_event <websiteEventID>`**
  - Deletes the event on the website attached to the given websiteEventID

---

## Installation

### Requirements

You will need;
- A vrchat account you (or someone else) have access to.
- Python 3.9 or higher
- Dependencies:
  - `dotenv`
  - `python-dotenv`
  - `vrchatapi`
  - `requests`

Install dependencies with:

`pip install -r requirements.txt`

---

## Environment Variables

.. code-block:: sh

        VRC_USER
        VRC_PASS
        CONTACT (Format being '{ProgramName}/{Version} (contact: {Email})')
        GROUP_ID (Separated by commas like 'grp_123, grp_456')
        ENDPOINT_BASE_EVENT
        ENDPOINT_EVENT
        ENDPOINT_BASE_GROUP
        ENDPOINT_GROUP
        API_KEY
