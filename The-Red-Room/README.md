# A Suit of Desktop Assistant Apps

The Red Room is meant to be a suit of apps that can simulate the Red Room from Black Widow (2021). While there are no real Widows to chemically subjugate here, the theme from General Draykov's Computer was the main inspiration to create a set of apps that can be part of a desktop virtual companion. Please note that this is still a rule based system, and no generative AI has been used thus far... 

## Date, Time, and News Headlines

When the `app-main.py` is executed, it extends a time-based greeting using the local date and time, including parsing day suffixes for a more realistic experience. A current weather update follows using an API call to OpenWeather Map. Then a list of news headlines from around the world are displayed, with scroll functionality to navigate the list. Hitting enter will open the link to the news source in your default web browser.

## File Manager

To use the `file_manager.py` you need to define a PATH, and when the app is run, all files and folders from the given root are listed, with the ability to navigate the list, and to open the files using their default programs in windows.

## System Monitor Dashboard

`monitor.py` uses `CPUtil`, and `GPUtil` to retreive the system details from your local machine, including performance details that are updated in real time.
