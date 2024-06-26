# 1.Import all necessary libraries
from tkinter import *
from tkinter.scrolledtext import ScrolledText
from PyPDF2 import PdfReader, generic
from tkinter import filedialog
import re
import nltk
import os
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import WordNetLemmatizer
import networkx as nx

# 2. RingStar algorithm
# Start : TextRings algorithm
stops=['a', 'about', 'above', 'across', 'after', 'again', 'al', 'all', 'almost', 'alone', 'along', 'already', 'also', 'although', 'always', 'among', 'an', 'and', 'another', 'any', 'anybody', 'anyone', 'anything', 'anywhere', 'are', 'around', 'as', 'at', 'away', 'b', 'back', 'backed', 'backing', 'backs', 'be', 'been', 'before', 'began', 'behind', 'best', 'better', 'between', 'both', 'but', 'by', 'c', 'came', 'can', 'cannot', 'case', 'cases', 'certain', 'certainly', 'clear', 'clearly', 'come', 'could', 'd', 'did', 'do', 'does', 'done', 'down', 'down', 'downed', 'downing', 'downs', 'during', 'e', 'each', 'early', 'either', 'end', 'ended', 'ending', 'ends', 'enough', 'et', 'even', 'evenly', 'ever', 'every', 'everybody', 'everyone', 'everything', 'everywhere', 'f', 'face', 'faces', 'fact', 'facts', 'far', 'felt', 'few', 'find', 'finds', 'first', 'for', 'four', 'from', 'full', 'fully', 'further', 'furthered', 'furthering', 'furthers', 'g', 'gave', 'general', 'generally', 'get', 'gets', 'go', 'going', 'good', 'goods', 'got', 'great', 'greater', 'greatest', 'group', 'grouped', 'grouping', 'groups', 'h', 'had', 'has', 'have', 'having', 'he', 'her', 'here', 'herself', 'high', 'high', 'high', 'higher', 'highest', 'him', 'himself', 'his', 'how', 'however', 'i', 'if', 'important', 'in', 'interest', 'interested', 'interesting', 'interests', 'into', 'is', 'it', 'its', 'itself', 'j', 'just', 'k', 'keep', 'keeps', 'kind', 'knew', 'know', 'known', 'knows', 'l', 'large', 'largely', 'last', 'later', 'latest', 'least', 'less', 'let', 'lets', 'like', 'likely', 'long', 'longer', 'longest', 'm', 'made', 'make', 'making', 'man', 'many', 'may', 'me', 'might', 'more', 'most', 'mostly', 'mr', 'mrs', 'much', 'must', 'my', 'myself', 'n', 'need', 'needed', 'needing', 'needs', 'never', 'new', 'newer', 'newest', 'next', 'no', 'nobody', 'non', 'noone', 'not', 'nowhere', 'o', 'of', 'off', 'often', 'on', 'once', 'one', 'only', 'open', 'or', 'other', 'others', 'our', 'out', 'over', 'p', 'part', 'parted', 'parting', 'parts', 'per', 'perhaps', 'place', 'places', 'point', 'pointed', 'pointing', 'points', 'present', 'presented', 'presenting', 'presents', 'problem', 'problems', 'put', 'puts', 'q', 'quite', 'r', 'rather', 'really', 'room', 'rooms', 's', 'said', 'same', 'saw', 'say', 'says', 'seem', 'seemed', 'seeming', 'seems', 'sees', 'several', 'shall', 'she', 'should', 'show', 'showed', 'showing', 'shows', 'side', 'sides', 'since', 'so', 'some', 'somebody', 'someone', 'something', 'somewhere', 'soon', 'state', 'states', 'still', 'still', 'such', 'sure', 't', 'than', 'that', 'the', 'their', 'them', 'then', 'there', 'therefore', 'these', 'they', 'thing', 'things', 'think', 'thinks', 'this', 'those', 'though', 'thought', 'thoughts', 'three', 'through', 'thus', 'to', 'today', 'together', 'too', 'took', 'toward', 'two', 'u', 'under', 'until', 'up', 'upon', 'us', 'use', 'used', 'uses', 'v', 'very', 'w', 'want', 'wanted', 'wanting', 'wants', 'was', 'way', 'ways', 'we', 'well', 'wells', 'went', 'were', 'what', 'when', 'where', 'whether', 'which', 'while', 'who', 'whole', 'whose', 'why', 'will', 'with', 'within', 'without', 'work', 'worked', 'working', 'works', 'would', 'x', 'y', 'yet', 'you', 'your', 'yours', 'z']


