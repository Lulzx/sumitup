import channel2index
TELEGRAPH_TOKEN = '0010fae64146e64e1f145470b866afc43e1f2221834eeffc8f3e4a901ac7'
CHANNEL_USERNAME = 'NoFapZ'
BOT_TOKEN = '1138512639:AAEJD18c-FX57Ixgm3hBpFx42tVVwbm0eiw'
response = channel2index.gen(
	CHANNEL_USERNAME, 
	bot_token = BOT_TOKEN, 
	telegraph_token = TELEGRAPH_TOKEN)
print(response)
