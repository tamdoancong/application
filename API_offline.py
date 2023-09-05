# 1. Import all necessary libraries
from tkinter import *
from tkinter.scrolledtext import ScrolledText
from PyPDF2 import PdfReader, generic
from tkinter import filedialog
from builder1 import process_text
import networkx as nx
import re
import os
import openai
import socket
import nltk
import time


# 2. Current working directory
work_dir = os.getcwd()

# 3. Set global variable
# Set global variable for number of sentences and keyphases to extract when internet is not available.
n, k = 5, 5
# Set global variable for number of sentences and keyphases to extract when internet is available.
n_sentences, ks = 36, 5
# Set global variable for number of words in a summary
nw = 100


# 4. All necessary functions
# 4.1 This function creates a window with desired title, color, and size.
def create_window(title, color, w, h):
    # Creat a window
    wd = Tk()
    # Write a title of the window
    wd.title("Summary for Long Document and Fun Chat  ")
    # Set the minimum size of the window when window appears
    wd.minsize(width = w, height = h)
    # Set the background color for the window
    wd.configure(bg = color)
    return wd


# 4.2 This function creates a canvas
# Parameters: window: what window the canvas will be put in, color, width, height,
#x: how many pixels from the left of the window,  y: how many pixels from the top of the window
def create_canvas(window, color, w, h, x, y):
    c = Canvas(window, bg = color, width = w, height = h)
    c.place(x = x, y = y)
    return c


# 4.3 This function creates a textbox with scroll bar
# Parameters: width (pixels); height (pixels);
# x: how many pixels from the left of the window,  y: how many pixels from the top of the window
# wchar:number characters can be inserted for each row; hchar: number characters can be inserted for each column
def scroll_text(w, h, x, y, wchar, hchar):
    # Create a frame in the window
    frame = Frame(window, width = w, height = h)
    frame.place(x = x, y = y)
    text_box = ScrolledText(frame, width = wchar, height = hchar)
    text_box.pack(fill = BOTH, expand = 1)
    return text_box


# 4.4 This function gets the text from a PDF file.
# Parameter: file path
# Return: number of pages; either an empty list or a list of pairs of each chapter's number and
# its correlated text; the text  which was extracted from the PDF file.
def pdf2text(pdf_file):
    reader = PdfReader(pdf_file)
    n_pages = len(reader.pages)
    print(f" number of pages: {n_pages}")
    lp = extract_chapter_pdf(reader)
    text = extract_text(0, n_pages, reader)
    if lp == []: lp = get_chapters_text(text)
    return n_pages, lp, text


# 4.5 This function gets the text from a text file.
# Parameter: file path
# Return: text
def ftext2text(file):
    with open(file, 'r', encoding = "utf-8") as f:
        text = f.read()
    return text


# 4.6 This function uploads a file ( PDF or txt) and returns the absolute path of a file.
# Parameter: none
# Return: file path
def upload_file():
    fname = filedialog.askopenfilename(filetypes = [('PDF Files', '*.pdf'), ('Text Files', '*.txt')])
    return fname


# 4.7 This function gets a user's question and feeds that to chat_API() function
# then gets the answer and insert it to out_box.
# Parameter: Click the Enter key on the  keyboard after finishing enter a question.
# Return: none
def enter(event):
    u_text = out_box.get("1.0", "end-1c")
    # print(u_text)
    if is_key_here() and is_on():
        s_text = chat_API(u_text)
        # time.sleep(3)
        # s_text = re.sub("System ", '', s_text)
    else:
        s_text = " Sorry, currently chat function only works on API mode!"
    out_box.insert(END, "\nSystem: ", 'tag2')
    out_box.insert(END, s_text)
    out_box.insert(END, "\nUser: ", 'tag1')


# 4.8 This function gets the API key from the key box if a user enter an API key.
# Parameter: Click the Enter key on the  keyboard after finishing enter an API key.
def getkey(event):
    text = key_box.get('1.0', "end-1c")
    key = text[178:]
    # print(key)
    key = key.strip()
    key = key.replace(" ","")
    if testkey(key):
        text2file(key, work_dir + "key.txt")
        insert_keybox("The system got the API key! Please pick an API model from this list [gpt-4,gpt-3.5-turbo] then type model's name into this box:")
    else:
        insert_keybox("API mode needs: 1/The internet is connected 2/The left button is ‘API mode’ 3/Click the middle button to \nprovide your OpenAI key file, or enter your key here then click 'Enter:")

def set_api_model(event):
    text = key_box.get('1.0', "end-1c")
    model = text[127:]
    print(model)
    model = model.strip()
    model = model.replace(" ","")
    if testmodel(model):
        insert_keybox(f"The system is working on {model}. API mode is ready to use! ")
        return model
    else:
        f"The  entered model has problem. The system will use GPT 4 model "