def text_normalize(text):
    lemmatizer = WordNetLemmatizer()
    sents = sent_tokenize(text)
    l_sents_lemmas =[]
    for sent in sents:
        if len(sent)> 30 and len(sent) < 200 and re.findall("=|\.,|pages",str(sent))==[]:
        # if  len(sent)> 30 and len(sent) < 200 and '='not in sent and '.,' not in sent:
            words = word_tokenize(sent)
            l_lemmas = []
            if len(words) > 5:
                for word in words:
                    lemma = lemmatizer.lemmatize(word)
                    if lemma.lower() not in stops and lemma not in [',', '.', '!', '?', '@', '#', '$', '%', '&', '*', '^', '+', '-', '/', '|', '~', ':', ')', '(', '=', '}', '{', '[', ']', '1', '2', '3', '4', '5', '6', '7', '8', '9',';']:
                        l_lemmas.append(lemma)
                if not l_lemmas: continue
                l_sents_lemmas.append((sent,l_lemmas))
    # print(l_sents_lemmas)

    return l_sents_lemmas

def l_sents_lemmas2graph(l_sents_lemmas):
    g = nx.DiGraph()
    g.add_edge(0, len(l_sents_lemmas) - 1)  # connect first ID to last ID
    for sent_id, (_, lemmas) in enumerate(l_sents_lemmas):
        if sent_id > 0:
            g.add_edge(sent_id, sent_id - 1)  # connect an ID to a next lower ID in a sequence
        g.add_edge(lemmas[0], sent_id)  # connect first lemma to ID
        # g.add_edge(lemmas[-1], sent_id)
        for i in range(1, len(lemmas)):
            g.add_edge(lemmas[i], lemmas[i - 1])
        #     g.add_edge(lemmas[i],sent_id)
    return g


def get_summary(text,ranker,M):
    lss = text_normalize(text)
    g = l_sents_lemmas2graph(lss)
    unsorted_ranks = ranker(g)
    ranks = sorted(unsorted_ranks.items(), reverse=True, key=lambda e: e[1])
    summary_id = sorted([i[0] for i in ranks if isinstance(i[0], int)][:M])
    all_sents = [sent for (sent, _) in lss]
    sents = [(i, all_sents[i]) for i in summary_id]
    print(f"sents: {sents}")
    return sents
# End : RingStar algorithm

n = 4

# 3. All necessary functions
# 3.1 This function creates a window with desired title, color, and size.
def create_window(title, color, w, h):
    # Creat a window
    wd = Tk()
    # Write a title of the window
    wd.title("Offline Summary Tool")
    # Set the minimum size of the window when window appears
    wd.minsize(width = w, height = h)
    # Set the background color for the window
    wd.configure(bg = color)
    return wd


# 3.2 This function creates a canvas
# Parameters: window: what window the canvas will be put in, color, width, height,
#x: how many pixels from the left of the window,  y: how many pixels from the top of the window
def create_canvas(window, color, w, h, x, y):
    c = Canvas(window, bg = color, width = w, height = h)
    c.place(x = x, y = y)
    return c


# 3.3 This function creates a textbox with scroll bar
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


# 3.4 This function gets the text from a PDF file.
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


# 3.5 This function gets the text from a text file.
# Parameter: file path
# Return: text
def ftext2text(file):
    with open(file, 'r', encoding="utf-8") as f:
        text = f.read()
    return text


# 3.6 This function uploads a file ( PDF or txt) and returns the absolute path of a file.
# Parameter: none
# Return: file path
def upload_file():
    fname = filedialog.askopenfilename(filetypes=[('PDF Files', '*.pdf'), ('Text Files', '*.txt')])
    return fname


# 3.8 This function gets user's desired number of summary sentences.
# Parameter: Click the Enter key on the  keyboard after finishing enter a desired number of summary sentences.
# Return: none
m = 0
def num_sents(event):
    global m
    if m == 0:
        u_text = out_box.get("end-2c linestart", "end-1c")
        out_box.insert(END, "\nSystem: Please click the button below to upload a file!", 'tag2')
        out_box.insert(END,"\nUser:",'tag1')
        r = re.findall("[^0-9]*",u_text[5:])
        if r ==[''] or r[0] != '' : m = n
        else: m = int(u_text[5:])
        print(f" num of sentences:{m}")
    return m


def message_user(event):
    out_box.insert(END, "\nSystem: Please click the button below to upload a file! ", 'tag2')


# 3.11 This function writes down a string to a file.
# Parameter: a string, file path with new name
# Return: none
def text2file(text, file):
    with open(file, 'w', encoding="utf-8") as f:
        f.write(text)


