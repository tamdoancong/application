### 1.Import all neccesary libaries
from tkinter import*
from PyPDF2 import PdfReader,generic
from tkinter import filedialog
from builder1 import process_text
from textblob import TextBlob
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
    wd.title("Fun Chat")
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
    print(f" number of pages: {n_pages}")
    lp = extract_chapter_pdf(reader)
    text = extract_text(0, n_pages, reader)
    # print(f"Text extract from pdf: {text}")
    if lp == []: lp = get_chapters_text(text)
    return n_pages, lp, text


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


def enter(event):
    u_text = out_box.get("1.0", "end-1c")
    s_text = chat_API(u_text)
    out_box.insert(END, "\nSystem: ",'tag2')
    out_box.insert(END,s_text)
    out_box.insert(END, "\nUser: ",'tag1')


## 2.8 This function gets the input text from the file
def get_textFfile(out_box):
    # Clean the output textbox
    # out_box.delete("1.0", END)
    # Get the absolute path of the uploading file
    fname=upload_file()
    # If the uploading file is pdf, convert to a string
    if is_pdf(fname):
        # convert pdf file to text
        n_pages, lp, text = pdf2text(fname)
        out_text = ""
        # If the file can be extracted by list of chapters(sections) and number of pages great than 100
        if n_pages > 100 and lp != [] :
            # For each chapter
            for e in lp:
                # Call the function clean_text() to clean each chapter's text
                ab, c, chap = clean_text(e[1])
                # print(f" clean chapter: {chap}")
                # # If internet is available
                if is_internet():
                    # Feeds each chapter's clean text to TextStar and get more  than 30 sentences
                    gM, gk = get_n_sents(chap, n_sentences, ks)
                    # Pass the summary result of TextStar to API
                    # and set the output's length (100 tokens)
                    r_chap = connect_API(gM, 100)
                    #
                    sents = r_chap.split('.')
                    s_chap = ".".join(sents[:-1])
                    # Concatenate all chapters' summary from API
                    out_text += '\n\n' + e[0] + s_chap+'.'
                    # print(e[0])
                #If internet is not available
                # if not is_internet():
                else:
                    # Feeds each chapter's clean text to TextStar and get small number sentences
                    gM, gk = get_n_sents(chap, n, k)
                    # print(gM)
                    # Concatenate all chapters' summary form TextStar
                    out_text += '\n' + e[0] + gM

        # This is the output summary
            summary = out_text
        # If a file does not have chapters' structure,
        # then call function paper2out(text,200) to process the in put text
        else:summary = paper2out(text,200)
    # If the uploading file is txt
    if is_txt(fname):
        #convert the file to a string
        text = ftext2text(fname)
        #Call function paper2out(text,200) to process the input string
        summary = paper2out(text,200)
    # Insert the summary to the output texbox, so user can see it
    out_box.insert(END, "\nSystem: ",'tag2')
    out_box.insert(END, "This is summary of the uploaded documment:"+summary)
    out_box.insert(END, "\nUser: ", 'tag1')


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
    # print(f" Abstract():\n {ab}")
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
    text = re.sub('\d?http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+','',text)
    # remove string after forward slash (/) which usually is converted from a table from pdf
    text = re.sub('\n?[/].+\n', ' ', text)
    # remove 1 or more white space before a comma
    text = re.sub('[\s]+,', ',', text)
    #remove a string of number which usually is converted from a table from pdf
    text = re.sub('\n^\d+\.?\d*$\n', '', text)
    # remove the lines with a lot numbers which often come from tables
    text = re.sub('\n?[\w\s-]*(\s*?[\d]+[.][\d]+-?)+', ' ', text)
    # print(f" text in clean_text() before extract conclusion:\n {text}")
    #remove line with equal sign
    # text = re.sub('\n?.*\s?=\s?.*\n', '', text)
    # text = re.sub('\n?\s?.+\s?::\s?.+\n', '', text, flags=re.DOTALL)
    c = get_Conclusion(text)
    # print(f"\nConclusion:\n {c}")
    # remove all newline
    text = re.sub('\n', ' ', text)
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
        # this model has total 4,097 tokens (input and output)
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