# 4.9 This function checks if a given key works or not.
# Parameter: key.
# Return: either True or False.
def testkey(key):
    try:
        openai.api_key = key
        ans = openai.ChatCompletion.create(
            model = "gpt-4",
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Who is president of US?"}
            ]
        )
        if ans.choices[0].message['content'] != "": return True
    except:
        OSError
    pass
    return False


def testmodel(model):
    try:
        openai.api_key = ftext2text(work_dir + "key.txt")
        ans = openai.ChatCompletion.create(
            model = f"{model}",
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Who is president of US?"}
            ]
        )
        if ans.choices[0].message['content'] != "": return True
    except:
        OSError
    pass
    return False


# 4.10 This function writes down a string to a text file.
# Parameter: a string, file path with new name
# Return: none
def text2file(text, file):
    with open(file, 'w', encoding="utf-8") as f:
        f.write(text)


# 4.11 This function gets an input text from the uploaded file.
# Parameter: out_box
# Return: None
def get_textFfile(out_box):
    # Clean the output textbox
    if count_words(out_box) > 1000: out_box.delete("1.0", END)
    # Get the absolute path of the uploading file
    fname = upload_file()
    # If a user click the right button "Upload file" but will not pick a file and close the widow.
    if fname == "":
        pass
    else:
        title = get_info(fname)
        # If the uploading file is pdf,
        if is_pdf(fname):
            # convert to a string
            n_pages, lp, text = pdf2text(fname)
            # print(f" lp: {lp}")
            out_text = ""
            # If the file can be extracted by list of chapters(sections) and number of pages great than 100
            if n_pages > 100 and lp != []:

                # If a device is connected to the internet and user choose " API mode"
                # and a valid OpenAI API key is provided.
                if is_on() and is_key_here():
                    # For each chapter:
                    for e in lp:
                        # Call the function clean_text() to clean each chapter's text
                        a, c, chap = clean_text(e[1])
                        # Feeds each chapter's clean text to a graph algorithm and get n_sentences.
                        gM, gk = get_n_sents(chap, n_sentences, ks)
                        # Pass the summary result of TextStar to API model
                        # and set the output's words = get_sents_box('').
                        r_chap = connect_API(gM, get_sents_box(''))
                        time.sleep(1)
                        # The summary from API model will fix  a number of words,
                        # so the last sentence usually will be uncompleted sentence.
                        # This step just get finished sentences.
                        sents = r_chap.split('.')
                        s_chap = ".".join(sents[:-1])
                        # Concatenate all chapters' summary from API
                        out_text += "\n" + e[0] + s_chap + '.' + "\n"
                        # get a desired number of words for a summary for a whole book.
                    APIsumbook = connect_API(out_text, get_sents_box(''))
                    time.sleep(1)
                    # Insert the results to the outbox
                    insert_outbox_book(title, APIsumbook, out_text, n_pages)
                # System works in local mode.
                else:
                    # Get summary from a graph algorithm for an entire book.
                    sumbook, gk = get_n_sents(text, get_sents_box(''), k)
                    # print(f" number of sentence for summary: {get_sents_box('')}")
                    # For each chapter:
                    for e in lp:
                        # Call the function clean_text() to clean each chapter's text.
                        a, c, chap = clean_text(e[1])
                        # Get a summary for each chapter from a graph algorithm.
                        gM, gk = get_n_sents(chap, get_sents_box(""), k)
                        # print(gM)
                        # Concatenate all chapters' summary from a graph algorithm.
                        out_text += '\n' + e[0] + gM + "\n"
                    # Insert a summary for a whole book to out_box.
                    insert_outbox_book(title, sumbook, out_text, n_pages)
            # If chapters' structure cannot extract from PDF file.
            else:
                # Call function paper2out(text) to process the text which was extracted from PDF file.
                nsa, a, c, summary = paper2out(text)
                # If the system is working in a "Local mode" and a is not an empty string
                # and the desired number of summary's sentences less than number sentences in a.
                if a != "" and user_know() == "Local mode!" and get_sents_box("") < nsa:
                    # Insert title and a to out_box.
                    insert_outbox_article(title, a, "by author(s)", n_pages)
                else:
                    # Insert title and summary to out_box.
                    insert_outbox_article(title, summary, "", n_pages)
        # If an uploading file is a txt file,
        if is_txt(fname):
            # convert the file to a string.
            text = ftext2text(fname)
            # Call function paper2out(text) to process the string
            nsa, a, c, summary = paper2out(text)
            # If API mode is  working:
            if is_on() and is_key_here():
                insert_outbox_article(title, summary, None, None)
            # If  "Local mode" is working and a is not an empty string
            # and the desired number of summary's sentences less than number sentences in a.
            elif a != "" and user_know() == "Local mode!" and get_sents_box("") < nsa:
                insert_outbox_article(title, a, " by author(s)", None)
                out_box.insert(END, "\nUser: ", 'tag1')
            else:
                insert_outbox_article(title, summary, None, None)


