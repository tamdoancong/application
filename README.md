According to  United Census Bureau https://www.census.gov/quickfacts/fact/table/US/HSD410221, until 2021, there are around 21 million American who have computer but unable to access to the internet at their home.
Boston Consulting Group https://www.bcg.com/publications/2021/digital-access-in-united-states-education and Education Week Research https://www.edweek.org/technology/most-students-now-have-home-internet-access-but//-what-about-the-ones-who-dont/2021/04 estimated 12 million of them are US students.
This category is extremely huger in the world.
This giant vulnerable group of people do not have an opportunity to access  internet Artificial Intelligence(AI)  apps based deep learning models like ChatGPT https://openai.com/blog/chatgpt , Google Bart https://ai.google/static/documents/google-about-bard.pdf ,etc or  local deep learning model which requires  the latest hardware (Central Processing Unit(CPU), Graphics Processing Unit(GPU)), the newest software(Compute Unified Device Architecture(CUDA)), big Random Access Memory(RAM), and computer skills.

However, deep learning models have dominated Natural Language Processing(NLP) nowadays.
Especially, after ChatGPT appeared and blew a new wind to NLP research and industry, Large Language Models(LLMs) quickly become a new attractive trend, rapidly growth up investment research and solid established future area.
Although GPT4 https://openai.com/gpt-4 is currently the state of the art (SOTA) in the field, many big tech companies have invested a huge money and time to create a new LLMs to compete with GPT 4 , for example Google Bart ,LLaMa https://ai.meta.com/blog/large-language-model-llama-meta-ai/ ,Ernie Bot https://www.technologyreview.com/2023/03/22/1070154/baidu-ernie-bot-chatgpt-reputation/ , Grok https://grok.x.ai/,etc.
These fantastic models need billions dollars to build, train, tune, deliver, and maintain  in a big clouding center and require a giant amount of data for pre-training process which takes from months to years.
Despite that, these models have a limited input token.

In other hand, graph based models without restrict number of input token do not need training process or  running in supper computer.
However, the performance of graph based method is usually lower  far away from  deep learning approaches SOTA.

We propose a local, non training, small size and real time   open source summarization system .
A significant part of the system is a novel fast graph based algorithm which connects lemmas and sentence identifiers to build a text graph.
The algorithm  ranks, extracts, and returns  the salient sentences in the order in which they occur in the text .
The other important components are local tools which convert, extract, and clean page's text, chapter's text, or text from a PDF document before feeding to the summarizer.
Our system outperforms several deep learning models but it just needs maximum 200MB memory and 158 MB of disk, so it  can run in any computer.
Thus, people who have a computer even though it is 10 years old can use this app to experience and get benefit from AI.
This is only a summary app, but deeply it supports equal deployment AI and social good.

# TextRings Local Desktop AI summary app(Version 1.0.0 for Window OS) : Local app! This version only needs 180 MB free space and maximum 200 MB of memory.The app can summarize long documents without word or token limit (ex: 800 pages) A user just needs download a single .exe file. This app can run anywhere and anytime with a working computer! This app was built for users who do not have budget for the internet at home or do not want push their documents to the cloud or who  have good finance to access fantastic LLMs app but travel to somewhere without internet connection or cloud system in busy period time . In the future this app will be considered to deliver by CDs or USB!

## Users can download a single .exe file (an end user version just double clicks for use after finishing download ) from my Google Drive link:

https://drive.google.com/drive/folders/1KM0cd_-hSne6g7nYFDdjVWWGPS4Ln6dS

 or  click on my GitHub link below to get the detailed instructions how to download and use this version:

https://github.com/tamdoancong/offline_summary_app_158MB/tree/main

Below  is the link of the DEMO  which provides detailed instructions how to use this version:  

https://www.youtube.com/watch?v=zv9dOiXoFjA

## Developers:

1.Download my python version TextRings_offline_summary.py 
2. Install dependency libraries in requirements.txt :



# Combined API and offline summary AI app (Version 1.1.0 Window OS,158 MB) : In this version, the app can summarize long documents  (ex: 800 pages) both  in 'Local mode' (producing reasonable result) or in 'API mode' (generating fantastic result).

## Users can download directly a single .exe file from my Google Drive link:

https://drive.google.com/drive/folders/13SjO0TstLB_zpbSRAEthI-sGyyuXpw3P

or  click on my GitHub link below to get the detailed instructions how to download and use this version:

https://github.com/tamdoancong/API_offline_summary_app

## Developers:
1.Download one or all my python versions (offline_APImultiplerequest.py, offline_API_summary_keywords.py) and builder1.py.
2. Install dependency libraries in requirements.txt for offline mode.
3. Install  an extra packet for API mode:
    openai==0.27.8
    


`