def chat_API(uq):
    file = "C:\\Users\\Tam Cong Doan\\Desktop\\PhD_doc\\qualify_exam\\GPT\\API\\fun_key.txt"
    openai.api_key = ftext2text(file)
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"{uq}"}
        ]
    )

    print(completion.choices[0].message['content'])
    return completion.choices[0].message['content']
## 2.13 This function gets an Abstract and remove author's information
## Parameter: text
## Return: an Abstract and text without an Abstract if an Abstract exists
# #       or [] and text
def get_Abstract(text):
    # Find the word 'Abstract'or ABSTRACT'
    # The first letter must be uppercase.
    # If use flags=re.IGNORECASE here the result will return 'abstract'
    abs = re.findall('\nAbstract|ABSTRACT', text)
    # print(f" Result re.findall(Abstract) :\n {abs}")
    # Find the word 'Introduction' or 'INTRODUCTION'
    intr = re.findall('Introduction|INTRODUCTION', text)
    # print(f"intr:n\{intr} ")
    # If the text contains the word 'Abstract',no matter lowercase or uppercase
    if abs != []:
        # Split the text into 2 parts by the key word 'Abstract'or 'ABSTRACT',
        #The word 'abstract' can be somewhere in body text or reference, so it causes a wrong spliting position
        # Get the second part for text which does not have author's information
        text_no_author = text.split(str(abs[0]), 1)[1]
        # Split the text into 2 parts by the key word 'Introduction' or 'INTRODUCTION',
        # Get the first part which is abstract
        # if len(intr) > 0:
        abstract1 = text_no_author.split(str(intr[0]), 1)[0]
        # print(f"abstract : \n {abstract1}")
        # Repeat len(intr) times to split the text and get the text after the word "Introduction".
        for i in range(len(intr)):text_no_author = text_no_author.split(str(intr[-1]), 1)[1]
        # Find the word 'KEYWORDS' or 'keywords'
        k = re.findall('KEYWORDS|Keywords', abstract1)
        #If the abstract1 contains the word 'KEYWORDS' or 'keywords'
        if k != []:
            #Split the text into 2 parts by the key word 'KEYWORDS' or 'Keywords',
            # Get the first part for abstract1 which does not have key words part
            abstract2 = abstract1.split(str(k[-1]),1)[0]
            return abstract2, text_no_author
        # If the abstract1 does not contains the word 'KEYWORDS' or 'Keywords'
        else: return abstract1, text_no_author
    else: return '', text


## 2.14 This function removes references
## Parameters: text
## Return: text without References
def remove_references(text):
    # Find the word 'References or REFERENCES'
    r = re.findall('References|REFERENCES', text)
    # Find the word 'Acknowledgements' or 'ACKNOWLEDGEMENTS'
    a = re.findall('Acknowledgements|ACKNOWLEDGEMENTS', text)
    # If the word 'References or REFERENCES' exists
    if r != []:
        # If the word 'Acknowledgements' or 'ACKNOWLEDGEMENTS' exists
        if a != []: text = text.split(str(a[-1]),1)[0]
        # If the word 'Acknowledgements' or 'ACKNOWLEDGEMENTS' does not exists
        else:text = text.split(r[-1],1)[0]
    return text


##2.15 This function gets the Conclusion
## Parameters: text
## Return: a Conclusion or ""
def get_Conclusion(text):
    # Find the word 'Conclusion' or 'CONCLUSION'
    c = re.findall('Conclusion|CONCLUSION', text)
    # print(f"\nc:{c}")
    # If the word 'Conclusion' or 'CONCLUSION'  exists
    if c != []:
        # Split the text into 2 parts by key word 'Conclusion' or 'CONCLUSION'
        # Get the second part
        conc = text.split(str(c[-1]), 1)[1]
        # print(f" conc after split by the word conclusion: {conc}")
        return conc
    else:return ""


## 2.16 This function gets page number
## Parameters: n1 (id number), n2(generation number),r(PdfReader)
## Return: a page number
def get_page_num(n1, n2, r):
    return r._get_page_number_by_indirect(generic.IndirectObject(n1, n2, r))