# 3.13 This function inserts an article's summary  to the out_box.
# Parameter: of an uploading document, summary of the document, a string "by author(s)".
# Return: none
def insert_outbox_article(title, summary, aut, n):
    out_box.insert(END, "\nSystem: ", 'tag2')
    out_box.insert(END, f"{user_know()} ", 'tag3')
    out_box.insert(END, f"Summary of the uploaded {n}-page document ", 'tag4')
    out_box.insert(END, f"{title}", 'tag5')
    out_box.insert(END,f" {aut}:\n", 'tag4')
    out_box.insert(END, summary)
    out_box.insert(END, "\nUser: ", 'tag1')


# 3.13 This function inserts a book's summary  to the out_box.
# Parameter: the title of an uploading book, a summary for the whole book , each chapter's summary.
# Return: none
def insert_outbox_book(title, sumbook, out_text, p):
    out_box.insert(END, "\nSystem: ", 'tag2')
    out_box.insert(END, f"{user_know()} ", 'tag3')
    out_box.insert(END, f"Summary of the uploaded {p}-page document ", 'tag4')
    out_box.insert(END, f"{title}:", 'tag5')
    out_box.insert(END, f" \n{sumbook}")
    out_box.insert(END, f"\nSummary for each chapter of the Uploaded Document: ", 'tag4')
    out_box.insert(END, f"{title}:", 'tag5')
    out_box.insert(END, f" \n{out_text}")
    out_box.insert(END, "\nUser: ", 'tag1')


# 3.14 This function checks which mode the system is currently working.
# Parameter: none
# Return: either "API mode!" or "Local mode!"
def user_know():
    if is_on() and is_key_here():
        return "API mode!"
    else:
        return "Local mode!"


# 3.15 This function gets n sentences from a long document by a graph based algorithm.
# Parameters: text,the number sentences of an output summary,the number keywords of an output.
# Return: summary, keywords
def get_n_sents(text, n, k):
    sents, kwds = process_text(text=text, ranker=nx.degree_centrality, sumsize=n,kwsize=k, trim=80)
    summary = ""
    #  "sents" is a list of tuples, each tuple is a pair of sentence's id and sentence's text.
    for sent in sents:
        # Extract only the sentence's text from each tuple and convert the tuple to string.
        s = str(sent[1])
        summary += " " + s
    return summary, kwds


# 3.16 This function cleans text.
# Parameter: a string.
# Return: either an abstract or an empty string,either a conclusion or an empty string,
#        a string without an abstract and a conclusion.
def clean_text(text):
    # Replace strange symbols which are not in [a-zA-Z0-9.!?:,{}()@$\n ] between character f and t by -.
    text = re.sub('f[^\w.!?:,{}%\[\]()@$/\n ]t', 'f-t', text)
    # Remove all strange synbols which are not in [a-zA-Z0-9.!?:,{}()@$\n -].
    text = re.sub('[^\w.!?:,{}%()\[\]@$=/~\n -]', ' ', text)  # this line code does not  result some missing words
    # Remove References and all text appears after that by calling remove_references(text) function.
    text = remove_references(text)
    # Call  function get_Abstract(text) to get an abstract and a text without abstract.
    ab, text = get_Abstract(text)
    # Remove Algorithm format if they exist.
    text = re.sub('\nAlcgorithm.*?end(\n\d.*?end)+', ' ', text, flags=re.DOTALL)
    # Remove Figure if they exist.
    text = re.sub('\n[Ff]igure.*?\n', '\n', text, flags=re.DOTALL)
    # Remove Table if they exist.
    text = re.sub('\n[Tt]able.*?\.', ' ', text, flags=re.DOTALL)
    # Remove ROUGE if they exist.
    text = re.sub('ROUGE-[\dL]', ' ', text, flags=re.DOTALL)
    # Remove F1@5 if they exist.
    text = re.sub('F1@[\d]*', ' ', text, flags=re.DOTALL)
    # Remove text in between 2 round brackets if they exist.
    text = re.sub('\([^)]*\)', ' ', text, flags=re.DOTALL)
    # Remove text in between 2 square brackets if they exist.
    text = re.sub('\[.*\]', ' ', text, )
    # Remove https if they exist.
    text = re.sub('\d?http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    # Remove string after forward slash (/) which usually is converted from a table from pdf if they exist.
    text = re.sub('\n?[/].+\n', ' ', text)
    # Remove 1 or more white space before a comma.
    text = re.sub('[\s]+,', ',', text)
    # Remove a string of number which usually is converted from a table from pdf.
    text = re.sub('\n^\d+\.?\d*$\n', '', text)
    # Remove the lines with a lot numbers which often come from tableges.
    text = re.sub('\n?[\w\s-]*(\s*?[\d]+[.][\d]+-?)+', ' ', text)
    # Replace '..' by '.'.
    text = re.sub('\.\.', '.', text)
    # Call a function get_Conclusion(text) to get a conclusion.
    c = get_Conclusion(text)
    # Replace all newlines by ' '.
    text = re.sub('\n', ' ', text)
    return ab, c, text


# 3.17  This function checks if the internet is connected or not.
# Parameter: none.
# Return: either True or False.
def is_internet():
    try:
        # Try to connect to "www.google.com" at port 443
        s = socket.create_connection(("www.google.com", 443))
        if s != None: return True
    except OSError:
        pass
    insert_keybox("The system is in the local mode! Please enter the desired number of sentences for the summary, then click the 'Upload a file' button in the bottom right to upload a document to the system!")
    insert_sents_box("Number of summary's sentences:")
    return False


# 3.18 This function  connects to the Open API model.
# Parameter: text, number words of a summary.
# Return: either a result summary or an error message.
def connect_API(n_sentences, m):
    openai.api_key = ftext2text(work_dir + "key.txt")
    s_answer = openai.ChatCompletion.create(
        # this model has total 4,097 tokens (input and output)
        model = "gpt-4",
        # max_tokens = m,
        messages =[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Summary to {m} words:{n_sentences}"}
        ]
    )
    print(f"Connected to API mode")
    return s_answer.choices[0].message['content']


# 3.19 This function connects to OpenAI API model.
# Parameter: a prompt.
# Return: either an answer for a prompt or an error message.
def chat_API(uq):
    openai.api_key = ftext2text(work_dir + "key.txt")

    answer = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"{uq}"}
        ]
    )
    return answer.choices[0].message['content']


