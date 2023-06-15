### 1.Import all neccesary libaries
from tkinter import*
from PyPDF2 import PdfReader
from tkinter import filedialog
from builder1 import process_text
import networkx as nx
import re
import os
import openai
import socket

# set global variable for number of sentences and keyphases to extract when internet is not available
n, k = 5, 5
# set global variable for number of sentences and keyphases to extract when internet is available
n_sentences, ks = 56, 5

### 2. Write all necessary functions
## 2.1 Fuction creates a window with desired title, color, and size
def create_window(title, color, w, h):
    # creat a window
    wd = Tk()
    # write a title of the window
    wd.title("Summary Task for Long Document")
    # set the minimum size of the window when window appears
    wd.minsize(width = w, height = h)
    # set the background color for the window
    wd.configure(bg = color)
    return wd


## 2.2 Fuction creates a cavas
## parameters: window: what window the canvas will be put in, color, width, height,
## x: how many pixels from the left of the window,  y: how many pixels from the top of the window
def create_canvas(window, color, w, h, x, y):
    c = Canvas(window, bg = color, width = w, height = h)
    c.place(x = x, y = y)
    return c


## 2.3 Function creates a textbox with scroll bar
## parameters: width,height,x: how many pixels from the left of the window,  y: how many pixels from the top of the window
# number characters can be inserted for each row,number characters can be inserted for each column
def scroll_text(w, h, x, y, wchar, hchar):
    #Create a frame in the window
    frame= Frame(window, width = w, height = h)
    frame.place(x = x, y = y)
    # Create a canvas which has the same size with the frame and put it on the frame
    c2=Canvas(frame, bg = 'white', width = w,height = h)
    #Create a scroll bar with vertical moving and put it in the frame
    sbar = Scrollbar(frame, orient = VERTICAL)
    #put the scroll bar on the right of the frame
    sbar.pack(side = RIGHT, fill = Y) #the scroll bar will not roll if use vbar.place()
    sbar.config(command = c2.yview)
    text_box = Text(c2, width = wchar, height = hchar, yscrollcommand = sbar.set, wrap = "word")
    text_box.pack(side = RIGHT, fill = Y)
    # input=text.get("1.0","end-1c")
    c2.config(width = w, height = h)
    # c2.config( yscrollcommand=vbar.set)
    c2.pack(side = LEFT, expand = True, fill = BOTH)
    return text_box


## 2.4 Function gets text from a PDF file
def pdf2text(pdf_file):
    reader = PdfReader(pdf_file)
    n_pages = len(reader.pages)
    # print(f" number of page: {number_of_pages}")
    text = ""
    for p in range(n_pages):
        page = reader.pages[p]
        text += page.extract_text()
    return text


## 2.5 Function gets text from a text file
def ftext2text(file):
    with open(file, 'r',encoding = "utf-8") as f:
        text = f.read()
    return text


## 2.6 Function uploads a file return the absolute path of a file
def upload_file():
    fname = filedialog.askopenfilename(filetypes=[('PDF Files', '*.pdf'),('Text Files', '*.txt')])
    return fname


## 2.7 Function gets input text from the textbox
def get_textFbox(in_box):
    t = in_box.get("1.0", "end-1c")
    print(f"This is input text: {t}")


## 2.8 Function gets input text from the file
def get_textFfile(out_box):
    # Clean the output textbox
    out_box.delete("1.0", END)
    # Get the absolute path of the uploading file
    fname=upload_file()
    # If the uploading file is pdf, convert to a string
    if fname[-3:] == 'pdf':
        # convert pdf file to text
        text = pdf2text(fname)
        # clean the text
        text = clean_text(text)
    # If the uploading file is txt, convert to a string
    else:text = ftext2text(fname)
    # If internet is connected,
    if is_internet() == True:
        # get M sentences by textstar
        gM, gk = get_n_sents(text, n_sentences, ks)
        # print(f" this is TextStar result: {gs}")
        # pass these M sentences to openAI API model and get the summary
        summary = connect_API(gM)
        # print(f" this is API result: {summary}")
    else:
        # If internet is not available, get the summary  from textstar
        summary, kw = get_n_sents(text, n, k)
        # Insert the summary to the output texbox, so user can see it
    out_box.insert(END, summary)


