# a better version from https://github.com/ptarau
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import WordNetLemmatizer
import networkx as nx

def stopwords():
    with open('stopwords.txt', 'r') as f:
        return set(l[:-1] for l in f.readlines())


def text2sents(text):
    lemmatizer = WordNetLemmatizer()
    stops = stopwords()
    # print(f" stopwords: {stops}")
    sents = sent_tokenize(text)
    lss = []
    for sent in sents:
        ws = word_tokenize(sent)
        ls = []
        for w in ws:
            lemma = lemmatizer.lemmatize(w)
            if lemma not in stops and lemma not in [',','.','!','?','@','#','$','%','&','*','^','+','-','/','|','~']:
                ls.append(lemma)
        if not ls: continue
        lss.append((ls, sent))
    return lss


def sents2graph(lss):
    g = nx.DiGraph()
    g.add_edge(0, len(lss) - 1)  # first ot last sent
    for sent_id, (ls, _) in enumerate(lss):
        if sent_id > 0:  # from sent to sent before it
            g.add_edge(sent_id, sent_id - 1)
        g.add_edge(ls[0], sent_id)  # from 1-st word to sent id
        g.add_edge(sent_id, ls[-1])  # from sent id to last word
        # g.add_edge(ls[0], ls[-1]) # from first word to last word
        for j, w in enumerate(ls):
            if j > 0: g.add_edge(w, ls[j - 1])
    return g


def textstar(g, ranker, sumsize, kwsize, trim):
    while True:
        gbak = g.copy()
        # print(gbak)
        unsorted_ranks = ranker(g)
        ranks = sorted(unsorted_ranks.items(), reverse=True, key=lambda x: x[1])
        total = len(ranks)
        split = trim * total // 100
        # print(ranks)
        weak_nodes = [n for (n, _) in ranks[split:]]
        weakest = weak_nodes[-1]
        weakest_rank = unsorted_ranks[weakest]
        for n in weak_nodes:
            g.remove_node(n)
        for n,r in ranks[0:split]:
            if r <= weakest_rank:
                g.remove_node(n)
        s_nodes = len([n for n in g.nodes if isinstance(n, int)])
        w_nodes = g.number_of_nodes() - s_nodes
        # print('=> S_NODES:', s_nodes, 'W_NODES',w_nodes)
        if s_nodes <= sumsize: break
        if w_nodes <= kwsize: break
    return gbak, ranks


def process_text(text, ranker = nx.betweenness_centrality, sumsize = 5, kwsize = 7, trim = 80):
    lss = text2sents(text)
    # print(len(lss))
    # print( f" lss : {lss}")
    g = sents2graph(lss)
    # print(g)
    # for f,t in g.edges(): print(t,'<-',f)
    g, ranks = textstar(g, ranker, sumsize, kwsize, trim)
    sids = sorted([sid for (sid, _) in ranks if isinstance(sid,int)])
    sids = sids[0:sumsize]
    # print("SIDS:",sids)
    all_sents = [sent for (_, sent) in lss]
    sents = [(i,all_sents[i]) for i in sids]
    kwds = [w for (w,_) in ranks if isinstance(w, str)][0:kwsize]
    # print(f" keyword from textstar: {kwds}")
    return sents, kwds