# 3.20 This function gets a title of an uploading pdf file.
# Parameter: a path file
# Return: either a title or a empty string.
def get_info(pdf_file):
    r = PdfReader(pdf_file)
    t = '"' + get_title(r) + '"'
    return t


# 3.21 This function gets the first line of text.
# Parameter: PdfReader
# Return: either a text or an empty string.
def get_title(r):
    i = 0
    text = ""
    while text == "":
        p = r.pages[i]
        text = p.extract_text()
        i += 1
    lns = text.split('\n')
    return lns[0]


# 3.22 This function gets an Abstract and remove author's information.
# Parameter: text.
# Return: either an  Abstract or an empty string and a text without an Abstract .
def get_Abstract(text):
    # Find the word 'Abstract'or ABSTRACT'
    # The first letter must be uppercase.
    # If use flags=re.IGNORECASE here the result will return 'abstract'
    abs = re.findall('\nAbstract|ABSTRACT', text)
    # Find the word 'Introduction' or 'INTRODUCTION'
    intr = re.findall('Introduction|INTRODUCTION', text)
    # If the text contains the word 'Abstract',no matter lowercase or uppercase
    if abs != []:
        # Split the text into 2 parts by the key word 'Abstract'or 'ABSTRACT',
        # The word 'abstract' can be somewhere in body text or reference, so it causes a wrong spliting position
        # Get the second part for text which does not have author's information
        text_no_author = text.split(str(abs[0]), 1)[1]
        # Split the text into 2 parts by the key word 'Introduction' or 'INTRODUCTION',
        # Get the first part which is abstract
        if len(intr) > 0:
            abstract1 = text_no_author.split(str(intr[0]), 1)[0]
            abstract1 = re.sub('\n1\.?', '', abstract1)
            abstract1 = re.sub('\n', ' ', abstract1)
            for i in range(len(intr)): text_no_author = text_no_author.split(str(intr[-1]), 1)[1]
        # Find the word 'KEYWORDS' or 'keywords'
        k = re.findall('KEYWORDS|Keywords', abstract1)
        # If the abstract1 contains the word 'KEYWORDS' or 'keywords'
        if k != []:
            # Split the text into 2 parts by the key word 'KEYWORDS' or 'Keywords',
            # Get the first part for abstract1 which does not have key words part
            abstract2 = abstract1.split(str(k[-1]), 1)[0]
            abstract2 = re.sub('\.\s?[1]($|\n)', '.', abstract2)
            return abstract2, text_no_author
        # If the abstract1 does not contains the word 'KEYWORDS' or 'Keywords'
        else:
            return abstract1, text_no_author
    else:
        return '', text


