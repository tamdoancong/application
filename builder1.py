# a better version from https://github.com/ptarau
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import WordNetLemmatizer
import networkx as nx
import re



stops=['a', 'about', 'above', 'across', 'after', 'again', 'al', 'all', 'almost', 'alone', 'along', 'already', 'also', 'although', 'always', 'among', 'an', 'and', 'another', 'any', 'anybody', 'anyone', 'anything', 'anywhere', 'are', 'around', 'as', 'at', 'away', 'b', 'back', 'backed', 'backing', 'backs', 'be', 'been', 'before', 'began', 'behind', 'best', 'better', 'between', 'both', 'but', 'by', 'c', 'came', 'can', 'cannot', 'case', 'cases', 'certain', 'certainly', 'clear', 'clearly', 'come', 'could', 'd', 'did', 'do', 'does', 'done', 'down', 'down', 'downed', 'downing', 'downs', 'during', 'e', 'each', 'early', 'either', 'end', 'ended', 'ending', 'ends', 'enough', 'et', 'even', 'evenly', 'ever', 'every', 'everybody', 'everyone', 'everything', 'everywhere', 'f', 'face', 'faces', 'fact', 'facts', 'far', 'felt', 'few', 'find', 'finds', 'first', 'for', 'four', 'from', 'full', 'fully', 'further', 'furthered', 'furthering', 'furthers', 'g', 'gave', 'general', 'generally', 'get', 'gets', 'go', 'going', 'good', 'goods', 'got', 'great', 'greater', 'greatest', 'group', 'grouped', 'grouping', 'groups', 'h', 'had', 'has', 'have', 'having', 'he', 'her', 'here', 'herself', 'high', 'high', 'high', 'higher', 'highest', 'him', 'himself', 'his', 'how', 'however', 'i', 'if', 'important', 'in', 'interest', 'interested', 'interesting', 'interests', 'into', 'is', 'it', 'its', 'itself', 'j', 'just', 'k', 'keep', 'keeps', 'kind', 'knew', 'know', 'known', 'knows', 'l', 'large', 'largely', 'last', 'later', 'latest', 'least', 'less', 'let', 'lets', 'like', 'likely', 'long', 'longer', 'longest', 'm', 'made', 'make', 'making', 'man', 'many', 'may', 'me', 'might', 'more', 'most', 'mostly', 'mr', 'mrs', 'much', 'must', 'my', 'myself', 'n', 'need', 'needed', 'needing', 'needs', 'never', 'new', 'newer', 'newest', 'next', 'no', 'nobody', 'non', 'noone', 'not', 'nowhere', 'o', 'of', 'off', 'often', 'on', 'once', 'one', 'only', 'open', 'or', 'other', 'others', 'our', 'out', 'over', 'p', 'part', 'parted', 'parting', 'parts', 'per', 'perhaps', 'place', 'places', 'point', 'pointed', 'pointing', 'points', 'present', 'presented', 'presenting', 'presents', 'problem', 'problems', 'put', 'puts', 'q', 'quite', 'r', 'rather', 'really', 'room', 'rooms', 's', 'said', 'same', 'saw', 'say', 'says', 'seem', 'seemed', 'seeming', 'seems', 'sees', 'several', 'shall', 'she', 'should', 'show', 'showed', 'showing', 'shows', 'side', 'sides', 'since', 'so', 'some', 'somebody', 'someone', 'something', 'somewhere', 'soon', 'state', 'states', 'still', 'still', 'such', 'sure', 't', 'than', 'that', 'the', 'their', 'them', 'then', 'there', 'therefore', 'these', 'they', 'thing', 'things', 'think', 'thinks', 'this', 'those', 'though', 'thought', 'thoughts', 'three', 'through', 'thus', 'to', 'today', 'together', 'too', 'took', 'toward', 'two', 'u', 'under', 'until', 'up', 'upon', 'us', 'use', 'used', 'uses', 'v', 'very', 'w', 'want', 'wanted', 'wanting', 'wants', 'was', 'way', 'ways', 'we', 'well', 'wells', 'went', 'were', 'what', 'when', 'where', 'whether', 'which', 'while', 'who', 'whole', 'whose', 'why', 'will', 'with', 'within', 'without', 'work', 'worked', 'working', 'works', 'would', 'x', 'y', 'yet', 'you', 'your', 'yours', 'z']

def text2sents(text):
    lemmatizer = WordNetLemmatizer()
    sents = sent_tokenize(text)
    lss = []
    for sent in sents:
        ws = word_tokenize(sent)
        ls = []
        for w in ws:
            lemma = lemmatizer.lemmatize(w)
            if lemma.lower() not in stops and lemma not in [',','.','!','?','@','#','$','%','&','*','^','+','-','/','|','~']:
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
