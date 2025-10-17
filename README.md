# VRChat Group & Event Syncing

A open-source, read only vrchat bot that will grab events from the given groups and optionally mirror them to a custom website's api.

---

## Features

### Console Commands

- **`help`**
  Lists all the commands usable in the console

- **`exit`**/**`quit`**
  Safely exits the bot

- **`reload_env`**
  Reloads the GROUP_ID portion of the .env file, mainly for if you want to add more groups to your system without restarting the bot

- **`add_group <groupID>`**
  Adds the given group to the website api straight from the console

- **`update_group <groupID>`**
  Updates the given groups data on the website

- **`delete_group <groupID>`**
  Deletes the given group from the websites api

- **`refetch`**
  Re-fetches the events on the group ids in your .env

- **`add_event <groupID> <eventID> <eventTitle> <eventDescription> <StartTime> <EndTime> <Category> <accessType> <platforms>`**
  Manually add a group to the website through the console in-case the bot doesn't grab it when scanning.
  Example: `add_event grp_123 cal_123 title description 2025-10-17T02:00:00Z 2025-10-17T03:00:00Z category public standalonewindows,android`

- **`update_event <websiteEventID> <groupID> <eventID> <eventTitle> <eventDescription> <StartTime> <EndTime> <Category> <accessType> <platforms>`**
  Updates the given websiteEventID with the new data given
  Example: `update_event 123 grp_123 cal_123 title description 2025-10-17T02:00:00Z 2025-10-17T03:00:00Z category public standalonewindows,android`

- **`delete_event <websiteEventID>`**
  Deletes the event on the website attached to the given websiteEventID
  Example: `delete_event 123`

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