# 3.23 This function removes references
# Parameters: text
# Return: text without References
def remove_references(text):
    # Find the word 'References or REFERENCES'
    r = re.findall('References|REFERENCES', text)
    # Find the word 'Acknowledgements' or 'ACKNOWLEDGEMENTS'
    a = re.findall('Acknowledgements|ACKNOWLEDGEMENTS', text)
    # If the word 'References or REFERENCES' exists
    if r != []:
        # If the word 'Acknowledgements' or 'ACKNOWLEDGEMENTS' exists
        if a != []:
            text = text.split(str(a[-1]), 1)[0]
        # If the word 'Acknowledgements' or 'ACKNOWLEDGEMENTS' does not exists
        else:
            text = text.split(r[-1], 1)[0]
    return text


# 3.24 This function gets a Conclusion.
# Parameters: text.
# Return: either a Conclusion or an empty string.
def get_Conclusion(text):
    # Find the word 'Conclusion' or 'CONCLUSION'
    c = re.findall('Conclusion|CONCLUSION', text)
    # If the word 'Conclusion' or 'CONCLUSION'  exists
    if c != []:
        # Split the text into 2 parts by key word 'Conclusion' or 'CONCLUSION', get the second part.
        conc = text.split(str(c[-1]), 1)[1]
        return conc
    else:
        return ""


# 3.25 This function gets a page number from an indirect object.
# Parameters: id number, generation number, PdfReader.
# Return: a page number.
def get_page_num(n1, n2, r):
    return r._get_page_number_by_indirect(generic.IndirectObject(n1, n2, r))


# 3.26 This function extracts text from a PDF file from page pm to page pn.
# Parameters: the page which begin to extract text, stop to extract text after this page, PdfReader.
# Return: text .
def extract_text(pm, pn, r):
    # Define a variable text with an empty string.
    text = ""
    # Loop from  page pm to  page pn.
    for p in range(pm, pn):
        # Call the function pages from PdfReader class.
        page = r.pages[p]
        # Concatenate extracting text from each page to a variable text.
        text += page.extract_text()
    return text

# 3.26 This function gets chapters'/sections' text directly from PDF file.
# Parameter: PdfReader
# Return: Either an empty list or a  list of pairs of chapters'(sections') number and their correlating text.
def extract_chapter_pdf(r):
    # Create an empty list l which will store none list type elements of outline.
    l = []
    #  Get outline  from PDF format
    outline = r._get_outline()
    # If the extracting outline  is empty, then return an empty list
    if outline == []:
        return []
    # If the extracting outline  is not empty,
    else:
        # Loop through all elements in outline.
        for o in outline:
            # If type of the element is not list, then put that element's title and page  to the list l.
            if type(o) != list: l.append((o.title, o.page))
        # Check if the word "Chapter"  is in the list l or not.
        find = re.findall("Chapter|CHAPTER", str(l))
        # If the word "Chapter|CHAPTER" is in the list l,
        if find != []:
            # Create an empty list lc which will contain tuples of chapter and the starting page number of the cahpter.
            lc = []
            # Create an empty list li which will contain indexes  of l where store elements which include either  the word "Chapter" or "CHAPTER".
            li = []
            # Loop through all elements in the list l.
            for i in l:
                # If the word "Chapter"  is in an element i:
                if "Chapter" in i[0] or "CHAPTER" in i[0]:
                    # Append a pair of chapter and a correlating the starting page number of the chapter to the list lc.
                    lc.append((i[0], get_page_num(i[1].idnum, i[1].generation, r)))
                    # Put the index of element i to the list li.
                    li.append(l.index(i))
            # Append the element which is located next to the last chapter in a list l and its starting page number to the list lc
            lc.append((l[li[-1] + 1][0], get_page_num(l[li[-1] + 1][1].idnum, l[li[-1] + 1][1].generation, r)))
            # Create an empty list lp which will contain pairs of chapter number and text in correlated chapter.
            lp = []
            # Put  tuples of chapter number and correlating text to the list lp.
            for e in range(len(lc) - 1): lp.append((lc[e][0], extract_text(lc[e][1], lc[e + 1][1], r)))
            return lp
        # If the word "Chapter" is not in the list l:
        else:
            # Check if the word "Conclusion" is in the list l or not.
            find1 = re.findall("Conclusion|CONCLUSION", str(l))
            # If the word "Conclusion" is in the list l:
            if find1 != []:
                # Create an empty list l_sec, which will contain pairs of section's number and  correlated the starting page number.
                l_sec = []
                # Loop through the list l
                for i in l:
                    # If an element contains a word "Conclusion" or "CONCLUSION"
                    if "Conclusion" in i[0] or "CONCLUSION" in i[0]:
                        # Get the index of the list l where stores the element that includes either "Conclusion" or "CONCLUSION"
                        con_i = l.index(i)
                # Create a list l_s such that l_s contains elements in l
                # from index 0 to the index next to the index of element which has the word "Conclusion".
                l_s = l[:con_i + 2]
                # Loop through l_s.
                for s in range(len(l_s)):
                    # Append a pair (section,a starting page number of correlated section) into the list l_sec
                    l_sec.append((l_s[s][0], get_page_num(l_s[s][1].idnum, l_s[s][1].generation, r)))
                # Create an empty list, which will contain pairs of section's number and correlated text.
                l_sec_text = []
                # Put  tuples of section's number and correlating text to the list l_sec_text
                for s1 in range(len(l_sec) - 1): l_sec_text.append(
                    (l_sec[s1][0], extract_text(l_sec[s1][1], l_sec[s1 + 1][1], r)))
                return l_sec_text
            else:
                # Find either "Bibliography" or "BIBLIOGRAPHY" in the list l.
                find2 = re.findall("Bibliography|BIBLIOGRAPHY", str(l))
                # If there is either "Bibliography" or "BIBLIOGRAPHY" in the list l:
                if find2 != []:
                    # Create an empty list,which will contain pairs of section and the correlated starting page number.
                    l2 = []
                    # Loop through the list l
                    for i in l:
                        # If an element contains a word "Bibliography|BIBLIOGRAPHY",
                        if "Bibliography" in i[0] or "BIBLIOGRAPHY" in i[0]:
                            # Get the index of the list l where stores that element.
                            bib_i = l.index(i)
                    # Create a list l_b such that l_b contains elements in l
                    # from index 0 to the index next to the index of element which has the word "Bibliography|BIBLIOGRAPHY"
                    l_b = l[:bib_i + 1]
                    # Loop through l_b
                    for s in range(len(l_b)):
                        # Append a pair (section's number,the correlated starting page number) into the list l_sec
                        l2.append((l_b[s][0], get_page_num(l_b[s][1].idnum, l_b[s][1].generation, r)))
                    # Create an empty list, which will contain pairs of section's number and correlated text.
                    l_text = []
                    # Put  tuples of section's  and correlating text to the list l_sec_text.
                    for s1 in range(len(l2) - 1): l_text.append(
                        (l2[s1][0], extract_text(l2[s1][1], l2[s1 + 1][1], r)))
                    return l_text
                else:
                    return []