## 2.17 This function extracts text from PDF file from page pm to page pn
## Parameters: pm(the page which begin to extract text), pn( stop to extract text after this page), r(PdfReader)
## Return: text which get from PdfReader
def extract_text(pm, pn, r):
    # Define a variable text with an empty string
    text = ""
    # Loop from  page pm to  page pn
    for p in range(pm, pn):
        # Call the function pages from PdfReader class
        page = r.pages[p]
        # Concatenate extracting text from each page to a variable text
        text += page.extract_text()
    return text


## 2.18 This function gets outline from pdf
## Parameter: r(PdfReader)
## Return: a list of pairs of chapters(sections) and correlating text
def extract_chapter_pdf(r):
    l = []
    #  get outline  from PDF format
    outline = r._get_outline()
    # print(f" outline from pdf: {outline}")
    # print(f"data type of outline: {type(outline)}")
    # If the extracting outline  is empty, then reurn an empty list
    if outline == []: return []
    #If the extracting outline  is not empty
    else:
        # Loop through all elements in outline
        for o in outline:
            # If type of the element is not list, then put that element's title and page  to the list l
            if type(o) != list: l.append((o.title,o.page))
        print(f" o in outline and o not a list : {l}")
        # Check if the word "Chapter"  is in the list l or not, no matter lower case or upper case
        find = re.findall("Chapter|CHAPTER", str(l))
        # print(find)
        # If the word "Chapter" is in the list l
        if find != []:
            lc = []
            li = []
            # Loop through all elements in the list l
            for i in l:
                # If the word "Chapter"  is in an element i,
                if "Chapter" in i[0] or "CHAPTER" in i[0]:
                    # Append a pair (chapter,a correlating page number) into the list lc
                    lc.append((i[0],get_page_num(i[1].idnum,i[1].generation,r)))
                    # print(f"get_page_num(i[1].idnum,i[1].generation,r):{get_page_num(i[1].idnum,i[1].generation,r)}")
                    # Put the index of element i to the list li
                    li.append(l.index(i))

            # print(f"li: {li}")
            # Append the element which is located next to the last chapter in a list l and its page number to the list lc
            lc.append((l[li[-1]+1][0],get_page_num(l[li[-1]+1][1].idnum, l[li[-1]+1][1].generation, r)))
            lp = []
            # Each pair tuple in lc includes chapter number and text in this chapter
            # Put  tuples of chapter title and correlating text to the list lp
            for e in range(len(lc)-1):lp.append((lc[e][0],extract_text(lc[e][1], lc[e+1][1], r)))
            # print(f"lp: {lp}")
            return lp
        # If the word "Chapter" is not in the list l
        else:
            # Check if the word "Conclusion" is in the list l or not
            find1 = re.findall("Conclusion|CONCLUSION", str(l))
            # If the word "Conclusion" is in the list l
            if find1 != []:
                l_sec = []
                # Loop through the list l
                for i in l:
                    # If an element contains a word "Conclusion" or "CONCLUSION"
                    if "Conclusion" in i[0] or "CONCLUSION" in i[0]:
                        # Get the index of the list l where stores that element
                        con_i = l.index(i)
                        # print(f" con_i: {con_i}")
                # Create a list l_s such that l_s contains elements in l
                # from index 0 to the index next to the index of element which has the word "Conclusion"
                l_s = l[:con_i+2]
                # Loop through l_s
                for s in range(len(l_s)):
                    # Append a pair (section,a page number) into the list l_sec
                    l_sec.append((l_s[s][0], get_page_num(l_s[s][1].idnum, l_s[s][1].generation, r )))
                # print(f"l_sec: {l_sec}")
                l_sec_text= []
                # Put  tuples of section title and correlating text to the list l_sec_text
                for s1 in range(len(l_sec)-1): l_sec_text.append((l_sec[s1][0],extract_text(l_sec[s1][1], l_sec[s1+1][1], r)))
                print(f"l_sec_text: {l_sec_text}")
                print(f"len of l_sec_text: {len(l_sec_text)}")
                return l_sec_text
            else:
                find2 = re.findall("Bibliography|BIBLIOGRAPHY", str(l))
                if find2 != []:
                    l2 = []
                    # Loop through the list l
                    for i in l:
                        # If an element contains a word "Bibliography|BIBLIOGRAPHY"
                        if "Bibliography" in i[0] or "BIBLIOGRAPHY" in i[0]:
                            # Get the index of the list l where stores that element
                            bib_i = l.index(i)
                            # print(f" con_i: {con_i}")
                    # Create a list l_s such that l_s contains elements in l
                    # from index 0 to the index next to the index of element which has the word "Conclusion"
                    l_b = l[:bib_i + 1]
                    print(f"l_b: {l_b}")
                    # Loop through l_s
                    for s in range(len(l_b)):
                        # Append a pair (section,a page number) into the list l_sec
                        l2.append((l_b[s][0], get_page_num(l_b[s][1].idnum, l_b[s][1].generation, r)))
                    # print(f"l_sec: {l_sec}")
                    l_text = []
                    # Put  tuples of section title and correlating text to the list l_sec_text
                    for s1 in range(len(l2) - 1): l_text.append(
                        (l2[s1][0], extract_text(l2[s1][1], l2[s1 + 1][1], r)))
                    print(f"l_sec_text: {l_text[5]}")
                    print(f"len of l_sec_text: {len(l_text)}")
                    return l_text
                else:return []