# 3.12 This function gets an input text from the uploaded file.
# Parameter: out_box
# Return:
def get_textFfile(out_box):
    # Get the absolute path of the uploading file
    fname = upload_file()
    # If a user click the right button "Upload file" but will not pick a file and close the widow.
    if fname == "":
        pass
    else:
        # If the uploading file is pdf, convert to a string
        if is_pdf(fname):
            title = os.path.basename(fname)[:-4]
            # convert pdf file to text
            n_pages, lp, text = pdf2text(fname)
            out_text = ""
            # If the file can be extracted by list of chapters(sections) and number of pages great than 100
            if n_pages > 100 and lp != []:
                # Get summary from a graph algorithm for an entire book.
                # ab, c, textbook= clean_text(text)
                # print(f"book :{text}")
                sumbook = get_n_sents(text, num_sents(''))
                print(f" sumbook num_sents: {num_sents('')} ")
                sumbook = sumbook.replace('\n', ' ')
                out_box.insert(END, "\nSystem: ", 'tag2')
                out_box.insert(END, f"Summary for the whole uploaded {n_pages}-page document", 'tag4')
                out_box.insert(END, f" '{title}':", 'tag5')
                out_box.insert(END, f"\n{sumbook}")
                window.update()

                # For each chapter:
                for e in lp:
                    # Call the function clean_text() to clean each chapter's text.
                    a, c, chap = clean_text(e[1])
                    # Get a summary for each chapter from a graph algorithm.
                    gM= get_n_sents(chap, num_sents(""))
                    e0 = e[0].replace('\n', ' ')
                    out_box.insert(END, f"\n\n{e0}: ", 'tag4')
                    out_box.insert(END, gM)
                    out_box.see(END)
                    window.update()
                out_box.insert(END, "\n\nSystem: Please enter a desired number summary sentences and hit 'Return' key!",
                               'tag2')
                out_box.insert(END, "\nUser:", 'tag1')
                out_box.see(END)
                global m
                m = 0
            # If chapters' structure cannot extract from PDF file.
            else:
                # Call function paper2out(text) to process the text which was extracted from PDF file.
                nsa, a, c, summary= paper2out(text)
                # print(f"text; {text}")
                # If a is not an empty string
                # and the desired number of summary's sentences less than number sentences in a.
                if a != ""  and num_sents("")< nsa:
                    # Insert title and a to out_box.
                    insert_outbox_article(title, a,  "by author(s)",n_pages)
                else:
                    # Insert title and summary to out_box.
                    insert_outbox_article(title, summary, "",n_pages)
        # If an uploading file is a txt file,
        if is_txt(fname):
            # convert the file to a string.
            text = ftext2text(fname)
            # Call function paper2out(text) to process the string
            nsa, a, c, summary= paper2out(text)
            # If a is not an empty string
            # and the desired number of summary's sentences less than number sentences in a.
            if a != "" and num_sents("")< nsa:
                insert_outbox_article('', a, " by author(s)")
                out_box.insert(END, "\nUser:", 'tag1')
            else:
                insert_outbox_article('', summary, None,None)


# 3.13 This function inserts an article's summary  to the out_box.
# Parameter: of an uploading document, summary of the document, a string "by author(s)".
# Return: none
def insert_outbox_article(title, summary, aut, n):
    global m
    out_box.insert(END, "\nSystem: ", 'tag2')
    out_box.insert(END, f"Summary of the uploaded {n}-page document ", 'tag4')
    out_box.insert(END, f"'{title}'", 'tag5')
    out_box.insert(END, f" {aut}:\n", 'tag4')
    out_box.insert(END, summary)
    out_box.insert(END, "\n\nSystem: Please enter a desired number summary sentences and hit 'Return' key!", 'tag2')
    out_box.insert(END, "\nUser:", 'tag1')
    out_box.see(END)
    m = 0