## 2.9 Function get n sentences from a long document by TextStar (a graph based algorithm)
## parameters: text:input text, n: the number semtences of an output summary, k: the number key words of an output
def get_n_sents(text, n, k):
    sents, kwds = process_text(text = text, ranker = nx.pagerank, sumsize = n,
                         kwsize=k, trim = 80)
    summary = ""
    for sent in sents:
        summary += sent[1]

    return summary, kwds


## 2.10 Function clean   text
def clean_text(text):
    # re.sub(pattern, repl, string, count=0, flags=0)
    text = re.sub('f[^a-zA-Z0-9.!?:,{}()@$\n ]t', 'f-t', text)
    text = re.sub('[^a-zA-Z0-9.!?:,{}()@$\n ]', '', text)
    return text


##2.11  Function checks if internet is connected or not
def is_internet():
    try:
        s = socket.create_connection(("www.google.com", 443))
        if s!= None: return True
    except OSError:
        pass
    return False

##2.12 Function connects to openAI API
def connect_API(n_sentences):
    file = "C:\\Users\\Tam Cong Doan\\key.txt"
    openai.api_key = ftext2text(file)
    # models = openai.Model.list()
    # print(models)
    response = openai.Completion.create(
        model = "text-davinci-003",
        prompt = "Summarize this text " + n_sentences ,
        temperature = .6,
        # maximum tokens of an output
        max_tokens = 200,
        top_p = 1.0,
        frequency_penalty = 0.0,
        presence_penalty = 0.0
    )
    return response.choices[0].text


### 3.Call the function to create a withow with the specific title, color, and size
window = create_window("Summary Task for Long Document",'green4', 900, 800)


### 4.Create a cavas with text " Summary of the iput paper:"
    # to let a user know that the text in the box below is the output summary
# Call a function to create a cavas with the specific color, size, and position in the window
c1 = create_canvas(window, "green", 793, 50, 60, 30)
# i1 = c2.create_image(0,0, anchor = N, image = img1)
# Insert a specific text to the canvas
t1=c1.create_text(360, 30, text = " Summary of the Input Text:", font = ("Arial", 12, "bold"), anchor = CENTER)


### 5.Create a textbox  which contains the output text
#width = 780, height = 208,x=60, y=80,wchar=97, hchar=8
out_box = scroll_text(780, 188, 60, 80, 97, 8)


###6. Create a cavas with text " Please type the input text or drag a file to the box below!"
### to let a user know to put the text or drag a file which user want to summary to the box below
# Call a function to create a canvas
c3 = create_canvas(window, "green", 793, 50, 60, 288)
# Insert text to the canvas
t2 = c3.create_text(360, 30, text = " Please put the input text to the box below or click the left button to upload a file ",
                    font = ("Arial", 12, "bold"), anchor = CENTER )


###7.Create a canvas which contains the input text
# width = 780, height = 208,x=60, y=80,wchar=97, hchar=8
in_box = scroll_text(780, 188, 60, 338, 97, 8)
print(f" The input text: {input}")


### 8. Create a button which a user clicks to upload a file
buttonL = Button(window,bg = "green", text= "Upload a File",font=('Arial', 12,"bold"),
                 width = 30, height = 2, anchor=CENTER, highlightthickness = 1,
                 command = lambda: get_textFfile(out_box))
# Place a button in a correct position
buttonL.place(x = 62, y = 480)


### 9. Create a button which a user clicks to get summary
buttonR = Button(window,bg = "green", text= "Get Summary",
                font = ('Arial', 12,"bold"), width = 30, height = 2, anchor = CENTER, highlightthickness = 1,
                command = lambda: get_textFbox(in_box))
buttonR.place(x = 550, y = 480)

window.mainloop()