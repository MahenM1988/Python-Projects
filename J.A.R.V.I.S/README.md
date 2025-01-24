# Rule-Based Response Model

This is a rule-based response model written in Python, inspired by J.A.R.V.I.S. from the MCU. When the app loads, users can choose to interact via the terminal or activate voice commands. The app utilizes the built-in Microsoft TTS engine.

## Features

When the app starts, it extends a time-based greeting using the local date and time, including parsing day suffixes for a more realistic experience.

### Built-in Commands

- **Access Entertainment Library**: 
  - Loads contents from a folder specified in the `config.ini` file. Currently, it lists files and folders, and plays media files using their default applications on Microsoft Windows.

- **Current Date and Time**: 
  - Returns the current date and time.

- **Current Weather Update**: 
  - Provides the latest weather information using an API call to OpenWeather Map.

- **News Headlines**: 
  - Retrieves the top news headlines from NewsAPI.

- **Search**: 
  - The command followed by a query will open your default web browser and search the internet using that query.

- **Look Up**: 
  - The command followed by a lookup query will search Wikipedia using the provided keywords.

- **System Specifications**: 
  - Uses `Psutil` and `GPUtil` to retrieve details about the machine running the code and formats them into a conversational string for a more engaging output.

## Repository Structure

There are two main versions in this repository:

- **J.A.R.V.I.S..py**: Contains the entire code in one application.
- **main.py**: Components have also been split and linked via this file.
