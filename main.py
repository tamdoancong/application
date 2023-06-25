### 1.Import all neccesary libaries
from tkinter import*
from PyPDF2 import PdfReader,generic
from tkinter import filedialog
from builder1 import process_text
# from textstar import process_text
import networkx as nx
import re
import os
import openai
import socket

# Set global variable for number of sentences and keyphases to extract when internet is not available
n, k = 5, 5
# Set global variable for number of sentences and keyphases to extract when internet is available
n_sentences, ks = 36, 5

### 2. Write all necessary functions
## 2.1 This fuction creates a window with desired title, color, and size
def create_window(title, color, w, h):
    # Creat a window
    wd = Tk()
    # Write a title of the window
    wd.title("Summary Task for Long Document")
    # Set the minimum size of the window when window appears
    wd.minsize(width = w, height = h)
    # Set the background color for the window
    wd.configure(bg = color)
    return wd


## 2.2 This fuction creates a cavas
## parameters: window: what window the canvas will be put in, color, width, height,
## x: how many pixels from the left of the window,  y: how many pixels from the top of the window
def create_canvas(window, color, w, h, x, y):
    c = Canvas(window, bg = color, width = w, height = h)
    c.place(x = x, y = y)
    return c


## 2.3 This function creates a textbox with scroll bar
## parameters: width,height,x: how many pixels from the left of the window,  y: how many pixels from the top of the window
# wchar:number characters can be inserted for each row,hchar: number characters can be inserted for each column
def scroll_text(w, h, x, y, wchar, hchar):
    #Create a frame in the window
    frame= Frame(window, width = w, height = h)
    frame.place(x = x, y = y)
    # Create a canvas which has the same size with the frame and put it on the frame
    c2=Canvas(frame, bg = 'white', width = w,height = h)
    #Create a scroll bar with vertical moving and put it in the frame
    sbar = Scrollbar(frame, orient = VERTICAL)
    #Put the scroll bar on the right of the frame
    sbar.pack(side = RIGHT, fill = Y) #the scroll bar will not roll if use vbar.place()
    sbar.config(command = c2.yview)
    text_box = Text(c2, width = wchar, height = hchar, yscrollcommand = sbar.set, wrap = "word")
    text_box.pack(side = RIGHT, fill = Y)
    # input=text.get("1.0","end-1c")
    c2.config(width = w, height = h)
    # c2.config( yscrollcommand=vbar.set)
    c2.pack(side = LEFT, expand = True, fill = BOTH)
    return text_box


## 2.4 This function gets the text from a PDF file
def pdf2text(pdf_file):
    reader = PdfReader(pdf_file)
    n_pages = len(reader.pages)
    lp = extract_chapter(reader)
    text = extract_text(0, n_pages, reader)
    return lp, text


## 2.5 This function gets the text from a text file
def ftext2text(file):
    with open(file, 'r',encoding = "utf-8") as f:
        text = f.read()
    return text


## 2.6 This function uploads a file and returns the absolute path of a file
def upload_file():
    fname = filedialog.askopenfilename(filetypes=[('PDF Files', '*.pdf'),('Text Files', '*.txt')])
    return fname


## 2.7 This function gets the input text from the textbox
def get_textFbox(in_box,out_box):
    in_text = in_box.get("1.0", "end-1c")
    a, c, text = clean_text(in_text)
    t = a + text + c
    if is_internet() == True:
        summary = connect_API(t, 100)
    else:
        # If internet is not available, get the summary  from textstar
        summary, kw = get_n_sents(t, n, k)
    # Clean the output textbox
    out_box.delete("1.0", END)
    # Insert the summary to the output texbox, so user can see it
    out_box.insert(END, summary)


## 2.8 This function gets the input text from the file
def get_textFfile(out_box):
    # Clean the output textbox
    out_box.delete("1.0", END)
    # Get the absolute path of the uploading file
    fname=upload_file()
    # If the uploading file is pdf, convert to a string
    if is_pdf(fname):
        # convert pdf file to text
        lp, text = pdf2text(fname)
        out_text = ""
        # If the file has chapters' structure
        if lp != [] :
            for e in lp:
                # Call the function clean_text() to clean each chapter's text
                ab, c, chap = clean_text(e[1])
                # If internet is available
                if is_internet():
                    # Feeds each chapter's clean text to TextStar and get more  than 30 sentences
                    gM, gk = get_n_sents(chap, n_sentences, ks)
                    # Pass the summary result of TextStar to API
                    r_chap = connect_API(gM, 100)
                    sents = r_chap.split('.')
                    s_chap = ".".join(sents[:-1])
                    # Concatenate all chapters' summary form API
                    out_text += '\n\n' + e[0] + s_chap+'.'
                    print(e[0])
                #If internet is not available
                if not is_internet():
                    # Feeds each chapter's clean text to TextStar and get small number sentences
                    gM, gk = get_n_sents(chap, n, k)
                    # Concatenate all chapters' summary form TextStar
                    out_text += '\n' + e[0] + gM
        # This is the output summary
        summary = out_text
        # If a file does not have chapters' structure,
        # then call function paper2out(text,200) to process the in put text
        if lp == []:summary = paper2out(text,200)
    # If the uploading file is txt
    if is_txt(fname):
        #convert the file to a string
        text = ftext2text(fname)
        #Call function paper2out(text,200) to process the input string
        summary = paper2out(text,200)
    # Insert the summary to the output texbox, so user can see it
    out_box.insert(END, summary)