def get_chapters_text(text):
    # Find a line which begins with a word "Chapter"
    l = re.findall("\n[C][Hh][Aa][Pp][Tt][Ee][Rr]\s*[\d]+\n", text)
    print(f" l chapters: {l}")
    # Find a line which begins with a word "Appendix"
    a = re.findall("\n[A][Pp][Pp][Ee][Nn][Dd][Ii][Xx]\s*[A-Za-z0-9]\n", text)
    # A line which begins with a word "Chapter" exists
    if l != []:
        lc = []
        # Generate index of l from 0 to second last index
        for i in range(len(l) - 1):
            # Append tuple( chapter, correlating text) to a list lc
            lc.append((l[i], text[(text.index(l[i]) + len(l[i])):text.index(l[i + 1])]))
        # Append the element which is located next to the last chapter in a list l and its page number to the list lc
        lc.append((l[-1], text[(text.index(l[-1]) + len(l[0])):text.index(a[0])]))
        return lc
    else:
        c = re.finditer("C[Oo][Nn][Tt][Ee][Nn][Tt][Ss]", text)

        if c != []:
            lc = []
            for i in c: lc.append((i.start(), i.end(), i.group(0)))
            print(f" re.finditer(Content) : {lc}")
            # print(f"lc:{lc[0]}")
            ap = re.finditer('Appendix\s?[AI1]\s?.+\n', text)
            # print(f"ap: {list(ap)}")
            lap = []
            for i in ap: lap.append((i.start(), i.end(), i.group(0)))
            # print(f"lap: {lap}")
            while len(lc) > 0 and len(lc[0]) > 0 and len(lap) > 0 and len(lap[0]) > 0 and lc[0][0] > lap[0][0]:
            # while lc[0][0] > lap[0][0] and len(lap) >1:
                lap.pop(0)
            # print(lap[0])
            # if len(lc) > 0 and len(lap) > 0:
            if len(lc) > 0 and len(lc[0]) > 0 and len(lap) > 0 and len(lap[0]) > 0:
                contents = text[lc[0][0]:lap[0][0]]

                text_no_content = text[lap[0][0]:]
                contents = re.sub('\n[\.\s]+', '\n', contents)
                # print(contents)
                chs = re.findall("\n\d+\s?[A-Z].+", contents)

                # print(f"chs before pop: {chs}")
                # print(f"len ch before pop: {len(chs)}")
                li = []
                for n in range(len(chs)):
                    if "Contents" in chs[n] or "CONTENTS" in chs[n][2]: li.append(n)
                for m in li: chs.pop(m)
                # print(f" length after pop:{len(chs)}")
                # print(f"lch after pop: {chs}")
                lch_pos = []
                for ch in range(len(chs)):
                    if re.findall(f"{chs[ch]}", text_no_content, flags=re.IGNORECASE) != []:
                        for t1 in re.finditer(f"{chs[ch]}", text_no_content, flags=re.IGNORECASE):
                            # print(list(set(re.finditer(f"{chs[ch]}", text_no_content, flags=re.IGNORECASE))))
                            # print(f"t1: {t1.start()},{t1.end()},{t1.group(0)}")
                            lch_pos.append((t1.start(), t1.end(), t1.group(0)))
                    else:
                        text1 = chs[ch]
                        text1 = re.sub('\s+', '', text1)
                        ft = re.finditer(f"{text1}", text_no_content, flags=re.IGNORECASE)
                        for i, t2 in enumerate(ft):
                            # print(f" next : {next(ft).group()}")

                            # print(f"t2 {i}: {t2.start()}, {t2.end()}, {t2.group(0)}")
                            if i == 0: lch_pos.append((t2.start(), t2.end(), t2.group(0)))

                # print(f"len of pos: {len(lch_pos)}")
                # print(f" lch_pos: {lch_pos}")
                lp_text = []
                for p in range(len(lch_pos) - 1):
                    lp_text.append((lch_pos[p][2], text_no_content[lch_pos[p][1]: lch_pos[p + 1][1]]))
                # print(f" len of lp_text:{len(lp_text)} ")
                # print(f"lp_text:{lp_text[-1]} ")
                ap2 = re.finditer('Appendix\s?[AI1]\s?.+\n', text_no_content)
                lap2 = []
                for a in ap2: lap2.append((a.start(), a.end(), a.group()))
                # while lch_pos[-1][1] > lap2[0][0] and lap2 != []:
                # while len(lch_pos) > 0 and len(lch_pos[-1]) > 0 and len(lap2) > 0 and len(lap2[0]) > 0 and lch_pos[-1][1] > lap2[0][0]:
                while len(lch_pos) > 0 and len(lch_pos[-1]) > 1 and len(lap2) > 0 and len(lap2[0]) > 0 and lch_pos[-1][1] > lap2[0][0]:
                    lap2.pop(0)

                lp_text.append((lch_pos[-1][2], text_no_content[lch_pos[-1][1]: lap2[0][0]]))
                # (f" len of lp_text:{len(lp_text)} ")
                # print(f"lp_text:{lp_text[-1]} ")
                return lp_text
        else:
            return []
    return []