# 3.27 This function gets chapters'/sections' text from a given text.
# Parameter: text
# Return: Either an  empty list or a list of pairs,
# where each pair contains of a chapters'/sections' number and its correlated text.
def get_chapters_text(text):
    # Find a line which begins with a word "Chapter"
    l = re.findall("\n[C][Hh][Aa][Pp][Tt][Ee][Rr]\s*[\d]+\n", text)
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
        # Find the word "Content" or "CONTENT"
        c = re.finditer("C[Oo][Nn][Tt][Ee][Nn][Tt][Ss]", text)
        # If either the word "Content" or "CONTENT" exist:
        if c != []:
            # Create an empty list
            lc = []
            for i in c: lc.append((i.start(), i.end(), i.group(0)))
            ap = re.finditer('Appendix\s?[AI1]\s?.+\n', text)
            lap = []
            for i in ap: lap.append((i.start(), i.end(), i.group(0)))
            while lc != [] and len(lap) > 1 and lc[0][0] > lap[0][0]:
                lap.pop(0)
            if len(lc) > 0 and len(lap) > 0:
                contents = text[lc[0][0]:lap[0][0]]
                text_no_content = text[lap[0][0]:]
                contents = re.sub('\n[\.\s]+', '\n', contents)
                chs = re.findall("\n\d+\s?[A-Z].+", contents)
                li = []
                for n in range(len(chs)):
                    if "Contents" in chs[n] or "CONTENTS" in chs[n][2]: li.append(n)
                for m in li: chs.pop(m)
                lch_pos = []
                for ch in range(len(chs)):
                    if re.findall(f"{chs[ch]}", text_no_content, flags=re.IGNORECASE) != []:
                        for t1 in re.finditer(f"{chs[ch]}", text_no_content, flags=re.IGNORECASE):
                            lch_pos.append((t1.start(), t1.end(), t1.group(0)))
                    else:
                        text1 = chs[ch]
                        text1 = re.sub('\s+', '', text1)
                        ft = re.finditer(f"{text1}", text_no_content, flags=re.IGNORECASE)
                        for i, t2 in enumerate(ft):
                            if i == 0: lch_pos.append((t2.start(), t2.end(), t2.group(0)))
                lp_text = []
                for p in range(len(lch_pos) - 1):
                    lp_text.append((lch_pos[p][2], text_no_content[lch_pos[p][1]: lch_pos[p + 1][1]]))
                ap2 = re.finditer('Appendix\s?[AI1]\s?.+\n', text_no_content)
                lap2 = []
                for a in ap2: lap2.append((a.start(), a.end(), a.group()))
                while len(lch_pos[-1]) > 0 and len(lap2) > 1 and lch_pos[-1][1] > lap2[0][0]:
                    lap2.pop(0)
                lp_text.append((lch_pos[-1][2], text_no_content[lch_pos[-1][1]: lap2[0][0]]))
                return lp_text
        else:
            return []
    return []


