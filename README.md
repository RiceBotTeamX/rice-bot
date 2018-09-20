# Eat Rice Bot

Eat Rice Bot is an interactive Facebook Messenger chatbot that provides information about dining here at Rice! It uses information from the Rice servery websites and NLP to answer nuanced questions about meals, eateries, and dietary restrictions.
Try it in browser or on mobile:
https://www.facebook.com/TXBOTT/

Some sample questions include:
* What rice dishes can I eat around McMurtry?
* Where can I get chicken?
* Colleges serving stuff without eggs?
* Vegetarian?
* gluten-free options at North or Seibel?
* What's on the menu at South and West?
* im vegan

## Implementation

There are three main parts: language processing, data collection, and internal logic to combine the two.

For input processing, we utilize [Wit.ai](https://wit.ai), a developer engine that uses natural language processing and machine learning to analyze user inputs and categorize words.

To generate our data on eateries, we pull data from the Rice servery website using the [Rice Dining](github.com/numinit/rice-dining) API and a Ruby library integrated with Python. Currently, we pull information once a day to ensure that users get up-to-date, accurate information.

We host Eat Rice Bot 24/7 on the Heroku platform. Eat Rice Bot may take a minute or two to boot up and respond to your first message, but all conversation following the initial communication should be significantly faster.
