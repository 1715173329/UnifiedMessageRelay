# Discord Bot Setup

## Register your bot and invite to your channel

[Instructions](https://discordpy.readthedocs.io/en/latest/discord.html)

Remember to give all of the permissions under text permissions.

## Install extension

```bash
pip install umr-discord-driver
```

## Config under Driver section

```yaml
Extensions:
  - umr_discord_driver
Driver:
  Discord:  # this name can be change, and the forward list should be using this name
    Base: Discord  # base driver name, don't change
    BotToken: asdsadsddfffsdffsdfsd  # the longer token on the developer console (the one says click to reveal)
    ClientToken: asdasdsadsfsafsdfsd # the shorter token on the developer console
```