# 3.28 This function gets a text, cleans the text, feeds the clean text to a summary graph based algorithm
# to get the summary without internet or  passes the TextStar's result to API with internet
# Parameter: text
# Return: number sentences in an abstract, an abstract or an empty string, a conclusion or an empty string,
# and a summary

def paper2out(text):
    # Call the clean_text(text) function to clean the text.
    a, c, body_text = clean_text(text)
    # Use nltk sent_tokenize to get number sentences of a.
    sents = nltk.tokenize.sent_tokenize(a)
    nsa = len(sents)
    a = ""
    osummary = ""
    for s in sents:
        if ("University" or "Author" or "@") not in s: a += s
    if is_key_here() and is_on():

        # Get M sentences by Textstar
        gM, gk = get_n_sents(body_text, n_sentences, ks)
        # Concatenate  the abstract, the conclusion and the M sentences
        t1 = a + gM + c
        # and pass result to openAI API model and get the summary.
        print(f"num of words: {get_sents_box('')}")
        st = connect_API(t1, get_sents_box(""))
        # time.sleep(10)
        sents = st.split('.')
        summary = ".".join(sents[:-1])
        osummary += "\n" + summary + '.'
    # If internet is not available
    else:
        sum, kw = get_n_sents(body_text, get_sents_box(""), k)
        osummary += sum
    return nsa, a, c, osummary


# 3.29 This function checks a file is PDF or not
# Parameter: a file path.
# Return : True or False.
def is_pdf(fname):
    if fname[-3:] == 'pdf':
        return True
    else:
        return False


# 3.30 This function checks a file is txt file or not.
# Parameter: a file path.
# Return : True or False.
def is_txt(fname):
    if fname[-3:] == 'txt':
        return True
    else:
        return False


# 3.31 This function connects to the left button.
# Parameter: none.
# Return : none.
def on_off():
    # If the left button shows "Local mode":
    if buttonL.config('text')[-1] == "Local mode":
        # When a user clicks the left button, the left button will change to "API mode".
        buttonL.config(text = "API mode")
        # Insert the text below to key_box.
        insert_keybox("API mode needs: 1/The internet is connected 2/The left button is ‘ API mode’ 3/Click the middle button to \nprovide your OpenAI key file, or enter your key here then click 'Enter:")
        # Insert the text below to sents_box.
        insert_sents_box("Number of summary's words:")
        if not is_internet():
            out_box.insert(END, "\nSystem: ", 'tag2')
            out_box.insert(END,"The internet is not currently connected. Please connect your device to the internet if you want to use the API mode!")
            out_box.insert(END, "\nUser: ", 'tag1')
        if is_internet() and not is_key_here():
            out_box.insert(END, "\nSystem: ", 'tag2')
            out_box.insert(END, "Your device is connected to the internet! The left button is ‘ API mode’! Please click the bottom middle button to \nprovide your OpenAI key text file, or enter your key into the top left box after the colon  then click 'Enter' if you want to use the API mode!")
            out_box.insert(END, "\nUser: ", 'tag1')


    # If the left button shows "API mode":
    else:
        # When a user clicks the left button, the left button will change to "Local mode".
        buttonL.config(text = "Local mode")
        # Insert the text below to sents_box.
        insert_keybox("The system is in the local mode! Please enter a desired number of sentences for the summary into the top \nright corner box, then click the 'Upload a file' button to upload a document to the system!")
        # Insert the text below to sents_box.
        insert_sents_box("Number of summary's sentences:")


# 3.32 This function check if a "API mode" is picked by a user.
# Parameter: none.
# Return : True or False.
def is_on():
    if buttonL.config('text')[-1] == "API mode":
        return True
    else:
        return False

# 3.33 This function counts the current words in a textbox.
# Parameter: textbox.
# Return : number of words.
def count_words(box):
    return len(box.get("1.0", END).split(" "))

# 3.34 This function connects to the middle button "Upload a key".
# Parameter: none.
# Return : none.
def upload_key():
    file = upload_file()
    if is_txt(file):
        key = ftext2text(file)
        if testkey(key):
            text2file(key, work_dir + "key.txt")
            print(f" key was saved at {work_dir}\key.txt")
            insert_keybox("The system got a working API key")
            # insert_keybox("The API mode is ready to use! You can  start a chat with the system or enter a desired number of words for a summary into the top right corner box, then click the 'Upload a File' button!")
        else:
            insert_keybox(
                "API mode needs:1/The internet is connected 2/The left button is ‘ API mode’ 3/Click the middle button to \nprovide your OpenAI key file, or enter your key here then click 'Enter:")
        return file
    else:
        insert_keybox(
            "API mode needs:1/The internet is connected 2/The left button is ‘ API mode’ 3/Click the middle button to provide your OpenAI key file, or enter your key here then click 'Enter:")

