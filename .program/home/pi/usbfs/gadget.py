import tkinter as tk
import subprocess


class Application(tk.Frame):
    fileMass = '/sys/kernel/config/usb_gadget/gadget/functions/mass_storage.usb0/lun.0/file'
    fileIMG ='/home/pi/usbfs/usbdisk.img'
    mntDIR = '/home/pi/mnt/'
    def hidkey(self, kcode):
        h = {
            38: 0x04, 56: 0x05, 54: 0x06, 40: 0x07, 26: 0x08,
            41: 0x09, 42: 0x0A, 43: 0x0B, 31: 0x0C, 44: 0x0D,
            45: 0x0E, 46: 0x0F, 58: 0x10, 57: 0x11, 32: 0x12,
            33: 0x13, 24: 0x14, 27: 0x15, 39: 0x16, 28: 0x17,
            30: 0x18, 55: 0x19, 25: 0x1A, 53: 0x1B, 29: 0x1C,
            52: 0x1D, 10: 0x1E, 11: 0x1F, 12: 0x20,	13: 0x21,
            14: 0x22, 15: 0x23,	16: 0x24, 17: 0x25,	18: 0x26,
            19: 0x27, 36: 0x28,	 9: 0x29, 22: 0x2A,	23: 0x2B,
            65: 0x2C, 20: 0x2D,	21: 0x2E, 34: 0x2F,	35: 0x30,
            51: 0x31, 47: 0x33,	48: 0x34, 49: 0x35,	59: 0x36,
            60: 0x37, 61: 0x38,	67: 0x3A, 68: 0x3B,	69: 0x3C,
            70: 0x3D, 71: 0x3E,	72: 0x3F, 73: 0x40,	74: 0x41,
            75: 0x42, 76: 0x43,	95: 0x44, 96: 0x45,	107: 0x46,
            127: 0x48, 118: 0x49, 110: 0x4A, 112: 0x4B,	119: 0x4C,
            115: 0x4D, 117: 0x4E, 113: 0x4F, 114: 0x50,	116: 0x51,
            111: 0x52, 77: 0x53, 106: 0x54,	63: 0x55, 82: 0x56,
            86: 0x57, 104: 0x58, 87: 0x59, 88: 0x5A, 89: 0x5B,
            83: 0x5C, 85: 0x5E,	79: 0x5F, 80: 0x60,	81: 0x61,
            90: 0x62, 91: 0x63,	135: 0x65, 84: 0x97, 37: 0xE0,
            50: 0xE1, 64: 0xE2,	105: 0xE4, 50: 0xE5, 108: 0xE6,
            134: 0xE7
            }
        return h.get(kcode, 0x00)
    
    def hidkeymod(self, kcode):
        m = {
             37: 0b00000001, #bit 0 is L CTRL
             50: 0b00000010, #bit 1 is L SHIFT
             64: 0b00000100, #bit 2 is L ALT
            204: 0b00000100, #bit 2 is L ALT with L_SHIFT
            #00: b'00001000', #bit 3 is L GUI
            105: 0b00010000, #bit 4 is R CTRL
            #50: b'00100000', #bit 5 is R SHIFT
            108: 0b01000000, #bit 6 is R ALT
            134: 0b10000000 #bit 7 is R GUI
            
            }
        return m.get(kcode, 0x00)
    
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.master.title(u'Keyboard and Mouse')
        self.master.geometry('500x400+300+200') # ширина=500, высота=400, x=300, y=200
        self.master.resizable(True, True)# размер окна может быть изменён по x и y
        self.master.protocol('WM_DELETE_WINDOW', self.window_destroy)
        self.keyboard = open("/dev/hidg0","wb",buffering=8)
        self.mouse = open("/dev/hidg1","wb",buffering=3)
        self.master.bind('<KeyPress>', self.keydown)
        self.master.bind('<KeyRelease>', self.keyup)
        self.master.bind('<Motion>', self.move)
        self.master.bind('<ButtonPress>', self.buttondown)
        self.master.bind('<ButtonRelease>', self.buttonup)
        self.out = bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00')
        self.outmod = 0b00000000
        self.outm = bytearray(b'\x00\x00\x00')
        self.outmx = 0
        self.outmy = 0
        self.create_widgets()

    def window_destroy(self):
        self.keyboard.close()
        self.mouse.close()
        self.master.destroy()
        
    def create_widgets(self):
        self.m = tk.Menu(self.master)
        self.mc = tk.Menu(self.master, tearoff=0, postcommand=self.showMenu)
        self.vMount = tk.IntVar()
        self.vM = tk.IntVar()
        self.mc.add_radiobutton(label="Mount to PI", command=self.mFS, variable=self.vMount, value=1)
        self.mc.add_radiobutton(label="Mount to WIN", command=self.mFS, variable=self.vMount,value=2)
        self.vCtrl = tk.IntVar()
        self.vAlt = tk.IntVar()
        self.vWin = tk.IntVar()

        self.m.add_checkbutton(label="Ctrl", command=self.hKeyD, variable=self.vCtrl)
        self.m.add_checkbutton(label="Alt", command=self.hKeyD, variable=self.vAlt)
        self.m.add_checkbutton(label="Win", command=self.hKeyD, variable=self.vWin)
       
        self.m.add_cascade(label="DISK", menu=self.mc)
        self.master.config(menu=self.m)        

    def hKeyD(self):
        self.out[0] = self.hKey()
        self.out[2] = 0
        self.keyboard.write(self.out)
        self.keyboard.flush()
        
    def keydown(self,event):
        self.outmod = self.outmod | self.hidkeymod(event.keycode)      
        self.out[0] = self.outmod | self.hKey()
        if self.hidkeymod(event.keycode) == 0:
            self.out[2] = self.hidkey(event.keycode)
        else:
            self.out[2] = 0
        self.keyboard.write(self.out)
        self.keyboard.flush()
    
    def keyup(self,event):
        if (self.outmod & 0b00000100) == 4: # L_ALT
            if (event.keycode != 64):
                self.keydown(event)
        elif (self.outmod & 0b01000000) == 64: # R_ALT
            if (event.keycode != 108):
                self.keydown(event)
        if self.outmod & self.hidkeymod(event.keycode):
            self.outmod = self.outmod ^ self.hidkeymod(event.keycode)
        self.out[0] = self.outmod | self.hKey()
        self.out[2] = 0
        self.keyboard.write(self.out)
        self.keyboard.flush()
    
    def move(self,event):
        xv = event.x - self.outmx
        yv = event.y - self.outmy
        self.outmx = event.x
        self.outmy = event.y
        xm = 255 + xv if xv < 0 else xv
        ym = 255 + yv if yv < 0 else yv
        self.outm[1] = xm if 0 <= xm <= 255 else 0
        self.outm[2] = ym if 0 <= ym <= 255 else 0
        #print(self.outm)
        self.mouse.write(self.outm)
        self.mouse.flush()
    
    def mkey(self, n):
        k = {
             #2: 0b00000100, #bit 2 is L_Button
             3: 0b00000010, #bit 1 is M_Button
             1: 0b00000001, #bit 0 is R_Button
            }
        return k.get(n, 0x00)        
    
    def buttondown(self, event):
        self.outm[0] = self.outm[0] | self.mkey(event.num)
        self.move(event)
         
    def buttonup(self, event):
        self.outm[0] = self.outm[0] ^ self.mkey(event.num)
        self.move(event)
    
    def showMenu(self):
        p = open(self.fileMass)
        result = p.read()
        p.close()
        if result =='':
            self.vMount.set(1)
            self.vM.set(1)
        else:
            self.vMount.set(2)
            self.vM.set(2)
            
    def mFS(self):
        if self.vMount.get() != self.vM.get():
            if self.vMount.get() == 1:
                result = subprocess.run(['echo  > '+self.fileMass], shell=True)
                result = subprocess.run(['sudo','mount','-o','loop,rw,uid=1000,gid=1000','-t','vfat', self.fileIMG, self.mntDIR])
                #, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                #print(result.stdout)
            elif self.vMount.get() == 2:
                result = subprocess.run(['sudo', 'umount', '-f', self.mntDIR])
                result = subprocess.run(['echo  '+self.fileIMG+' > '+self.fileMass], shell=True)
    
    def hKey(self):
        outHOT = 0b00000000
        outHOT = outHOT | 0b00000001 if self.vCtrl.get() == 1 else outHOT
        outHOT = outHOT | 0b00000100 if self.vAlt.get() == 1 else outHOT
        outHOT = outHOT | 0b00001000 if self.vWin.get() == 1 else outHOT
        return(outHOT)
 
if __name__ == '__main__':
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()