## 2.9 Function get n sentences from a long document by TextStar (a graph based algorithm)
## parameters: text:input text, n: the number semtences of an output summary, k: the number key words of an output
def get_n_sents(text, n, k):
    sents, kwds = process_text(text = text, ranker = nx.degree_centrality, sumsize = n,
                         kwsize=k, trim = 80)
    summary = ""
    # A sent is a list of tuples, each tuple is a pair of sentence id and sentence
    for sent in sents:
        # Extract only the sentence and convert tuple to string
        s = str(sent[1])
        summary += " "+ s
    return summary, kwds


## 2.10 Function clean   text
def clean_text(text):
    # re.sub(pattern, repl, string, count=0, flags=0)
    # replace strange symbols which are not in [a-zA-Z0-9.!?:,{}()@$\n ]
    # between character f and t by -
    # text = re.sub('f[^a-zA-Z0-9.!?:,{}%\[\]()@$/\n ]t', 'f-t', text)
    text = re.sub('f[^\w.!?:,{}%\[\]()@$/\n ]t', 'f-t', text)
    #remove all strange synbols which are not in [a-zA-Z0-9.!?:,{}()@$\n -]
    # text = re.sub('[^a-zA-Z0-9.!?:,{}()\[\]@$=/~\n -]', '', text)# this line code will result some missing words
    text = re.sub('[^\w.!?:,{}%()\[\]@$=/~\n -]', ' ', text)#this line code does not  result some missing words
    #remove References and all text appears after that
    # by splitting the text into 2 sparts with 'References' or 'Acknowledgements' cut point
    text = remove_references(text)
    # get abstract
    ab, text = get_Abstract(text)
    # remove Algorithm
    text = re.sub('\nAlgorithm.*?end(\n\d.*?end)+', ' ', text,flags=re.DOTALL)
    #remove Figure
    text = re.sub('\n[Ff]igure.*?\n', '\n', text, flags=re.DOTALL)
    #remove Table
    text = re.sub('\n[Tt]able.*?\.', ' ', text, flags=re.DOTALL)
    #remove ROUGE
    text = re.sub('ROUGE-[\dL]', ' ', text, flags=re.DOTALL)
    #remove F1@5
    text = re.sub('F1@[\d]*', ' ', text, flags=re.DOTALL)
    #remove text in between 2 round brackets
    text = re.sub('\([^)]*\)', ' ', text, flags=re.DOTALL)
    # remove text in between 2 square brackets
    text = re.sub('\[.*\]', ' ', text, )
    #remove https
    text = re.sub('https?:', ' ', text)
    # remove string after forward slash (/) which usually is converted from a table from pdf
    text = re.sub('\n?[/].+\n', ' ', text)
    # remove 1 or more white space before a comma
    text = re.sub('[\s]+,', ',', text)
    #remove a string of number which usually is converted from a table from pdf
    text = re.sub('\n([\d]+\.?([\d]+)?)*\n', ' ', text)
    # remove the lines with a lot numbers which often come from tables
    text = re.sub('\n?[\w\s-]*(\s*?[\d]+[.][\d]+-?)+', ' ', text)
    #remove line with equal sign
    # text = re.sub('\n?.*\s?=\s?.*\n', '', text)
    # text = re.sub('\n?\s?.+\s?::\s?.+\n', '', text, flags=re.DOTALL)
    # remove all newline
    text = re.sub('\n', ' ', text)
    c = get_Conclusion(text)
    return ab, c, text


##2.11  Function checks if internet is connected or not
def is_internet():
    try:
        # Try to connect to "www.google.com" at port 443
        s = socket.create_connection(("www.google.com", 443))
        if s != None: return True
    except OSError:
        pass
    return False


##2.12 This function connects to openAI API
def connect_API(n_sentences, m):
    file = "C:\\Users\\Tam Cong Doan\\Desktop\\PhD_doc\\qualify_exam\\GPT\\API\\fun_key.txt"
    openai.api_key = ftext2text(file)
    response = openai.Completion.create(
        model = "text-davinci-003",
        prompt = f"Summarize this text. Please provide complete sentences \n{ n_sentences}" ,
        temperature = 0,
        # maximum tokens of an output
        max_tokens = m,
        top_p = .6,
        frequency_penalty = 0.0,
        presence_penalty = 0.0
    )
    return response.choices[0].text


