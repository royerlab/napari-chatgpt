from Bard import Chatbot

token = 'Wgi6lxj2R-NE9yMgkG3r_sXrsV9-JVO16thWD-2tTGjnAoxCvJxj0vYieQFdBinHGntcQA.'
# environ.get("BARD_TOKEN")

chatbot = Chatbot(token)

print(chatbot.ask("Please summarise our conversion"))