# 3.35 This function counts checks if the provided key is valid or not.
# Parameter: none.
# Return : True or False.
def is_key_here():
    if not os.path.exists(work_dir + "key.txt"): return False
    else:
        key = ftext2text(work_dir + "key.txt")
        if testkey(key):
            insert_keybox("API mode is ready to use! You can  start a chat with the system or enter a desired number of words for the summary into the top right corner box, click the 'Upload a File' button !")
            # out_box.insert(END,"User: ", 'tag1')# make User: appears after chat question
            return True
        else:
            insert_keybox(
                "The system is in the local mode! Please enter a desired number of sentences for the summary into the top \nright corner box, then click the 'Upload a file' button to upload a document to the system!")
            return False


def insert_keybox(message):
    key_box.delete('1.0', END)
    key_box.insert(END, f"{message}")
    key_box.see(END)


def insert_sents_box(message):
    sents_box.delete('1.0', END)
    sents_box.insert('1.0', f"{message}",END)
    sents_box.see(END)


def num_sents(event):
    t = sents_box.get("1.0", "end-1c")
    print(f"num sentences : {t[29:]}")
    return t[29:].strip()

ws = 0
num = 0
def get_sents_box(event):
    global num, ws
    t = sents_box.get("1.0", "end-1c")
    # print(len(t))
    # print(f" sentence box: {t}")
    if not is_on():
        r = re.findall("[^0-9]*", t[30:])
        if r == [''] or r[0] != '':
            num = n
            # print(f"number of sentence: {num}")
            return num

        else: return num2int(t[30:])
    else:
    # number of words
        r = re.findall("[^0-9]*", t[26:])
        if r ==[''] or r[0] != '':
            ws = nw
            return ws
        else:
            return num2int(t[26:])

# This function cleans space, newline, and converts an input string number to an integer
def num2int(num):
    num = num.strip()
    num = num.replace(" ", "")
    num = num.replace("\n", "")
    num = int(num)
    return num


### 3.Call the function to create a withow with the specific title, color, and size
window = create_window("Fun Chat", 'green4', 1086, 800)

key_box = Text(window, width = 108, height = 2, fg = 'forest green')
key_box.place(x = 26, y = 8)
key_box.insert(END, "The system is in the local mode! Please enter a desired number of sentences for the summary into the top \nright corner box, then click the 'Upload a file' button to upload a document to the system!")
key_box.bind('<Return>', getkey)

sents_box = Text(window, width = 19, height = 2, wrap = WORD, fg = 'forest green')
sents_box.place(x = 900, y = 8)
sents_box.insert(END, "Number of summary's sentences:")
sents_box.bind('<Return>', get_sents_box)

### 5.Create a textbox  which contains the output text
# width = 780, height = 208,x=60, y=80,wchar=97, hchar=8
out_box = scroll_text(998, 188, 26, 50, 126, 28)
out_box.tag_config('tag1', foreground='red', font=('Arial', 10, "bold"))
out_box.tag_config('tag2', foreground='green', font=('Arial', 10, "bold"))
out_box.tag_config('tag3', foreground='purple4', font=('Arial', 10, "italic"))
out_box.tag_config('tag4', foreground='forest green', font=('Arial', 10, "italic"))
out_box.tag_config('tag5', foreground='brown4', font=('Arial', 10, "italic"))

out_box.insert(END, "System: " ,'tag2')
out_box.insert(END,"Hello! How are you doing  today? Please start a chat with me by typing your words after 'User:', or enter a desired \nnumber of (sentences) words for a summary into the top right corner box, then click the 'Upload a File' button in the \nbottom-right to upload a document for summary! ")
out_box.insert(END,"\nUser: ",'tag1')
out_box.bind('<Return>', enter)
text = out_box.get("1.0", END)
# print(f"text outbox: {text}")

### 8. Create a button which a user clicks to upload a file
buttonR = Button(window, bg="green", text="Upload a File", font=('Arial', 12, "bold"),
                 width=30, height=1, anchor=CENTER, highlightthickness=1,
                 command=lambda: get_textFfile(out_box))
# Place a button in a correct position
buttonR.place(x=746, y=504)

buttonL = Button(window, bg="green", text="Local mode", font=('Arial', 12, "bold"),
                 width=30, height=1, anchor=CENTER, highlightthickness=1,
                 command=lambda: on_off())
buttonL.place(x=26, y=504)

buttonM = Button(window, bg="green", text="Provide your API key", font=('Arial', 12, "bold"),
                 width=30, height=1, anchor=CENTER, highlightthickness=1,
                 command=lambda: upload_key())
buttonM.place(x=386, y=504)

window.mainloop()