## 2.13 This function gets an Abstract and remove author's information
def get_Abstract(text):
    abs = re.findall('Abstract|ABSTRACT', text)
    intr = re.findall('Introduction|INTRODUCTION', text)
    if abs != []:
        # remove authors information
        text = text.split(str(abs[0]), 1)[1]
        # print(f" text after Abstract: {text}")
        abstract = text.split(str(intr[-1]), 1)[0]
        k = re.findall('KEYWORDS|keywords', abstract)
        if k != []:
            abstract = abstract.split(str(k[-1]),1)[0]
        for i in range(len(intr )):
            text = text.split(str(intr[-1]), 1)[1]
        return abstract, text
    else: return '', text


##2.14 This function removes references
def remove_references(text):
    r = re.findall('References|REFERENCES', text)
    a = re.findall('Acknowledgements|ACKNOWLEDGEMENTS', text)
    if r != []:
        if a != []: text = text.split(str(a[-1]),1)[0]
        else:text = text.split(r[-1],1)[0]
    return text


##2.15 This function gets the Conclusion
def get_Conclusion(text):
    c = re.findall('Conclusion|CONCLUSION', text)
    if c != []:
        conc = text.split(str(c[-1]), 1)[1]
        return conc
    else:return ""


##2.16 This function gets page number
## Parameters: n1 (id number), n2(generation number),r(PdfReader)
def get_page_num(n1, n2, r):
    return r._get_page_number_by_indirect(generic.IndirectObject(n1, n2, r))


## 2.17 This function extracts text from PDF file from page pm to page pm
## parameters: pm(start page), pn(end page), r(PdfReader)
def extract_text(pm, pn, r):
    text = ""
    for p in range(pm, pn):
        page = r.pages[p]
        text += page.extract_text()
    return text


## 2.18 This function gets outline from pdf
def extract_chapter(r):
    l = []
    # If the extracting outline  is empty
    outline = r._get_outline()
    if outline == []: return []
    #If the extracting outline  is not empty
    else:
        for o in outline:
            if type(o) != list: l.append((o.title,o.page))
        find = re.findall("Chapter|chapter", str(l))
        # print(find)
        if find == []: return []
        if find != []:
            lc = []
            li = []
            for i in l:
                if "Chapter" in i[0] or "CHAPTER" in i[0]:
                    lc.append((i[0],get_page_num(i[1].idnum,i[1].generation,r)))
                    li.append(l.index(i))
            # print(f"li: {li}")
            lc.append((l[li[-1]+1][0],get_page_num(l[li[-1]+1][1].idnum, l[li[-1]+1][1].generation, r)))
            lp = []
                # Each pair tuple in lc includes chapter number and text in this chapter
            for e in range(len(lc)-1):lp.append((lc[e][0],extract_text(lc[e][1], lc[e+1][1], r)))
            # print(len(lp))
            return lp


## 2.19 This function gets the text, cleans text, feeds the clean text to TextStar to get the summary without internet
# or  passes the TextStar's result to API with internet
def paper2out(text,m):
    a, c, text = clean_text(text)
    # If internet is connected,
    if is_internet() == True:
        # Get M sentences by textstar
        gM, gk = get_n_sents(text, n_sentences, ks)
        # add the abstract, conclusion and M sentences
        # pass result text to openAI API model and get the summary
        t = a + gM + c
        summary = connect_API(t,m)
    else:
        # If internet is not available, get the summary  from textstar
        summary, kw = get_n_sents(text, n, k)
    return summary


## 2.20 This function checks a file is PDF or not
def is_pdf(fname):
    if fname[-3:] == 'pdf': return True
    else: return False


## 2.21 This function checks a file is txt file or not
def is_txt(fname):
    if fname[-3:] == 'txt': return True
    else: return False


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
t2 = c3.create_text(360, 30, text = " Please put the input text to the box below then click the right button to get summary\n "
                                    "                           or click the left button to upload a file to get summary ",
                    font = ("Arial", 12, "bold"), anchor = CENTER )


###7.Create a canvas which contains the input text
# width = 780, height = 208,x=60, y=80,wchar=97, hchar=8
in_box = scroll_text(780, 188, 60, 338, 97, 8)
# print(f" The input text: {input}")


### 8. Create a button which a user clicks to upload a file
buttonL = Button(window,bg = "green", text= "Upload a File",font=('Arial', 12,"bold"),
                 width = 30, height = 2, anchor=CENTER, highlightthickness = 1,
                 command = lambda: get_textFfile(out_box))
# Place a button in a correct position
buttonL.place(x = 62, y = 480)


### 9. Create a button which a user clicks to get summary
buttonR = Button(window,bg = "green", text= "Get Summary",
                font = ('Arial', 12,"bold"), width = 30, height = 2, anchor = CENTER, highlightthickness = 1,
                command = lambda: get_textFbox(in_box,out_box))
buttonR.place(x = 550, y = 480)

window.mainloop()