# 3.15 This function gets n sentences from a long document by a graph based algorithm.
# Parameters: text,the number sentences of an output summary,the number keywords of an output.
# Return: summary, keywords
def get_n_sents(text, nsent):
    # ab, c, text = clean_text(text)
    sents = get_summary(text=text, ranker=nx.degree_centrality, M=nsent)
    # print(sents)
    summary = ""
    #  "sents" is a list of tuples, each tuple is a pair of sentence's id and sentence's text.
    for sent in sents:
        # Extract only the sentence's text from each tuple and convert the tuple to string.
        s = str(sent[1])
        summary += " " + s[0].upper() + s[1:]
        summary = summary.replace('1 Introduction', ' ')
        summary = summary.replace('  ',' ')
    return summary


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
    # print(f"text after remove reference {text}")
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
    # Remove the lines with a lot numbers which often come from tables.
    text = re.sub('\n?[\w\s-]*(\s*?[\d]+[.][\d]+-?)+', ' ', text)
    # Replace '..' by '.'.
    text = re.sub('\.\.', '.', text)
    # Call a function get_Conclusion(text) to get a conclusion.
    c = get_Conclusion(text)
    # l = text.split('\n')
    # # print(l)
    # for i in l:
    #     # print(f"i  :{i}")
    #     # print(f"i type :{type(i)}")
    #     if len(i)< 20: l.remove(i)
    #
    # for i in l: print(f"i: {i}")
    # t = ""
    # for c in l:
    #     t+= c+' '
    # print(f" t: {t}")
    # Replace all newlines by ' '.
    text = re.sub('\n', ' ', text)
    return ab, c, text


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
        # print(f" text no author : {text_no_author}")
        # Split the text into 2 parts by the key word 'Introduction' or 'INTRODUCTION',
        # Get the first part which is abstract
        if len(intr) > 0:
            abstract1 = text_no_author.split(str(intr[0]), 1)[0]
            abstract1 = re.sub('\n1\.?', '', abstract1)
            abstract1 = re.sub('\n', ' ', abstract1)
            # print(f" abstract1: {abstract1}")
            # for i in range(len(intr)): text_no_author = text_no_author.split(str(intr[-1]), 1)[1]
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
    print(f"outline: {outline}")
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
    # print(f"text : {text}")
    # Use nltk sent_tokenize to get number sentences of a.
    sents = nltk.tokenize.sent_tokenize(a)
    nsa = len(sents)
    a = ""
    for s in sents:
        if ("University" or "Author" or "@") not in s: a += s
    sum = get_n_sents(body_text, num_sents(""))
    summary = sum
    return nsa, a, c, summary


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


# 3.33 This function counts the current words in a textbox.
# Parameter: textbox.
# Return : number of words.
def count_words(box):
    return len(box.get("1.0", END).split(" "))

def clear():
    global m
    out_box.delete("1.0", END)
    out_box.insert(END, "System: Please enter a desired number summary sentences and hit 'Return' key!", 'tag2')
    out_box.insert(END, "\nUser:", 'tag1')
    m = 0

def save2file(out_box):
    try:
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text files", "*.txt")])
        text = out_box.get("1.0", "end-1c")
        with open(file_path, 'w') as file:
            file.write(text)
    except:
        OSError
        pass



### 3.Call the function to create a withow with the specific title, color, and size
window = create_window("Offline Summary Tool", 'green4', 1086, 718)


### 5.Create a textbox  which contains the output text
# width = 780, height = 208,x=60, y=80,wchar=97, hchar=8
out_box = scroll_text(998, 688, 26, 22, 127, 41)
out_box.insert(END,"Hi! How are you today! I am Tam's reader assistant! I will help you save time, energy and money by summarizing  documents for \nyou without internet connection and no fee :)")
out_box.insert(END, "\nSystem: Please enter a desired number summary sentences and hit 'Return' key!", 'tag2')
out_box.insert(END,"\nUser:",'tag1')

out_box.tag_config('tag1', foreground='red',font=('Arial', 10,"bold"))
out_box.tag_config('tag2', foreground='green',font=('Arial', 10,"bold"))
out_box.tag_config('tag3', foreground='purple4',font=('Arial', 10,"italic"))
out_box.tag_config('tag4', foreground='forest green',font=('Arial', 10,"italic"))
out_box.tag_config('tag5', foreground='brown4', font=('Arial', 10, "italic"))
out_box.bind('<Return>', num_sents)

### 8. Create a button which a user clicks to upload a file
buttonM = Button(window, bg="green", text="Upload a File", font=('Arial', 10, "bold"),
                 width=30, height=1, anchor=CENTER, highlightthickness=1,
                 command=lambda: get_textFfile(out_box))
# Place a button in a correct position
buttonM.place(x=420, y=686)

###9. Create a button which a user clicks to clear the screen
buttonR = Button(window, bg="green", text="Clear", font=('Arial', 10, "bold"),
                 width=30, height=1, anchor=CENTER, highlightthickness=1,
                 command=lambda: clear())
# Place a button in a correct position
buttonR.place(x=50, y=686)

#10
buttonL = Button(window, bg="green", text="Save", font=('Arial', 10, "bold"),
                 width=30, height=1, anchor=CENTER, highlightthickness=1,
                 command=lambda: save2file(out_box))
# Place a button in a correct position
buttonL.place(x=780, y=686)

window.mainloop()