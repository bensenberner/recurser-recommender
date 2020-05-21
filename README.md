# Recurser Recommender
## Disclaimer
I made this for myself and I put it online so that I could link to it in a check-in. I'll clean it up later if you want to use it as long as you ask nicely
## Your current options
Just joined (virtual) RC? Don't know who to talk to?

You could
- Browse the directory manually
- Join zulip channels and PM people who pique your interest with their wisdom
- Use a bot to pair you up for coffee or a pairing session
- Come up with random names and see if anyone has that name in Zulip

which are all fine and dandy.

But if you're looking for a little more fine-tuning on the directory search method, then you are in luck my friend.

## What this does this do?
Zeroth of all, I want to point out that this all runs locally, so I don't see any data that you enter into the CLI

First, you scrape all the recursers.

Then, you run the main script on the command line. It will present you, one by one, with every recurser who matches your search criteria (which is to say, whose profile matches your regex).
It presents them in reverse chronological order based on when they last attended RC. It presents them to you by opening up your browser to each person's profile.

Then, you feed in a 'rating' to the script indicating whether 
- you've already spoken with them already
- you want to talk to them later
- you don't want to talk to them

My workflow for this is that when I see someone I want to talk to, I reach out to them immediately, and then I go back to the script and I indicate "already messaged."

Swallow the frog, you know!

When you're done, you indicate that you want to quit and the script **saves your ratings to a database** (aka a pickle) so that you can pick up where you left off when you run it again.

## How do I use it?
1. In your shell, export an environment variable called `RECURSE_AUTH_TOKEN` containing a [personal access token](https://www.recurse.com/settings/apps).
2. `pip install -r requirements.txt`
3. Run `python main.py` and follow the prompts
4. Make some new BFFs

## FUTURE WORK (which I will only do if someone asks me to do it)
- provide an option to open up a window to compose email to a person
