import queue

#
# Komendy wysłane do robota:
# moveForward, moveBackward, moveLeft, moveRight, moveRight,
# speed1, speed2, speed3, speed4, 
# stop
#

class RobotControl():
    def __init__(self, com_que):
        self.command_queue = com_que
        self.last_command = None
        self.last_message = None
        self.block = False
        self.move_forward = False
        self.forward_stopped = False

        self.move_backward = False
        self.backward_stopped = False

        self.move_left = False
        self.left_stopped = False

        self.move_right = False
        self.right_stopped = False
        self.key_list = ['1_down', '2_down', '3_down', '4_down', 'W_down', 'A_down', 'S_down','D_down', 'W_up', 'A_up', 'S_up', 'D_up'] # lista przycisków uwzględnianych w kolejce


    def encoder(self):
        if self.block: # Gdy podczas jazdy do przodu lub do tyłu chcemy skręcić, ze względu na silniki najpierw zatrzymuejmy robota i dopiero potem rusza
            self.block = False
            message = self.last_message
            self.last_message = None
            return message

        if not self.command_queue.empty():
            command = self.command_queue.get()
            while command not in self.key_list: # Pomijanie nieużywanych przycisków 
                if not self.command_queue.empty():
                    command = self.command_queue.get()
                else:
                    if self.last_command != None: # Jesli kolejka jest pusta aktualną komendą będzie poprzednia komenda
                        command = self.last_command
                    else: # Jesli kolejka jest pusta i nie ma poprzedniej komendy, wysyłam do robota komende stop
                        return 'stop'
                    
        elif self.last_command != None: # Jesli kolejka jest pusta aktualną komendą będzie poprzednia komenda
            command = self.last_command
        else:
            return 'stop'
        
        if command == 'W_down' and not self.move_backward:
            self.move_forward = True
            self.last_command = command
            if (self.move_left or self.move_right) and not self.forward_stopped:
                self.last_message = 'moveForward'
                self.block = True
                self.forward_stopped = True
                return 'stop'
            else:
                return 'moveForward'
        
        elif command == 'S_down' and not self.move_forward:
            self.move_backward = True
            self.last_command = command
            if (self.move_left or self.move_right) and not self.forward_stopped:
                self.last_message = 'moveBackward'
                self.block = True
                self.forward_stopped = True
                return 'stop'
            else:
                return 'moveBackward'
        
        elif command == 'A_down' and not self.move_right:
            self.move_left = True
            self.last_command = command
            if (self.move_backward or self.move_forward) and not self.left_stopped:
                self.last_message = 'moveLeft'
                self.block = True
                self.left_stopped = True
                return 'stop'
            else:
                return 'moveLeft'
        
        elif command == 'D_down' and not self.move_left:
            self.move_right = True
            self.last_command = command
            if (self.move_backward or self.move_forward) and not self.right_stopped:
                self.last_message = 'moveRight'
                self.block = True
                self.right_stopped = True
                return 'stop'
            else:
                return 'moveRight'

        elif command == 'W_up' and self.move_forward:
            self.move_forward = False
            
            if self.move_right:
                if self.last_command == 'D_down':
                    return 'moveRight'
                else:
                    self.last_command = 'D_down'
                    return 'stop'
            elif self.move_left:
                if self.last_command == 'A_down':
                    return 'moveRight'
                else:
                    self.last_command = 'A_down'
                    return 'stop'
            else:
                self.last_command = None

            return 'stop'
        
        elif command == 'S_up' and self.move_backward:
            self.move_backward = False
            
            if self.move_right:
                if self.last_command == 'D_down':
                    return 'moveRight'
                else:
                    self.last_command = 'D_down'
                    return 'stop'
            elif self.move_left:
                if self.last_command == 'A_down':
                    return 'moveRight'
                else:
                    self.last_command = 'A_down'
                    return 'stop'
            else:
                self.last_command = None

            return 'stop'
        
        elif command == 'A_up' and self.move_left:
            self.move_left = False
            self.left_stopped = False
            
            if self.move_backward:
                if self.last_command == 'S_down':
                    return 'moveBackward'
                else:
                    self.last_command = 'S_down'
                    return 'stop'
            elif self.move_forward:
                if self.last_command == 'W_down':
                    return 'moveForward'
                else:
                    self.last_command = 'W_down'
                    return 'stop'
            else:
                self.last_command = None
                
            return 'stop'
        
        elif command == 'D_up' and self.move_right:
            self.move_right = False
            self.right_stopped = False

            if self.move_backward:
                if self.last_command == 'S_down':
                    return 'moveBackward'
                else:
                    self.last_command = 'S_down'
                    return 'stop'
            elif self.move_forward:
                if self.last_command == 'W_down':
                    return 'moveForward'
                else:
                    self.last_command = 'W_down'
                    return 'stop'
            else:
                self.last_command = None
                
            return 'stop'
        
        elif command == '1_down':
            return 'speed1'
        
        elif command == '2_down':
            return 'speed2'
        
        elif command == '3_down':
            return 'speed3'
        
        elif command == '4_down':
            return 'speed4'
        
        else: # Przy sprzecznych komendach stan robota zeruje sie i wysyła komende 'stop'
            self.last_command = None
            self.move_forward = False
            self.move_backward = False
            self.move_left = False
            self.move_right = False
            self.wait = True
            return 'stop'

    def send_command(self):
        message = self.encoder()
        return message

