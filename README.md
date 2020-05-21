# Recurser Recommender

## Making friends at RC
Just joined (virtual) RC? Don't know who to talk to?

You could
- Browse the directory manually
- Join zulip channels and PM people who pique your interest with their wisdom
- Use a bot to pair you up for coffee or a pairing session
- Come up with random names and see if anyone has that name in Zulip

which are all fine and dandy.

But problems arise.
- What if you see someone interesting but you don't want to reach out to them immediately?
- What if you message everyone on the first 3 pages of the directory search results, but with every fresh search you gotta start from page 1?

This tool exists to solve those types of problems.

## What does this do?
1. Scrapes all the recursers
2. Presents you, one by one, with every recurser who matches your search criteria (which is to say, whose profile matches your regex).
    - It presents them in reverse chronological order based on when they last attended RC
    - It presents them to you by opening up your browser to that person's profile.
3. Asks you to indicate whether:
    - you've already spoken with them already
    - you want to talk to them later
    - you don't want to talk to them
4. Saves all of these indications


My workflow for this is that when I see someone I want to talk to, I reach out to them immediately, and then I go back to the script and I indicate "already messaged."

Swallow the frog, you know!

## How do I use it?
1. In your shell, export an environment variable called `RECURSE_AUTH_TOKEN` containing a [personal access token](https://www.recurse.com/settings/apps).
2. `pip install -r requirements.txt`
3. Run `python main.py` and follow the prompts
4. Make some new BFFs

## FUTURE WORK (which I will only do if someone asks me to do it)
- provide an option to open up a window to compose email to a person
