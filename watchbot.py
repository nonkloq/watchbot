from bothandle import Browser
import re
# from beepy import beep
from bs4 import BeautifulSoup as BSP
from time import sleep, time
from assessment_data import answers

VERSION = "BETA 4.1.0"
class WatchBot:
    """WATCH BOT BETA-4x"""
    def __init__(self,name,phnum):
        self.uname = name
        self.phnum = phnum
        self.web = None
    
    def run(self):
        """ Cycle and Watch lessons """
        back_url = [self.web.get_current_url()]
        while back_url:
            cl = self.cycle(back_url)
            if len(back_url)==1:cl= self.cycle(back_url)
            if not back_url: break
            print()
            self.start_watch(cl)

    def cycle(self,back_url):
        """ Navigate Courses """
        cl = None
        print("<-")
        self.web.go_to(back_url.pop())
        while True: 
            sleep(2)
            nlid = nextlessonid(self.web.get_page_source())
            if not nlid: break
            cl = nlid
            print(nlid,end=" -> ")
            back_url.append(self.web.get_current_url())
            self.web.click(nlid)
        print()
        return cl
        

    def start_watch(self,cl):
        """ Watch Lessons """
        names = get_names(self.web)
        sleep(.3)
        while names:
            if next_available(self.web,names[0]):
                names.pop(0)
                self.web.click("Next")
                sleep(1)
            elif "Assessment" in names[0]:
                #beep(sound=3)
                handle_assessment(self.web,self.uname,cl,answers.get(cl,'NAN'))
                break
            else:
                print('Watching: '+names[0],end="\n")
                s = time()
                sleep_until_video_ends(self.web,names[0])
                e = time()
                print(f"==> Completed in {(e-s)/60:.2f}mins\n")
        print(f"\nSuccessfully Completed: {cl}\n")

    def openw(self,):
        """Open Chrome Window"""
        self.web = Browser()
        self.web.workbot(self.uname, self.phnum)
        self.web.go_to("https://naanmudhalvan.azurewebsites.net/")
        sleep(.3)

    def signin(self):
        """ Automated Signin """
        # Signing in
        self.web.click("SIGN IN",tag="button")
        sleep(.3)

        #  Mobile and Verification
        self.web.click(classname="PhoneInputCountrySelect",tag="select")
        sleep(.3)
        self.web.click("India",tag="option")
        sleep(.4)
        self.web.type(self.phnum,into="Enter your mobile number")
        sleep(.4)
        self.web.click(classname="primary-action",tag="div")

        otp = usr_input("Enter OTP:", 6)

        self.web.type(otp,"Enter 6 digit code",tag= "input")
        self.web.click(classname="primary-action",tag="div")

# ------------------------------------------ UTILS------------------------------------------------------------

def script_exec_4x(obj):
    obj.execute_script("""
    document.querySelectorAll('video').forEach((videoElement) => {
        videoElement.playbackRate = 4;
    });""")

def make_soup(obj):
    return BSP(obj.get_page_source(),"html.parser")

def usr_input(msg,constrain):
    inp = ""
    while len(inp) != constrain:
        inp = input(msg)
    return inp
# ---------------------------------------- For Course Navigation ---------------------------------------------
def nextlessonid(html):
    pattern = "[0-9]{1,3}% completed"
    reng = list(re.finditer(pattern, html))
    if not reng: return
    out = []
    for r in reng: 
        i = r.start()
        s,e=i,i-2
        while html[s] != "%": s+=1
        if int(html[i:s])>=100: continue
        while  s>1 and html[s-1] != '"': s-=1
        return html[s:e]
    return ""

# --------------------------------------------------- For Lessons Navigation ----------------------------------------------
def tosec(stamp):
    a,b = stamp.split(':')
    return (int(a)*60+int(b))/4

def get_names(obj):
    illegal = ["This is a modal window.","","Previous","Next"]
    soup = make_soup(obj)
    out = [x.text for x in soup.find_all('p') if not x.text in illegal]
    return out


def next_available(obj,name):
    soup = make_soup(obj)

    curr = None
    for x in soup.find_all('p'):
        if x.text == name:
            curr = x 
            break
            
    if not curr:
        dd = soup.find(attrs={"class":"vjs-duration-display"})
        exep = True
        if dd:
            m =  tosec(dd.text[-5:])
            n =  tosec(soup.find(attrs={"class":"vjs-current-time"}).text[-9:-4])
            exep = 0<=(m-n)<=1
        
        return not ("disabled" in soup.find(attrs={"name":"Next"}).attrs) and exep
    
    i = curr.parent.find('i')
    return (i and i.attrs['data-icon-name'] == "Accept")

def sleep_until_video_ends(obj,name):
    # Video time
    soup = make_soup(obj)
    dd = soup.find(attrs={"class":"vjs-duration-display"})
    if not dd: 
        print("==> Not Video file")
        return
    script_exec_4x(obj)
    tot = tosec(dd.text[-5:])
    m = tot 
    print(f"==> Est. time {m/60:.2f}mins")
    
    
    dif = 5
    while True:
        sleep(dif)
        m-=dif
        if m<=0:
            soup = make_soup(obj)
            n =  tosec(soup.find(attrs={"class":"vjs-current-time"}).text[-9:-4])
            #sleep delta
            m = tot-n
        else: script_exec_4x(obj)
        if next_available(obj,name): break 
    

def handle_assessment(obj,name,cl,link):
    print(f"\n\nHey {name}, \n\tPlease Enter \'completed\' after manually completing the assessment and claiming the certificate!(i.e. 100% completed)")
    print(f"\t{cl} Assessment Answers: {link}")
    print("\tNew Tabs opened:- ",end=" ")
    obj.new_tab(url="https://www.google.com")
    print("Tab1-Google",end="")
    if len(link)>3: 
        obj.new_tab(url=link)
        print(", Tab2-Youtube")
    print("You can close the new tabs.")
    usr_input(">", 9)

def main():
    print(f"""
    \t~~~~ ~~~~ ~~~~ WatchBOT 4x ~~~~ ~~~~ ~~~~\n
Author: Satz
Version: {VERSION}


----> Server side problems will lead to crash.
----> Don't close the chrome window and Don't change the current page.
----> Follow bot instructions.
----> Stable internet connection is recommended (Set video quality lower for better experience).
----> Terminate the bot by pressing 'CTR+C'. 

Note: 
    Bot can not able to autoplay the first video of the lesson, so the user is requested to play it manually.
    You should manually complete the assessment test when you get notified by the bot.

\n
""")

    name = input("Enter Name(For notifications):")
    phnum = usr_input("Phone Number:", 10)
    print("\n\n")
    bot = WatchBot(name,phnum)
    
    bot.openw()
    print("Check your OTP before you press enter!")
    bot.signin()
    print("\n")

    s = time()
    tot = bot.run()
    e = time()
    if (e-s<10): print("Unusual Runtime")
    print(f"\nTotal exc. Time {(e-s)/60:.2f}mins")


if __name__ == "__main__":
    main()