## 2.19 This function gets the text, cleans text, feeds the clean text to TextStar to get the summary without internet
# or  passes the TextStar's result to API with internet
def paper2out(text,m):
    a, c, body_text = clean_text(text)
    # print(f" \nAbstract:\n {a}")
    # print(f" \nConclusion:\n {c}")
    # print(f"\nBody_text:\n {body_text}")
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

## 2.22 Split text by key word recursive
def cut(text,word,n_words,keep_part):
    # for i in range(len(intr)):
    #     text_no_author = text_no_author.split(str(intr[-1]), 1)[1]
    if n_words >1: cut(text,word,n_words -1,keep_part)
    if n_words ==1: return text.split(word, 1)[keep_part]


### 3.Call the function to create a withow with the specific title, color, and size
window = create_window("Fun Chat",'green4', 900, 800)



### 5.Create a textbox  which contains the output text
#width = 780, height = 208,x=60, y=80,wchar=97, hchar=8
out_box = scroll_text(798, 188, 26, 26, 104, 29)
out_box.insert(END,"User: ",'tag1')
out_box.tag_config('tag1', foreground='red')
out_box.tag_config('tag2', foreground='green')
out_box.bind('<Return>', enter)


### 8. Create a button which a user clicks to upload a file
buttonL = Button(window,bg = "green", text= "Upload a File",font=('Arial', 12,"bold"),
                 width = 30, height = 1, anchor=CENTER, highlightthickness = 1,
                 command = lambda: get_textFfile(out_box))
# Place a button in a correct position
buttonL.place(x = 300, y = 500)
window.mainloop()