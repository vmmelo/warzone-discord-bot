# Call of Duty: Warzone Discord Bot
A discord bot written in python, that is mainly used to send latest Warzone updates to servers that invited the bot.

### How to add to my server?
You only need to invite the bot to your server using this [link](https://discord.com/oauth2/authorize?client_id=950949140848857129&permissions=309237836816&scope=bot)

When new updates are released, the bot will create a new text channel on the server (if doesn't exist yet) ```warzone-updates```. 

### Bot Commands
- !setlanguage pt|en|es|fr
   - to translate the next updates automatically



### Useful dev commands:
##### Manage dynamodb locally
docker-compose up -d

npm install -g dynamodb-admin

dynamodb-admin
