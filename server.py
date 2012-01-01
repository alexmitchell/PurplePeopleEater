import main

server = main.ServerLoop()

try: server.play()
except KeyboardInterrupt: pass
