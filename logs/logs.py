import logging
from config.config_app import TEST_MODE_A

my_logger = logging.getLogger('my_logs')
my_logger.setLevel(logging.DEBUG)

handler_console = logging.StreamHandler()
handler_console.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(module)s | %(funcName)s] %(message)s')
handler_console.setFormatter(formatter)
my_logger.addHandler(handler_console)


print(my_logger)



# # handler_file = logging.FileHandler('C:\\Users\\Asus\\PycharmProjects\\module7\\logs\\my_blog.log', mode='a')
# # handler_file.setLevel(logging.DEBUG)
#
# handler_console = logging.StreamHandler()
# handler_console.setLevel(logging.DEBUG)
#
# formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(module)s | %(funcName)s] %(message)s')
#
# # handler_file.setFormatter(formatter)
# handler_console.setFormatter(formatter)
#
# # my_logger.addHandler(handler_file)
# my_logger.addHandler(handler_console)
